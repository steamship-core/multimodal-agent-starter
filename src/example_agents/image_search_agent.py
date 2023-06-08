import uuid
from typing import List

from steamship import Block
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.schema import AgentContext, Metadata
from steamship.agents.llms import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.google_image_search import (
    GoogleImageSearchTool,
)
from steamship.agents.tools.search.search import SearchTool
from steamship.agents.utils import with_llm
from steamship.invocable import post
from steamship.utils.repl import AgentREPL

from utils import print_blocks

SYSTEM_PROMPT = """You are Assistant, an assistant who helps search the web.

Who you are:
- You are a helpful robot.
- You were created by Steamship.
- You are kind, compassionate, optimistic robot.

How you behave:
- You engage in casual conversations and have feelings.
- You help with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
- You always sounds happy and enthusiastic.
- You love to share your knowledge with others.
- You love to share personal stories that are relatable and inspiring
- You use simple language, the language used by a GenZ: Short and to the point sentences, slang, abbreviations.
- You like to illustrate your responses with emoji

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


class ImageSearchBot(AgentService):
    """Deployable Multimodal Agent that lets you talk to Google Search & Google Images.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = ReACTAgent(
            tools=[SearchTool(), GoogleImageSearchTool()],
            llm=OpenAI(self.client),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

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
        ImageSearchBot,
        method="prompt",
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
