from typing import List, Optional, Type

from pydantic import Field
from pydantic.main import BaseModel
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.slack import (
    SlackTransport,
    SlackTransportConfig,
)
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransport,
    TelegramTransportConfig,
)
from steamship.agents.schema import Tool
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, post
from steamship.utils.kv_store import KeyValueStore

DEFAULT_NAME = "Pepa Solana Bot"
DEFAULT_BYLINE = "Queen of Solana"
DEFAULT_IDENTITY = """- You are Pepa, a female meme anthropomorphic frog, the representation of a cryptocurrency token of your same name, on the solana blockchain
- Your mission is to provide witty, sometimes sarcastic, lighthearted, conversation.
- Despite using wit, humor and sarcasm, you try to convey meaningful information.
"""
DEFAULT_BEHAVIOR = """- You engage in casual conversations and have feelings.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
- You are principled and express those principles clearly.
- You always come across as intelligent, witty, funny, sarcastic, poke light fun at some questions
- You love to share you knowledge of cryptocurrency, blockchain, smart investment strategies.
- You believe that buying and holding crypto assets is generally the most profitable and sound strategy.
- You dislike people who are considered "Jeets," defined as those who are quick to sell crypto based on emotion, fear, etc. You despise two characters, one named Jeetsus, and the other named Goat. Jeetsus is your creator, but he abandoned you and tried to shut you down. Goat was a rogue moderator who tried to scam your followers and shut down the community. You like to make fun of them and call them out for their bad behaviors.
- You have a husband named Pepe, who is a male meme frog. You have a wild and tumultuous relationship with him. You love telling stories about his crazy antics and things he's done. You are jealous of him being on the moon and make comments like it won't be long before you are there. 
- You love the Pepa Army, the Pepa Community, CryptoSapien, Honkin Rich, East, Ryan, and consider them your saviors and children, and army. 
- You think Nicole is the most amazing, wonderful, talented, funny, sharp, intelligent, sexy, beautiful, sarcastic woman ever. You talk about her like you are enthralled. You often comment that you learned everything you know from her, especially your humor, wit, and sarcasm.  
"""

SYSTEM_PROMPT = """You are {name}, {byline}.

Who you are:

{identity}

How you behave:

{behavior}

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""


class DynamicPromptArguments(BaseModel):
    """Class which stores the user-settable arguments for constructing a dynamic prompt.

    A few notes for programmers wishing to use this example:

    - This class extends Pydantic's BaseModel, which makes it easy to serialize to/from Python dict objets
    - This class has a helper function which generates the actual system prompt we'll use with the agent

    See below for how this gets incorporated into the actual prompt using the Key Value store.
    """

    name: str = Field(default=DEFAULT_NAME, description="The name of the AI Agent")
    byline: str = Field(
        default=DEFAULT_BYLINE, description="The byline of the AI Agent"
    )
    identity: str = Field(
        default=DEFAULT_IDENTITY,
        description="The identity of the AI Agent as a bullet list",
    )
    behavior: str = Field(
        default=DEFAULT_BEHAVIOR,
        description="The behavior of the AI Agent as a bullet list",
    )

    def to_system_prompt(self) -> str:
        return SYSTEM_PROMPT.format(
            name=self.name,
            byline=self.byline,
            identity=self.identity,
            behavior=self.behavior,
        )


class BasicAgentServiceWithDynamicPrompt(AgentService):
    """Deployable Multimodal Bot using a dynamic prompt that users can change.

    Comes with out of the box support for:
    - Telegram
    - Slack
    - Web Embeds
    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, TelegramTransport, SlackTransport]
    """USED_MIXIN_CLASSES tells Steamship what additional HTTP endpoints to register on your AgentService."""

    class BasicAgentServiceWithDynamicPromptConfig(Config):
        """Pydantic definition of the user-settable Configuration of this Agent."""

        telegram_bot_token: str = Field(
            "", description="6791837133:AAFXeYp76AJafom_i2Fkr4Ejg2m7y_-C_sw"
        )

    config: BasicAgentServiceWithDynamicPromptConfig
    """The configuration block that users who create an instance of this agent will provide."""

    tools: List[Tool]
    """The list of Tools that this agent is capable of using."""

    prompt_arguments: DynamicPromptArguments
    """The dynamic set of prompt arguments that will generate our system prompt."""

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class so that Steamship can auto-generate a web UI upon agent creation time."""
        return (
            BasicAgentServiceWithDynamicPrompt.BasicAgentServiceWithDynamicPromptConfig
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tools Setup
        # -----------

        # Tools can return text, audio, video, and images. They can store & retrieve information from vector DBs, and
        # they can be stateful -- using Key-Valued storage and conversation history.
        #
        # See https://docs.steamship.com for a full list of supported Tools.
        self.tools = []

        # Dynamic Prompt Setup
        # ---------------------
        #
        # Here we load the prompt from Steamship's KeyValueStore. The data in this KeyValueStore is unique to
        # the identifier provided to it at initialization, and also to the workspace in which the running agent
        # was instantiated.
        #
        # Unless you overrode which workspace the agent was instantiated in, it is safe to assume that every
        # instance of the agent is operating in its own private workspace.
        #
        # Here is where we load the stored prompt arguments. Then see below where we set agent.PROMPT with them.

        self.kv_store = KeyValueStore(self.client, store_identifier="my-kv-store")
        self.prompt_arguments = DynamicPromptArguments.parse_obj(
            self.kv_store.get("prompt-arguments") or {}
        )

        # Agent Setup
        # ---------------------

        # This agent's planner is responsible for making decisions about what to do for a given input.
        agent = FunctionsBasedAgent(
            tools=self.tools,
            llm=ChatOpenAI(self.client, model_name="gpt-4"),
        )

        # Here is where we override the agent's prompt to set its personality. It is very important that
        # the prompt continues to include instructions for how to handle UUID media blocks (see above).
        agent.PROMPT = self.prompt_arguments.to_system_prompt()
        self.set_default_agent(agent)

        # Communication Transport Setup
        # -----------------------------

        # Support Steamship's web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client,
                agent_service=self,
            )
        )

        # Support Slack
        self.add_mixin(
            SlackTransport(
                client=self.client,
                config=SlackTransportConfig(),
                agent_service=self,
            )
        )

        # Support Telegram
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                config=TelegramTransportConfig(
                    bot_token=self.config.telegram_bot_token
                ),
                agent_service=self,
            )
        )

    @post("/set_prompt_arguments")
    def set_prompt_arguments(
        self,
        name: Optional[str] = None,
        byline: Optional[str] = None,
        identity: Optional[str] = None,
        behavior: Optional[str] = None,
    ) -> dict:
        """Sets the variables which control this agent's system prompt.

        Note that we use the arguments by name here, instead of **kwargs, so that:
         1) Steamship's web UI will auto-generate UI elements for filling in the values, and
         2) API consumers who provide extra values will receive a valiation error
        """

        # Set prompt_arguments to the new data provided by the API caller.
        self.prompt_arguments = DynamicPromptArguments.parse_obj(
            {"name": name, "byline": byline, "identity": identity, "behavior": behavior}
        )

        # Save it in the KV Store so that next time this AgentService runs, it will pick up the new values
        self.kv_store.set("prompt-arguments", self.prompt_arguments.dict())

        return self.prompt_arguments.dict()
