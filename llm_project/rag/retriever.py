"""Retriever — builds a ChromaDB retriever for similarity search."""

import os
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from rag.embeddings import get_embeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vector_db/chroma_store")


def get_retriever(k: int = 5) -> VectorStoreRetriever:
    """Return a ChromaDB retriever configured for top-k similarity search."""
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name="citizen_services",
    )
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
