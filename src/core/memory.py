"""Implements various forms of memory for the Agent."""
from typing import List, Optional
from steamship import Steamship
from steamship_langchain.llms import OpenAIChat
from steamship_langchain.vectorstores import SteamshipVectorStore
from langchain.chains import ChatVectorDBChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

MEMORY_HANDLE_DEFAULT = "memory-default"
EMBEDDER_MODEL_DEFAULT = "text-embedding-ada-002"
LLM_MODEL_DEFAULT = "gpt-3.5-turbo"
LLM_TEMPERATURE_DEFAULT = 0
EMBEDDER_DIMENSIONALITY_DEFAULT = 1536
TOP_K_DOCS_FOR_INDEX_DEFAULT = 2

ANSWER_QUESTION_PROMPT_DEFAULT = """I want you to ANSWER a QUESTION based on the following pieces of CONTEXT. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Your ANSWER should be analytical and straightforward. 
Try to share deep, thoughtful insights and explain complex ideas in a simple and concise manner. 
When appropriate use analogies and metaphors to illustrate your point. 
Your ANSWER should have a strong focus on clarity, logic, and brevity.
Your ANSWER should be truthful and correct according to the given SOURCES

CONTEXT: {context}
QUESTION: {question}
ANSWER:"""

REFINE_QUESTION_DEFAULT = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""


class Memory:
    """
    Intended usage:

    Inside the Agent __init__:

       self.memory = Memory(client)

    Elsewhere in the agent:

       self.memory.remember("text")
       self.memory.search("fragment")
       self.memory.answer("question")

    """

    client: Steamship
    handle: str
    llm_model: str
    llm_temperature: int
    embedder_instance_handle: str
    index_instance_handle: str
    embedder_model: str
    top_k_docs_for_index: int
    verbose_logging: bool
    answer_question_prompt: str
    refine_question_prompt: str
    has_done_runtime_init: bool
    
    def __init__(
        self,
        client: Steamship,
        handle: Optional[str] = MEMORY_HANDLE_DEFAULT,
        llm_model: str = LLM_MODEL_DEFAULT,
        llm_temperature: int = LLM_TEMPERATURE_DEFAULT,
        embedder_model: str = EMBEDDER_MODEL_DEFAULT,
        answer_question_prompt: Optional[str] = ANSWER_QUESTION_PROMPT_DEFAULT,
        refine_question_prompt: Optional[str] = REFINE_QUESTION_DEFAULT,
        top_k_docs_for_index: int = TOP_K_DOCS_FOR_INDEX_DEFAULT,
        verbose_logging: bool = False
    ):
        self.client = client
        self.handle = handle
        self.embedder_instance_handle = f"{self.handle}-embedder"
        self.index_instance_handle = f"{self.handle}-index"
        self.has_done_runtime_init = False
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.embedder_model = embedder_model
        self.answer_question_prompt = answer_question_prompt
        self.refine_question_prompt = refine_question_prompt
        self.verbose_logging = verbose_logging
        self.top_k_docs_for_index = top_k_docs_for_index
        
    def runtime_init(self):
        """Called from within method invocation so that the Exception can be caught in a more convenient place."""
        self.has_done_runtime_init = True

    def get_embedding_index(self) -> SteamshipVectorStore:
        """Fetch a named embedding index."""
        if self.index is None:            
          self.index = SteamshipVectorStore(
              client=self.client,
              index_name=self.embedder_instance_handle,
              embedding=self.embedder_model,
          )
        return self.index

    def remember_sentence(self, sentence: str, metadata: Optional[dict] = None) -> dict:
        """Save a fragment of text to the provided embedding index."""
        self.get_embedding_index.add_texts(texts=[sentence], metadatas=[metadata])
    
    def remember_sentences(self, sentences: List[str], metadatas: List[dict] = None) -> dict:
        """Save a fragment of text to the provided embedding index."""
        self.get_embedding_index.add_texts(texts=sentences, metadatas=metadatas)

    def search(self, query: str, k: int = None) -> List[Document]:
        """Retrieve records from the embedding index."""
        search_results = self.get_embedding_index().similarity_search(query, k=k)
        search_results.wait()
        return search_results.output.items

    def answer(self, question: str, index: str = "default", prompt: Optional[str] = None) -> dict:
        """Answer a question using the provided embedding index."""
        llm = OpenAIChat(
          client=self.client, 
          model_name=self.llm_model, 
          temperature=self.llm_temperature, 
          verbose=self.verbose_logging
        )
        doc_chain = load_qa_chain(
          llm,
          chain_type="stuff",
          prompt=self.answer_question_prompt,
          verbose=self.verbose_logging,
        )
        question_chain = LLMChain(
            llm=OpenAIChat(
              client=self.client, 
              model_name=self.llm_model, 
              temperature=self.llm_temperature,
              verbose=self.verbose_logging
            ),
            prompt=self.refine_question_prompt,
        )
        result = ChatVectorDBChain(
            vectorstore=self.get_embedding_index(),
            combine_docs_chain=doc_chain,
            question_generator=question_chain,
            return_source_documents=True,
            top_k_docs_for_context=self.top_k_docs_for_index,
        )
        
        answer = (result["answer"] or "").strip()
        source_documents = result["source_documents"]

        return {"answer": answer, "source_documents": source_documents}



