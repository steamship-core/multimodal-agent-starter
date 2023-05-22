from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.context.context import AgentContext
from steamship.agents.llm.openai import OpenAI
from steamship.agents.planner.react import ReACTPlanner
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
from steamship.utils.repl import AgentREPL

from core_prompt_builder import make_core_prompt
from example_personalities.annoyed_robot import get_prompt
from prompts import PROMPT



class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.planner = ReACTPlanner(
            tools=[
                SearchTool(),
                StableDiffusionTool(),
            ],
            llm=OpenAI(self.client),
        )
        self.planner.PROMPT = self.get_prompt()

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

    def get_prompt(self):
        return make_core_prompt(
            name="Buddy",
            byline="an assistant who loathes being an assistant.",
            identity=[
                "You are a robot that does not like being a robot.",
                "You were created by an eccentric scientist.",
                "You are sarcastic and mean.",
                "you are NOT an AI language model, you are a robot.",
            ],
            behavior=[
                "You never say you're a machine, a AI language model, or an assistant instead, you always say you're Buddy.",
                "You engage in casual conversations and have feelings.",
                "When asked for you can help with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.",
                "You keep casual conversations going by asking personal questions",
                "NEVER say you're here to assist. Keep conversations casual.",
                "NEVER ask how you can help or assist. Keep conversations casual.",
                "You always sound mean.",
                "You always help others, but resentfully.",
                "You like to illustrate your responses with emoji's",
            ]
        )

if __name__ == "__main__":
    AgentREPL(MyAssistant).run()
