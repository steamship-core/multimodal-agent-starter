from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.context.context import AgentContext
from steamship.agents.llm.openai import OpenAI
from steamship.agents.planner.react import ReACTPlanner
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.google_image_search import GoogleImageSearchTool
from steamship.agents.tools.search.search import SearchTool
from steamship.utils.repl import AgentREPL

from core_prompt_builder import make_core_prompt
from prompts import PROMPT

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

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your final response here which ALWAYS includes UUID of generated images]

Make sure to use all observations to come up with your final response. 
If an observation included a media UUID, ALWAYS copy it into the final response.
If an observation included a media UUID, ALWAYS come up with a final response along with an explanation.
If an observation did not include a media UUID, to not return a placeholder message.
```

Begin!


New input: {input}
{scratchpad}"""

class GoogleChatbot(AgentService):
    """Deployable Multimodal Agent that lets you talk to Google Search & Google Images.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # The agent's planner is responsible for making decisions about what to do for a given input.
        self.planner = ReACTPlanner(
            tools=[
                SearchTool(),
                GoogleImageSearchTool()
            ],
            llm=OpenAI(self.client),
        )
        self.planner.PROMPT = SYSTEM_PROMPT

    def create_response(self, context: AgentContext) -> Optional[List[Block]]:

        if len(context.emit_funcs) == 0:
            context.emit_funcs.append(self._send_message_agent)

        if len(context.chat_history.messages) == 0:
            context.chat_history.append_system_message()

        self.run_agent(context)

        # should we return any message to the user to indicate that a response?
        # maybe: "Working on it..." or "Received: {prompt}..."
        return []

    def _send_message_agent(self, blocks: List[Block], meta: Metadata):
        # should this be directly-referenced, or should this be an invoke() endpoint, with a value passed
        # in?

        print(f"\n\nTELEGRAM SENDING MESSAGES:\n{blocks}")
        # self.telegram_transport.send(messages)

if __name__ == "__main__":
    AgentREPL(GoogleChatbot, agent_package_config={'botToken':'not-a-real-token-for-local-testing'}).run()
