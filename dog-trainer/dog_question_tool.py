"""Tool for generating images."""
import json
from typing import Any, List, Union

from dog import Dog
from steamship import Block, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.tools.search import SearchTool
from steamship.agents.utils import get_llm
from steamship.utils.repl import ToolREPL

QUESTION_REWRITE = """Please rephrase the question below so that it includes specific information about the dog breed and dog description.

You know about the following dogs:

{dogs}

Here is a question from a user. Rewrite the request so that it includes the breed of dog but not the name. Include the description if relevant to the question. Return the rewritten request and nothing else.

REQUEST: {request}

REWRITTEN REQUEST:"""


class DogQuestionTool(Tool):
    name: str = "QuestionTool"
    human_description: str = "Answers a Question."
    agent_description = (
        "Used to answer questions about dogs. "
        "Use this tool whenever a user asks a dog-related question, or for dog-related advice. "
        "Input: The question or advice request. "
        "Output: The answer."
    )

    dogs: List[Dog]

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[Any]]:
        llm = get_llm(context, default=OpenAI(client=context.client))

        dogs = "\n".join([f"- {json.dumps(dog.dict())}" for dog in self.dogs])

        rewritten_question = llm.complete(
            QUESTION_REWRITE.format(dogs=dogs, request=tool_input[0].text)
        )[0].text.strip()

        print(rewritten_question)

        # Create the Stable Diffusion tool we want to wrap
        search_tool = SearchTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        return search_tool.run([Block(text=rewritten_question)], context)


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    ToolREPL(
        DogQuestionTool(
            dogs=[
                Dog(
                    name="Fido",
                    breed="Daschund",
                    description="A silly dog whose tongue is always out.",
                ),
                Dog(
                    name="Biggy",
                    breed="German Shephard",
                    description="A strong dog that is always guarding things.",
                ),
            ]
        )
    ).run()
