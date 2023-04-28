import abc
from abc import ABC
from typing import List

from langchain import LLMChain
from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain.agents import Tool
from steamship.invocable import PackageService
from steamship_langchain import OpenAI

from src.parser import (
    FORMAT_INSTRUCTIONS_W_TOOLS,
    CustomParser,
    get_format_instructions,
)

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"
VERBOSE = True


class Agent(PackageService, ABC):
    @abc.abstractmethod
    def get_tools(self) -> List[Tool]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_personality(self) -> str:
        raise NotImplementedError()

    def get_prompt(self, tools):
        prefix = self.get_personality()
        suffix = """Question: {question}
    {agent_scratchpad}"""
        return ZeroShotAgent.create_prompt(
            tools,
            format_instructions=get_format_instructions(bool(tools)),
            prefix=prefix,
            suffix=suffix,
            input_variables=["question", "agent_scratchpad"],
        )

    def get_agent(self):
        llm = OpenAI(client=self.client, temperature=0)

        tools = self.get_tools()
        prompt = self.get_prompt(tools)
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(
            llm_chain=llm_chain, allowed_tools=tool_names, output_parser=CustomParser()
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=VERBOSE
        )

        return agent_executor

    def run(self, input: str) -> str:
        return self.get_agent().run(question=input)
