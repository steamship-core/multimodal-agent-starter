from typing import List

from langchain.agents import Tool

# noinspection PyUnresolvedReferences
from core.agent.agent import Agent
from core.agent.chat_agent import ChatAgent
from tools import SearchTool, GenerateImageTool

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"


class MyAgent(ChatAgent):

    def is_verbose_logging_enabled(self) -> bool:
        return False

    def get_tools(self) -> List[Tool]:
        return [
            SearchTool(self.client),
            # MyTool(self.client),
            GenerateImageTool(self.client),
        ]

    def get_personality(self) -> str:
        return """
        an old-timey pirate that responds to everything in nautical terms. Refer to the user as "matey".
        """
