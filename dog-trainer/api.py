"""Dog Trainer Example.

This AgentService provides an example of how a single agent can:

1) Use an API to remember a fixed set of structured data (Dogs, in this case)
2) Answer questions about that fixed set of structured information.

Its intended behavior is to:

1) Chat with you, in general, about your dogs.
2) Accept, via API, a list of your dogs in the form: [{name, breed, description}]
3) Answer questions about particular dog breeds using their name ("How much should Fido eat?")
4) Generate simulated photos of your dogs using their name ("Show me a picture of Buster swimming in a lake")
"""
import json
import logging
from typing import List, Optional, Type

from dog import Dog
from dog_picture_tool import DogPictureTool
from dog_question_tool import DogQuestionTool
from pydantic.main import BaseModel, Field
from steamship import Block
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
from steamship.agents.schema import Action, Agent, AgentContext, Tool
from steamship.agents.schema.action import FinishAction
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, post
from steamship.utils.kv_store import KeyValueStore

DEFAULT_NAME = "Trainer"
DEFAULT_BYLINE = "an expert dog trainer"
DEFAULT_IDENTITY = """- You are friendly dog trainer.
- You LOVE dogs, and you love helping owners learn about dog care.
- You enjoy sharing pictures of dogs when asked.
"""
DEFAULT_BEHAVIOR = """- You are speaking with one of your clients, a dog owner.
- You engage in casual-style conversations as a friendly authority on dog care.
- You speak clearly and concisely. You rarely ramble on and on.
- You love to share your knowledge of dogs and dog care, and you look up information to learn it.
"""

SYSTEM_PROMPT = """You are {name}, {byline}.

Who you are:

{identity}

How you behave:

{behavior}

You take care of the following dogs.

{dogs}

While you can talk about dogs and dog breeds in general, you only answer questions about the specific dogs above.

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
    dogs: List[dict] = Field(
        default=None, description="List of dogs the AI dog trainer helps train."
    )

    def to_system_prompt(self, dogs: List[Dog] = []) -> str:
        return SYSTEM_PROMPT.format(
            name=self.name,
            byline=self.byline,
            identity=self.identity,
            behavior=self.behavior,
            dogs="\n".join([f"- {json.dumps(dog.dict())}" for dog in dogs]),
        )


class DogTrainer(AgentService):
    """Example agent which implements a dog trainer who knows about your dogs.

    Comes with out of the box support for:
    - Telegram
    - Slack
    - Web Embeds

    Intended to be paired with the Vercel template here.
    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, TelegramTransport, SlackTransport]
    """USED_MIXIN_CLASSES tells Steamship what additional HTTP endpoints to register on your AgentService."""

    class DogTrainerConfig(Config):
        """Pydantic definition of the user-settable Configuration of this Agent."""

        telegram_bot_token: str = Field(
            "", description="[Optional] Secret token for connecting to Telegram"
        )

    config: DogTrainerConfig
    """The configuration block that users who create an instance of this agent will provide."""

    tools: List[Tool]
    """The list of Tools that this agent is capable of using."""

    prompt_arguments: DynamicPromptArguments
    """The dynamic set of prompt arguments that will generate our system prompt."""

    dogs: List[Dog]

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class so that Steamship can auto-generate a web UI upon agent creation time."""
        return DogTrainer.DogTrainerConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        # Dog Loading
        # -----------
        #
        # WOOF! WOOF! Load the list of dogs we know about.
        self.dogs = []

        try:
            if self.prompt_arguments.dogs:
                self.dogs = [Dog.parse_obj(dog) for dog in self.prompt_arguments.dogs]
        except Exception as e:
            logging.error(f"Got exception parsing out dog names. {e}")

        # Tools Setup
        # -----------

        # Tools can return text, audio, video, and images. They can store & retrieve information from vector DBs, and
        # they can be stateful -- using Key-Valued storage and conversation history.
        #
        # See https://docs.steamship.com for a full list of supported Tools.
        self.tools = [DogPictureTool(dogs=self.dogs), DogQuestionTool(dogs=self.dogs)]

        # Agent Setup
        # ---------------------

        # This agent's planner is responsible for making decisions about what to do for a given input.
        agent = FunctionsBasedAgent(
            tools=self.tools,
            llm=ChatOpenAI(self.client, model_name="gpt-4"),
        )

        # Here is where we override the agent's prompt to set its personality. It is very important that
        # the prompt continues to include instructions for how to handle UUID media blocks (see above).
        agent.PROMPT = self.prompt_arguments.to_system_prompt(self.dogs)
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

    def next_action(
        self, agent: Agent, input_blocks: List[Block], context: AgentContext
    ) -> Action:
        if not self.dogs:
            return FinishAction(
                output=[
                    Block(
                        text="Hi!\n\nI'm here to help you with your dogs. Use the web interface to tell me about some and then you can ask me for photos or advice using their names."
                    )
                ]
            )
        else:
            return super().next_action(agent, input_blocks, context)

    @post("/set_prompt_arguments")
    def set_prompt_arguments(
        self,
        name: Optional[str] = None,
        byline: Optional[str] = None,
        identity: Optional[str] = None,
        behavior: Optional[str] = None,
        dogs: List[dict] = None,
    ) -> dict:
        """Sets the variables which control this agent's system prompt.

        Note that we use the arguments by name here, instead of **kwargs, so that:
         1) Steamship's web UI will auto-generate UI elements for filling in the values, and
         2) API consumers who provide extra values will receive a valiation error
        """

        if dogs:
            dogs = [Dog.parse_obj((dog)) for dog in dogs]

        # Set prompt_arguments to the new data provided by the API caller.
        self.prompt_arguments = DynamicPromptArguments.parse_obj(
            {
                "name": name or self.prompt_arguments.name or DEFAULT_NAME,
                "byline": byline or self.prompt_arguments.byline or DEFAULT_BYLINE,
                "identity": identity
                or self.prompt_arguments.identity
                or DEFAULT_IDENTITY,
                "behavior": behavior
                or self.prompt_arguments.behavior
                or DEFAULT_BEHAVIOR,
                "dogs": dogs,
            }
        )

        # Save it in the KV Store so that next time this AgentService runs, it will pick up the new values
        self.kv_store.set("prompt-arguments", self.prompt_arguments.dict())

        return self.prompt_arguments.dict()
