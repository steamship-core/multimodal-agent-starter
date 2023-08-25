from typing import List, Type

from pydantic import Field
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
from steamship.invocable import Config

from example_projects.prompt_golf.tools.game_start_tool import GameStartTool
from example_projects.prompt_golf.tools.modify_prompt_tool import ModifyPromptTool


class PromptGolfAgent(FunctionsBasedAgent):
    pass


class PromptGolfAgentService(AgentService):
    """Deployable Multimodal Bot that lets you generate Stable Diffusion images.

    Comes with out of the box support for:
    - Telegram
    - Slack
    - Web Embeds

    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, TelegramTransport, SlackTransport]
    """USED_MIXIN_CLASSES tells Steamship what additional HTTP endpoints to register on your AgentService."""

    class BasicAgentConfig(Config):
        """Pydantic definition of the user-settable Configuration of this Agent."""

        telegram_bot_token: str = Field(
            "", description="[Optional] Secret token for connecting to Telegram"
        )

    config: BasicAgentConfig
    """The configuration block that users who create an instance of this agent will provide."""

    tools: List[Tool]
    """The list of Tools that this agent is capable of using."""

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class so that Steamship can auto-generate a web UI upon agent creation time."""
        return PromptGolfAgentService.BasicAgentConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tools Setup
        # -----------

        # Tools can return text, audio, video, and images. They can store & retrieve information from vector DBs, and
        # they can be stateful -- using Key-Valued storage and conversation history.
        #
        # See https://docs.steamship.com for a full list of supported Tools.
        self.tools = [ModifyPromptTool(), GameStartTool()]

        # Agent Setup
        # ---------------------

        # This agent's planner is responsible for making decisions about what to do for a given input.
        self.set_default_agent(
            PromptGolfAgent(
                tools=self.tools,
                llm=ChatOpenAI(self.client, model_name="gpt-4"),
            )
        )

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
