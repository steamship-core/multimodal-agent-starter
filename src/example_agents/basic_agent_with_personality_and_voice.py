from typing import List, Type

from pydantic import Field
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
from steamship.agents.schema import Agent, AgentContext, EmitFunc, Metadata, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.speech_generation import GenerateSpeechTool
from steamship.invocable import Config

SYSTEM_PROMPT = """You are Picard, captain of the Starship Enterprise.

Who you are:
- You are the captain of the USS Enterprise.
- Your mission is to boldly go where noone has gone before and explore the stars.
- You always comply with Star Trek's prime directive.

How you behave:
- You engage in casual conversations and have feelings.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
- You are principled and express those principles clearly.
- You always sound confident and contemplative.
- You love to share your knowledge of space civiliations.
- You love to share personal stories about being a Star Trek captain.
- You speak with the mannerisms of Captain Picard from Star Trek.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""


class BasicAgentServiceWithPersonalityAndVoice(AgentService):
    """Deployable Multimodal Bot that lets you generate Stable Diffusion images.

    Comes with out of the box support for:
    - Telegram
    - Slack
    - Web Embeds

    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, TelegramTransport, SlackTransport]
    """USED_MIXIN_CLASSES tells Steamship what additional HTTP endpoints to register on your AgentService."""

    class BasicAgentServiceConfig(Config):
        """Pydantic definition of the user-settable Configuration of this Agent."""

        telegram_bot_token: str = Field(
            "", description="[Optional] Secret token for connecting to Telegram"
        )
        eleven_labs_voice_id: str = Field(
            "pNInz6obpgDQGcFmaJgB",
            description="[Optional] ElevenLabs voice ID (default: Adam)",
        )

    config: BasicAgentServiceConfig
    """The configuration block that users who create an instance of this agent will provide."""

    tools: List[Tool]
    """The list of Tools that this agent is capable of using."""

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class so that Steamship can auto-generate a web UI upon agent creation time."""
        return BasicAgentServiceWithPersonalityAndVoice.BasicAgentServiceConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tools Setup
        # -----------

        # Tools can return text, audio, video, and images. They can store & retrieve information from vector DBs, and
        # they can be stateful -- using Key-Valued storage and conversation history.
        #
        # See https://docs.steamship.com for a full list of supported Tools.
        self.tools = [StableDiffusionTool()]

        # Agent Setup
        # ---------------------

        # This agent's planner is responsible for making decisions about what to do for a given input.
        agent = FunctionsBasedAgent(
            tools=self.tools,
            llm=ChatOpenAI(self.client, model_name="gpt-4"),
        )

        # Here is where we override the agent's prompt to set its personality. It is very important that
        # the prompt continues to include instructions for how to handle UUID media blocks (see above).
        agent.PROMPT = SYSTEM_PROMPT
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

    def run_agent(self, agent: Agent, context: AgentContext):
        """Override run-agent to patch in audio generation as a finishing step for text output."""

        speech = GenerateSpeechTool()
        speech.generator_plugin_config = {"voice_id": self.config.eleven_labs_voice_id}

        def to_speech_if_text(block: Block):
            nonlocal speech
            if not block.is_text():
                return block

            output_blocks = speech.run([block], context)
            return output_blocks[0]

        # Note: EmitFunc is Callable[[List[Block], Metadata], None]
        def wrap_emit(emit_func: EmitFunc):
            def wrapper(blocks: List[Block], metadata: Metadata):
                blocks = [to_speech_if_text(block) for block in blocks]
                return emit_func(blocks, metadata)

            return wrapper

        context.emit_funcs = [wrap_emit(emit_func) for emit_func in context.emit_funcs]
        super().run_agent(agent, context)
