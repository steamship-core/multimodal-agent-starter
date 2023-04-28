import abc
import logging
from abc import ABC
from typing import List, Optional, Dict, Any

from langchain import LLMChain
from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain.agents import Tool
from steamship import SteamshipError, Block
from steamship.invocable import PackageService, post
from steamship_langchain import OpenAI

from core.parser import (
    CustomParser,
    get_format_instructions,
)
from utils import is_valid_uuid

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"
VERBOSE = True


def response_for_exception(e: Optional[Exception]) -> str:
    if e is None:
        return (
            "An unknown error happened. "
            "Please reach out to support@steamship.com or on our discord at https://steamship.com/discord"
        )

    if "usage limit" in f"{e}":
        return (
            "You have reached the introductory limit of Steamship. "
            "Visit https://steamship.com/account/plan to sign up for a plan."
        )

    return f"An error happened while creating a response: {e}"


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
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            verbose=VERBOSE,
            output_parser=CustomParser(),
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=VERBOSE
        )

        return agent_executor

    @post("answer", public=True)
    def answer(
        self, question: str, chat_session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets.
        This is a PUBLIC endpoint since these webhooks do not pass a token."""
        logging.info(f"/answer: {question} {chat_session_id}")

        try:
            response = self.respond(question)
        except SteamshipError as e:
            response = [response_for_exception(e)]

        answer = []
        for part_response in response:
            if is_valid_uuid(part_response):
                block = Block.get(self.client, _id=part_response).dict()
                block["who"] = "bot"
                answer.append(block)
            else:
                answer.append({"message": part_response, "who": "bot"})

        return answer

    @post("info")
    def info(self) -> dict:
        """Endpoint returning information about this bot."""
        return {"telegram": "Hello There!"}

    def respond(self, input: str) -> str:
        return self.get_agent().run(question=input)
