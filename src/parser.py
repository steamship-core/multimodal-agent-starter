from typing import Any

from langchain.agents.conversational_chat.base import AgentOutputParser as BaseChatAgentOutputParser


class ChatCustomParser(BaseChatAgentOutputParser):
    @property
    def _type(self) -> str:
        return "ChatCustomParser"

    def parse(self, text: str) -> Any:
        cleaned_output = text.strip()
        if cleaned_output.startswith("AI: "):
            cleaned_output = cleaned_output[len("AI: "):]
        return super().parse(cleaned_output)
