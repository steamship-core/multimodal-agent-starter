from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin
from steamship.utils.repl import AgentREPL


class DocsiteBot(AgentService):
    """DocsiteBot is intended to be a production-ready Agent for developer projects.

    [GOALS]

    - Update the Knowledge Base every time a new GitHub Release is created for your open source project.
    - Interact with users via a chat widget on your DocSite
    - Interact with users on your Discord

    [DESIGN]

    - DocsiteBot is based off of the documetn_qa_agent.py, which implements a simple question-answering bot that
      supports hot-loading URLs pointing at PDF and YouTube files.

    """

    USED_MIXIN_CLASSES = [
        IndexerPipelineMixin,  # Provide an asynchronous pipeline for learning documents from URL
        FileImporterMixin,  # Provide async endpoints for loading files via URL
        BlockifierMixin,  # Provide async endpoints for byte-converting files via URL
        IndexerMixin,  # Provide async endpoints for indexing files via URL
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
            tools=[VectorSearchQATool()],
            llm=ChatOpenAI(self.client),
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(DocsiteBot, agent_package_config={}).run()
