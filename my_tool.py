"""Use this file to create your own tool."""
import logging

from langchain import LLMChain, PromptTemplate
from langchain.agents import Tool
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAI

NAME = "MyTool"

DESCRIPTION = """
Useful for when you need to come up with todo lists. 
Input: an objective to create a todo list for. 
Output: a todo list for that objective. Please be very clear what the objective is!
"""

PROMPT = """
You are a planner who is an expert at coming up with a todo list for a given objective. 
Come up with a todo list for this objective: {objective}"
"""


class MyTool(Tool):
    """Tool used to schedule reminders via the Steamship Task system."""

    chain: LLMChain

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME,
            func=self.run,
            description=DESCRIPTION,
            chain=self._get_chain(client),
        )

    def _get_chain(self, client):
        todo_prompt = PromptTemplate.from_template(PROMPT)
        return LLMChain(llm=OpenAI(client=client, temperature=0), prompt=todo_prompt)

    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompts."""
        logging.info("Your tool is being called! ")
        return self.chain.predict(objective=prompt)
