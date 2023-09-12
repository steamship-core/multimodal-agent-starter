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

    def dog_list_as_json_bullets(self) -> str:
        """Return the list of dogs we know about as JSON bullet points.

        LLMs don't care if we speak in English or JSON, so this is a perfectly fine way to enumerate them.
        """
        return "\n".join([f"- {json.dumps(dog.dict())}" for dog in self.dogs])

    def rewrite_question_with_better_details(
        self, request: str, context: AgentContext
    ) -> str:
        """Rewrite a question with more specific information about the dog specified.

        For example, if the user says: "How much should Barky eat?"
        We want the rewrite to be something like: "How much should a  chocolate labrador that is 2 years old eat?"
        """
        llm = get_llm(context, default=OpenAI(client=context.client))
        dogs = self.dog_list_as_json_bullets()
        rewritten_question = llm.complete(
            QUESTION_REWRITE.format(dogs=dogs, request=request)
        )[0].text.strip()
        return rewritten_question

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[Any]]:
        # Rewrite the question with information about the breed and description
        rewritten_question = self.rewrite_question_with_better_details(
            tool_input[0].text, context
        )

        # Now return the results of issuing that question to Google
        search_tool = SearchTool()
        return search_tool.run([Block(text=rewritten_question)], context)


if __name__ == "__main__":
    print("Try running with an input like 'Fido'")
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
