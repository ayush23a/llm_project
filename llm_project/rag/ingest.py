"""Document ingestion pipeline — loads PDFs, TXT files, and web pages, chunks them, and stores in ChromaDB."""

import os
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from rag.embeddings import get_embeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vector_db/chroma_store")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_pdf(file_path: str) -> List[Document]:
    """Load and chunk a PDF file."""
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return text_splitter.split_documents(pages)


def load_txt(file_path: str) -> List[Document]:
    """Load and chunk a plain text file."""
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    return text_splitter.split_documents(docs)


def load_url(url: str) -> List[Document]:
    """Load and chunk content from a web URL."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    return text_splitter.split_documents(docs)


def ingest_documents(file_path: str = None, url: str = None) -> dict:
    """
    Ingest a file or URL into the vector store.
    Returns a summary dict with chunk count and source.
    """
    chunks: List[Document] = []

    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            chunks = load_pdf(file_path)
        elif ext in (".txt", ".md"):
            chunks = load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .txt, .md")

    elif url:
        chunks = load_url(url)
    else:
        raise ValueError("Provide either file_path or url.")

    if not chunks:
        return {"status": "error", "message": "No content extracted."}

    # Add source metadata
    source_name = file_path or url
    for chunk in chunks:
        chunk.metadata["source"] = source_name

    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name="citizen_services",
    )
    vectorstore.add_documents(chunks)

    return {
        "status": "success",
        "source": source_name,
        "chunks_ingested": len(chunks),
    }
