from typing import List

from langchain.agents import Tool

# noinspection PyUnresolvedReferences
from core.agent.agent import Agent
from tools import SearchTool, GenerateImageTool


class MyAgent(Agent):  # or Agent

    def is_verbose_logging_enabled(self) -> bool:
        return True

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
