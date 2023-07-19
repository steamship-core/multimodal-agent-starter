from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin
from steamship.utils.repl import AgentREPL

from slack import SlackTransport, SlackTransportConfig

QUESTION_ANSWERING_PROMPT = """Use the following pieces of technical documentation to answer the question at the end.
If you don't know the answer, just say you don't know; don't try to make up an answer.

TECHNICAL DOCUMENTATION
=======================

{source_text}

QUESTION
========

{question}

HELPFUL ANSWER
=============="""


SOURCE_DOCUMENT_PROMPT = """Document:
{text}"""


class ExampleDocumentQAService(AgentService):
    """DocumentQAService is an example AgentService that exposes:  # noqa: RST201

    - A few authenticated endpoints for learning PDF and YouTube documents:

         /index_url
        { url }

        /index_text
        { text }

    - An unauthenticated endpoint for answering questions about what it has learned

    This agent provides a starter project for special purpose QA agents that can answer questions about documents
    you provide.
    """

    USED_MIXIN_CLASSES = [
        IndexerPipelineMixin,
        FileImporterMixin,
        BlockifierMixin,
        IndexerMixin,
        SlackTransport,
        SteamshipWidgetTransport,
    ]

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
        self.add_mixin(IndexerPipelineMixin(self.client, self))

        self._agent = FunctionsBasedAgent(
            tools=[
                VectorSearchQATool(
                    question_answering_prompt=QUESTION_ANSWERING_PROMPT,
                    source_document_prompt=SOURCE_DOCUMENT_PROMPT,
                )
            ],
            llm=ChatOpenAI(self.client),
        )
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

        self.add_mixin(
            SlackTransport(self.client, SlackTransportConfig(), self, self._agent)
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(ExampleDocumentQAService, agent_package_config={}).run()
