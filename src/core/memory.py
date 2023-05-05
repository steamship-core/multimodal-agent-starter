"""Implements various forms of memory for the Agent."""
from typing import Optional
from steamship import Steamship


class Memory:
    """
    Intended usage:

    Inside the Agent __init__:

       self.memory = Memory(..)

    """

    client: Steamship
    embedder_handle: str
    embedder_version: str
    embedder_dimensionality: int
    has_done_runtime_init: bool

    def __init__(
        self,
        client: Steamship,
        embedder_handle: str,
        embedder_version: str,
        embedder_dimensionality: int,
    ):
        self.client = client
        self.has_done_runtime_init = False
        self.embedder_handle = embedder_handle
        self.embedder_version = embedder_version
        self.embedder_dimensionality = embedder_dimensionality

    def runtime_init(self):
        """Called from within method invocation so that the Exception can be caught in a more convenient place."""
        self.has_done_runtime_init = True

    def get_embedding_index(self, index: str = "default") -> EmbeddingIndex:
        """Fetch a named embedding index."""
        pass

    def remember(self, text: str, metadata: Optional[dict] = None, index: str = "default") -> dict:
        """Save a fragment of text to the provided embedding index."""
        pass
    
    def search(self, text: str, index: str = "default") -> dict:
        """Retrieve records from the provided embedding index."""
        pass

    def answer(self, question: str, index: str = "default", prompt: Optional[str] = None) -> dict:
        """Answer a question using data from the provided embedding index."""
        pass

