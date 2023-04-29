import abc
import logging
from abc import ABC
from typing import List, Optional, Dict, Any

from langchain.agents import Tool
from steamship import SteamshipError, Block
from steamship.invocable import PackageService, post

from utils import is_valid_uuid

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"


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