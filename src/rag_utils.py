"""Shared RAG utilities for PDF processing and question answering."""

import os
from typing import List, Any
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class RAGSystem:
    """Retrieval Augmented Generation system for PDF documents."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.5, max_tokens: int = 512):
        """Initialize RAG system with specified LLM model.

        Args:
            model: OpenAI model name
            temperature: LLM temperature parameter
            max_tokens: Maximum tokens in response
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.vector_db = None
        self.retriever = None
        self.chain = None

    def load_pdf(self, file_path: str) -> List[Any]:
        """Load and parse PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            List of document objects
        """
        loader = UnstructuredPDFLoader(file_path=file_path)
        documents = loader.load()
        return documents

    def split_text(self, documents: List[Any], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Any]:
        """Split documents into chunks.

        Args:
            documents: List of documents to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        return chunks

    def create_vector_db(self, chunks: List[Any], collection_name: str = "pdf-rag") -> Chroma:
        """Create vector database from document chunks.

        Args:
            chunks: List of document chunks
            collection_name: Name for the vector collection

        Returns:
            Chroma vector database
        """
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            collection_name=collection_name
        )
        self.vector_db = vector_db
        return vector_db

    def setup_retriever(self, k: int = 5):
        """Setup retriever for document search.

        Args:
            k: Number of top results to retrieve
        """
        if self.vector_db is None:
            raise ValueError("Vector DB not initialized. Call create_vector_db first.")

        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": k})

    def setup_chain(self, template: str = None):
        """Setup RAG chain for question answering.

        Args:
            template: Custom prompt template (optional)
        """
        if self.retriever is None:
            raise ValueError("Retriever not initialized. Call setup_retriever first.")

        if template is None:
            template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""

        prompt = ChatPromptTemplate.from_template(template)
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, question: str) -> str:
        """Query the RAG system.

        Args:
            question: User question

        Returns:
            Answer from the RAG system
        """
        if self.chain is None:
            raise ValueError("Chain not initialized. Call setup_chain first.")

        return self.chain.invoke(question)

    def get_context(self, question: str, k: int = 5) -> List[str]:
        """Get relevant context for a question.

        Args:
            question: User question
            k: Number of results to retrieve

        Returns:
            List of relevant document chunks
        """
        if self.vector_db is None:
            raise ValueError("Vector DB not initialized.")

        results = self.vector_db.similarity_search(question, k=k)
        return [doc.page_content for doc in results]
