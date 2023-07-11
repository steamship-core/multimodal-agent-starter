import uuid
from typing import List

from steamship import Block
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms import OpenAI
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.schema import Agent, AgentContext, EmitFunc, Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.speech_generation.generate_speech import GenerateSpeechTool
from steamship.agents.utils import with_llm
from steamship.invocable import post
from steamship.utils.repl import AgentREPL

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


MODEL_NAME = "gpt-4"

class StarTrekCaptainWithVoice(AgentService):
    """Deployable Multimodal Agent that illustrates a character personality with voice.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._agent = FunctionsBasedAgent(
            tools=[StableDiffusionTool()],
            llm=ChatOpenAI(self.client, model_name=MODEL_NAME),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

    def run_agent(self, agent: Agent, context: AgentContext):
        """Override run-agent to patch in audio generation as a finishing step for text output."""

        speech = GenerateSpeechTool()
        speech.generator_plugin_config = {
            "voice_id": "pNInz6obpgDQGcFmaJgB"  # Adam on ElevenLabs
        }

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

    @post("prompt")
    def prompt(self, prompt: str) -> str:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)
        # Add the LLM
        context = with_llm(
            context=context, llm=OpenAI(client=self.client, model_name=MODEL_NAME)
        )

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output

            def block_text(block: Block) -> str:
                if isinstance(block, dict):
                    return f"{block}"
                if block.is_text():
                    return block.text
                elif block.url:
                    return block.url
                elif block.content_url:
                    return block.content_url
                else:
                    block.set_public_data(True)
                    return block.raw_data_url

            block_text = "\n".join([block_text(b) for b in blocks])
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output


if __name__ == "__main__":
    AgentREPL(
        StarTrekCaptainWithVoice,
        method="prompt",
        agent_package_config={},
    ).run()
