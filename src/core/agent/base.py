from abc import ABC, abstractmethod
from typing import List, Optional

from langchain.agents import Tool
from steamship import Block
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage

from core.agent.utils import is_valid_uuid, _make_image_public


class BaseAgent(TelegramBot, ABC):
    name: str = "MyAgent"

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        raise NotImplementedError()

    @abstractmethod
    def get_personality(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def is_verbose_logging_enabled(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_agent(self):
        raise NotImplementedError()

    def create_response(
        self, incoming_message: ChatMessage
    ) -> Optional[List[ChatMessage]]:
        """Use the LLM to prepare the next response by appending the user input to the file and then generating."""

        chain_output = self.get_agent().run(input=incoming_message.text)
        output_messages = self.chain_output_to_chat_messages(
            incoming_message.get_chat_id(), chain_output
        )
        return output_messages

    def chain_output_to_chat_messages(
        self, chat_id: str, chain_output: List[str]
    ) -> List[ChatMessage]:
        """Transform the output of the Chain/Agent into a list of ChatMessage objects.

        A Chain/Agent returns a string or list of strings. The string contents contains a sneak-route for mime encoding:
        It is either:
        - A parseable UUID, representing a block containing binary data, or:
        - Text
        This method inspects each string and creates a block of the appropriate type.
        """
        ret = []
        for part_response in chain_output:
            if is_valid_uuid(part_response):
                block = Block.get(self.client, _id=part_response)
                message = ChatMessage.from_block(
                    block,
                    chat_id=chat_id,
                )
                message.url = _make_image_public(self.client, block)

            else:
                message = ChatMessage(
                    client=self.client,
                    chat_id=chat_id,
                    text=part_response,
                )

            ret.append(message)
        return ret
