from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.context.context import AgentContext
from steamship.agents.llm.openai import OpenAI
from steamship.agents.planner.react import ReACTPlanner
from steamship.agents.service.agent_service import AgentService

from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
from steamship.experimental.package_starters.telegram_agent import TelegramAgentService
from steamship.utils.repl import AgentREPL

from core_prompt_builder import make_core_prompt


class MyAssistant(TelegramAgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.planner = ReACTPlanner(
            tools=[
                SearchTool(),
                StableDiffusionTool(),
            ],
            llm=OpenAI(self.client),
        )
        self.planner.PROMPT = self.get_personality()

    def get_personality(self):
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
    AgentREPL(MyAssistant, agent_package_config={'botToken':'not-a-real-token-for-local-testing'}).run()
