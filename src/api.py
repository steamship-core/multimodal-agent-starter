import uuid
from typing import List, Optional

from steamship import Block, Task
from steamship.agents.llms.openai import OpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import AgentContext, Action, FinishAction
from steamship.agents.schema.context import Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.invocable import post
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin
from steamship.utils.repl import AgentREPL

from example_tools.vector_search_qa_tool import VectorSearchQATool


class ReACTAgentThatAlwaysUsesToolOutput(ReACTAgent):
    def next_action(self, context: AgentContext) -> Action:
        """Small wrapper around ReACTAgent that ALWAYS uses the output of a tool if available.

        This tends to defer the response to the tool (in this case, VectorSearchQATool) which dramatically
        reduces the LLM answering with hallucinations from its own background knowledge.
        """
        if context.completed_steps and len(context.completed_steps):
            last_step = context.completed_steps[-1]
            return FinishAction(output=last_step.output, context=context)
        return super().next_action(context)


class ExampleDocumentQAService(AgentService):
    """ExampleDocumentQAService is an example bot you can deploy for PDF and Video Q&A.  # noqa: RST201

    To use this example:

        - Copy this file into api.py in your multimodal-agent-starter project.
        - Run `ship deploy` from the command line to deploy a new version to the cloud
        - View and interact with your agent using its web interface.

    API ACCESS:

    Your agent also exposes an API. It is documented from the web interface, but a quick pointer into what is
    available is:

        /learn_url  - Learn a PDF or YouTube link
        /learn_text - Learn a fragment of text

    - An unauthenticated endpoint for answering questions about what it has learned

    This agent provides a starter project for special purpose QA agents that can answer questions about documents
    you provide.
    """

    indexer_mixin: IndexerPipelineMixin

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # This Mixin provides HTTP endpoints that coordinate the learning of documents.
        #
        # It adds the `/learn_url` endpoint which will:
        #    1) Download the provided URL (PDF, YouTube URL, etc)
        #    2) Convert that URL into text
        #    3) Store the text in a vector index
        #
        # That vector index is then available to the question answering tool, below.
        self.indexer_mixin = IndexerPipelineMixin(self.client, self)
        self.add_mixin(self.indexer_mixin, permit_overwrite_of_existing_methods=True)

        # A ReACTAgent is an agent that is able to:
        #    1) Converse with you, casually... but also
        #    2) Use tools that have been provided to it, such as QA tools or Image Generation tools
        #
        # This particular ReACTAgent has been provided with a single tool which will be used whenever
        # the user answers a question. But you can extend this with more tools if you wish. For example,
        # you could add tools to generate images, or search Google, or register an account.
        self._agent = ReACTAgentThatAlwaysUsesToolOutput(
            tools=[
                VectorSearchQATool(
                    agent_description=(
                        "Used to answer questions. "
                        "Whenever the input is a question, ALWAYS use this tool. "
                        "The input is the question. "
                        "The output is the answer. "
                    )
                )
            ],
            llm=OpenAI(self.client),
        )

        # This Mixin provides HTTP endpoints that
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

    @post("/index_url")
    def index_url(
        self,
        url: Optional[str] = None,
        metadata: Optional[dict] = None,
        index_handle: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Task:
        return self.indexer_mixin.index_url(
            url=url, metadata=metadata, index_handle=index_handle, mime_type=mime_type
        )

    @post("prompt")
    def prompt(self, prompt: str) -> str:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)
        # Add the LLM
        context = with_llm(context=context, llm=OpenAI(client=self.client))

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            block_text = "\n".join(
                [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
            )
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(ExampleDocumentQAService, "prompt", agent_package_config={}).run()
