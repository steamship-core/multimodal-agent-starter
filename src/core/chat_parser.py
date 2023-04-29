from typing import Any

from langchain.agents.conversational_chat.output_parser import ConvoOutputParser


class ChatCustomParser(ConvoOutputParser):
    @property
    def _type(self) -> str:
        return "ChatCustomParser"

    def parse(self, text: str) -> Any:
        cleaned_output = text.strip()
        if cleaned_output.startswith("AI: "):
            cleaned_output = cleaned_output[len("AI: ") :]
        return super().parse(cleaned_output)
