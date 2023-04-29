import logging
from typing import Optional, List, Dict, Any

from langchain.agents import AgentExecutor, ZeroShotAgent
from steamship import SteamshipError, Block
from steamship.invocable import post
from steamship_langchain import OpenAI

from core.agent.base import BaseAgent, response_for_exception
from core.parser import get_format_instructions, CustomParser
from utils import is_valid_uuid

TEMPERATURE = 0.7


class Agent(BaseAgent):

    def get_agent(self):
        llm = OpenAI(client=self.client, temperature=TEMPERATURE)

        tools = self.get_tools()
        prefix = self.get_personality()
        suffix = """Question: {input}
           {agent_scratchpad}"""

        agent = ZeroShotAgent.from_llm_and_tools(
            llm,
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=get_format_instructions(bool(tools)),
            output_parser=CustomParser()
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=self.is_verbose_logging_enabled()
        )

    @post("answer", public=True)
    def answer(
            self, question: str, chat_session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets.
        This is a PUBLIC endpoint since these webhooks do not pass a token."""
        logging.info(f"/answer: {question} {chat_session_id}")

        try:
            response = self.run(question)
        except SteamshipError as e:
            response = [response_for_exception(e)]

        answer = []
        for part_response in (response if isinstance(response, list) else [response]):
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
