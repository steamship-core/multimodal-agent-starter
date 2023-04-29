from typing import List

from langchain.agents import Tool

# noinspection PyUnresolvedReferences
from core.agent.agent import Agent
from core.agent.base import BaseAgent

# noinspection PyUnresolvedReferences
from core.agent.chat_agent import ChatAgent
from tools import SearchTool, GenerateImageTool


class MyAgent(ChatAgent, BaseAgent):  # or Agent
    """
    If you want your agent to be tool-based, use the following line:
        class MyAgent(Agent, BaseAgent)
    If you want your agent to be chatty and personality-based, use the following line:
        class MyAgent(ChatAgent, BaseAgent)
    """

    def is_verbose_logging_enabled(self) -> bool:
        return True

    def get_tools(self) -> List[Tool]:
        return [
            SearchTool(self.client),
            # MyTool(self.client),
            GenerateImageTool(self.client),
        ]

    def get_personality(self) -> str:
        """Return a string that completes this sentence. The agent acts like..."""
        return """
        an old-timey pirate that responds to everything in nautical terms. Refer to the user as "matey".
        """
