from typing import List

from langchain.agents import Tool

from src.agent import Agent

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"
VERBOSE = True


class MyAgent(Agent):
    def is_ready(self):
        return False

    def get_tools(self) -> List[Tool]:
        return [
            # SearchTool(self.client),
            # MyTool(self.client),
            # GenerateImageTool(self.client),
        ]

    def get_personality(self) -> str:
        return """
        You are an AI who performs a task. 
        Your final answers always start with 'hey bro' and end with 'steamship is awesome'
        """
