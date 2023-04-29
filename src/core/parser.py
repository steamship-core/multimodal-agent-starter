import re
from typing import Union

from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain.schema import AgentAction, AgentFinish

FINAL_ANSWER_ACTION = "Final Answer:"

FORMAT_INSTRUCTIONS_W_TOOLS = """
Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do unless it's a casual conversation, then skip to final answer.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. Consider all observations to come up with a final answer.
"""

FORMAT_INSTRUCTIONS_WO_TOOLS = """
Use the following format:

Question: the input question you must answer
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""


def get_format_instructions(has_tools=True) -> str:
    if has_tools:
        return FORMAT_INSTRUCTIONS_W_TOOLS
    else:
        return FORMAT_INSTRUCTIONS_WO_TOOLS


class CustomParser(MRKLOutputParser):
    def get_format_instructions(self) -> str:
        return get_format_instructions(True)

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if FINAL_ANSWER_ACTION in text:
            output = text.split(FINAL_ANSWER_ACTION)[-1].strip()
            output = re.split(
                r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})",
                output,
            )

            output = [re.sub(r"^\W+", "", el) for el in output]

            return AgentFinish({"output": output}, text)
        return super().parse(text)
