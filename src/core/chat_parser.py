import re
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
        try:
            return super().parse(cleaned_output)
        except Exception as e:
            # Try to get a UUID.
            try:
                output = re.split(
                    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})",
                    output,
                )
                output = [re.sub(r"^\W+", "", el) for el in output]
                return {
                    "action": "Final Answer",
                    "action_input": output[0]
                }
            except Exception as e:
                return {
                    "action": "Final Answer",
                    "action_input": cleaned_output
                }
