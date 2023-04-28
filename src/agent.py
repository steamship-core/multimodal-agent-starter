import abc
from abc import ABC
from typing import List

from langchain.agents import AgentExecutor, ConversationalChatAgent, Tool
from langchain.agents.conversational_chat.prompt import PREFIX
from langchain.memory import ConversationBufferWindowMemory
from steamship.invocable import PackageService
from steamship_langchain.llms import OpenAIChat

from src.parser import  ChatCustomParser

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"


class Agent(PackageService, ABC):
    name: str = "MyAgent"

    @abc.abstractmethod
    def get_tools(self) -> List[Tool]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_personality(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def is_verbose_logging_enabled(self) -> bool:
        pass

    def get_agent(self):
        llm = OpenAIChat(client=self.client, temperature=TEMPERATURE, model_name=MODEL_NAME)

        sys_message = f"{PREFIX}\n Please take on the personality of {self.get_personality()}"

        tools = self.get_tools()
        memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
        )

        agent = ConversationalChatAgent.from_llm_and_tools(
            llm, tools,
            system_message=sys_message,
            output_parser=ChatCustomParser()
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=self.is_verbose_logging_enabled()
        )

    def run(self, prompt: str) -> str:
        return self.get_agent().run(input=prompt)
