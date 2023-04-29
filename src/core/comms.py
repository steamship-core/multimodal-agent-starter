"""Implements the input/output communication channels for the Agent."""
from typing import Optional, List

from steamship import Steamship, Block
from steamship.experimental.transports import TelegramTransport
from steamship.experimental.transports.chat import ChatMessage
from steamship.experimental.transports.steamship_widget import SteamshipWidgetTransport
import logging

class CommsChannels:
    """
    Intended usage:

    Inside the Agent __init__:

       self.comms = CommsChannels(..)

    Inside the Agent response function:

       obj = self.comms.[appropriate_version]_send(output)
       return obj


    """
    client: Steamship
    telegram_token: Optional[str]

    web_transport: SteamshipWidgetTransport
    telegram_transport: TelegramTransport
    has_done_runtime_init: bool

    def __init__(
        self,
        client: Steamship,
        telegram_token: Optional[str],
    ):
        self.client = client
        self.telegram_token = telegram_token
        self.has_done_runtime_init = False

    def runtime_init(self):
        """Called from within method invocation so that the Exception can be caught in a more convenient place."""
        self.web_transport = SteamshipWidgetTransport()
        try:
            self.telegram_transport = TelegramTransport(bot_token=self.telegram_token)
        except Exception as ex:
            logging.error(ex)
        self.has_done_runtime_init = True

    def telegram_info(self) -> dict:
        """Endpoint returning information about this bot."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        try:
            return self.telegram_transport.info()
        except Exception as ex:
            logging.error(ex)
            return {}

    def telegram_send(self, messages: List[ChatMessage]) -> List[dict]:
        """Send a list of responses to the Telegram user."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        if messages:
            logging.info(f"Sending messages to telegram: {messages}")
            self.telegram_transport.send(messages)
        return []

    def web_transport_send(self, messages: List[ChatMessage]) -> List[dict]:
        """Prepares a list of messages for the Web client."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        ret = []
        if messages:
            logging.info(f"Sending blocks to web client: {messages}")
            for message in messages:
                m = message.dict()
                m["who"] = "bot"
                ret.append(m)
        return ret
