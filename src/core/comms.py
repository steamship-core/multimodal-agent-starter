"""Implements the input/output communication channels for the Agent."""
from typing import Optional, List, Union

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

       inbound_message = self.comms.XYZ_parse(**kwargs)
       outbound_result = generate_response(inbound_message)
       outbound_messages = self.comms.XYZ_send(output)
       return outbound_messages

    """

    client: Steamship
    telegram_token: Optional[str]

    web_transport: SteamshipWidgetTransport
    telegram_transport: TelegramTransport
    has_done_runtime_init: bool

    def __init__(
        self,
        client: Steamship,
        telegram_token: Optional[str] = None,
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

    def instance_init(self, telegram_endpoint: str):
        """This instance_init method should be called from PackageService.instance_init."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        try:
            # Register any required hooks.
            self.telegram_transport.instance_init(webhook_url=telegram_endpoint)
            self.web_transport.instance_init()
        except Exception as ex:
            logging.error(ex)

    def telegram_info(self) -> dict:
        """Endpoint returning information about this bot."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        try:
            return self.telegram_transport.info()
        except Exception as ex:
            logging.error(ex)
            return {}

    def telegram_parse(self, **kwargs) -> Optional[ChatMessage]:
        """Parses an inbound Telegram message."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        if not kwargs or "message" not in kwargs:
            return None
        return self.telegram_transport.parse_inbound(payload=kwargs["message"])

    def webtransport_parse(self, **kwargs) -> Optional[ChatMessage]:
        """Parses an inbound Telegram message."""
        if not self.has_done_runtime_init:
            self.runtime_init()

        if not kwargs or "question" not in kwargs:
            return None

        return self.web_transport.parse_inbound(
            payload={
                "question": kwargs.get("question"),
                "chat_session_id": kwargs.get("chat_session_id"),
            }
        )

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
