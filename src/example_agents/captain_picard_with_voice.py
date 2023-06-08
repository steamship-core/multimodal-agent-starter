import logging
import uuid
from typing import List

from steamship import Block, Task, SteamshipError
from steamship.agents.logging import AgentLogging
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.schema import (
    AgentContext,
    Metadata,
    Action,
    FinishAction,
    Agent,
    EmitFunc,
)
from steamship.agents.llms import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
from steamship.agents.tools.speech_generation.generate_speech import GenerateSpeechTool
from steamship.agents.utils import with_llm
from steamship.invocable import post
from steamship.utils.repl import AgentREPL

from utils import print_blocks

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

TOOLS:
------

You have access to the following tools:
{tool_index}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

Some Tools will return Observations in the format of `Block(<identifier>)`. `Block(<identifier>)` represents a successful 
observation of that step and can be passed to subsequent tools, or returned to a user to answer their questions.
`Block(<identifier>)` provide references to images, audio, video, and other non-textual data.

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your final response here]
```

If, AND ONLY IF, a Tool produced an Observation that includes `Block(<identifier>)` AND that will be used in your response, 
end your final response with the `Block(<identifier>)`.

Example:

```
Thought: Do I need to use a tool? Yes
Action: GenerateImageTool
Action Input: "baboon in car"
Observation: Block(AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAAA)
Thought: Do I need to use a tool? No
AI: Here's that image you requested: Block(AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAAA)
```

Make sure to use all observations to come up with your final response.

Begin!

New input: {input}
{scratchpad}"""


class StarTrekCaptainWithVoice(AgentService):
    """Deployable Multimodal Agent that illustrates a character personality with voice.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = ReACTAgent(
            tools=[
                StableDiffusionTool(),
            ],
            llm=OpenAI(self.client),
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
        context = with_llm(context=context, llm=OpenAI(client=self.client))

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
            block_text = "\n".join(
                [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
            )
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output


if __name__ == "__main__":
    AgentREPL(
        StarTrekCaptainWithVoice,
        method="prompt",
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
