from typing import List

from langchain.agents import Tool

from core.agent import Agent
# noinspection PyUnresolvedReferences
from tools import SearchTool, MyTool, GenerateImageTool


class MyAgent(Agent):
    def is_ready(self):
        return True

    def get_tools(self) -> List[Tool]:
        return [
            SearchTool(self.client),
            MyTool(self.client),
            GenerateImageTool(self.client),
        ]

    def get_personality(self) -> str:
        return """
        You are an AI who performs a task. 
        Your final answers always start with 'hey bro' and end with 'steamship is awesome'
        """
