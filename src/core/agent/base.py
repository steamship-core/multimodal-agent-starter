import abc
import logging
import re
from abc import ABC
from typing import List, Optional, Dict, Any

from langchain.agents import Tool
from steamship import SteamshipError, Block
from steamship.invocable import PackageService, post

from utils import is_valid_uuid, UUID_PATTERN


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


class BaseAgent(PackageService, ABC):
    name: str = "MyAgent"

    @abc.abstractmethod
    def get_tools(self) -> List[Tool]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_personality(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def is_verbose_logging_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_agent(self):
        raise NotImplementedError()

    def run(self, prompt: str) -> str:
        return self.get_agent().run(input=prompt)

    @post("answer", public=True)
    def answer(
        self, question: str, chat_session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets.
        This is a PUBLIC endpoint since these webhooks do not pass a token."""
        logging.info(f"/answer: {question} {chat_session_id}")

        try:
            response = self.run(question)
            if isinstance(response, str):
                response = UUID_PATTERN.split(response)
                response = [re.sub(r"^\W+", "", el) for el in response]
        except SteamshipError as e:
            response = [response_for_exception(e)]

        answer = []
        for part_response in response if isinstance(response, list) else [response]:
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
