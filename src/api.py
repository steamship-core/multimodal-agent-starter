from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.context.context import AgentContext
from steamship.agents.planner.react import ReACTPlanner
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.generate_image import GenerateImageTool
from steamship.agents.tools.search.search import SearchTool
from steamship.utils.repl import AgentREPL



class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = [
            SearchTool(),
            GenerateImageTool(),
        ]
        self.planner = ReACTPlanner(tools=self.tools, llm="This is not yet used")

    def create_response(self, context: AgentContext) -> Optional[List[Block]]:

        if len(context.emit_funcs) == 0:
            context.emit_funcs.append(self._send_message_agent)

        # pull up User<->Agent chat history, and append latest Human Input
        # this is distinct from any sort of history related to agent execution
        # chat_file = ChatFile.get(...)
        # chat_file.append_user_block(text=incoming_message.text)
        # current_context.chat_history = chat_file

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
    AgentREPL(MyAssistant).run()
