import chromadb
from chromadb.utils import embedding_functions
import ollama
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import uuid

MODEL_NAME = "gemma3:1b"

TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=100)

chroma_client = None
collection = None


def get_collection():
    global chroma_client, collection
    if collection is None:
        print("Initializing ChromaDB and Embeddings...")
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        print("Downloading/Loading Embedding Model (this may take a while)...")
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2")
        collection = chroma_client.get_or_create_collection(name="samsung_docs",
                                                            embedding_function=sentence_transformer_ef)
        print("ChromaDB Initialized.")
    return collection


def ingest_document(file_path: str, original_filename: str):
    ext = os.path.splitext(original_filename)[1].lower()
    text = ""

    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback for other encodings if needed, or strict error
            with open(file_path, "r", encoding="cp949") as f:
                text = f.read()
    else:
        return 0  # Unsupported

    if not text.strip():
        return 0

    print(f"Splitting text for {original_filename}...")
    chunks = TEXT_SPLITTER.split_text(text)

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": original_filename} for _ in chunks]

    print(f"Adding {len(chunks)} chunks to collection...")
    col = get_collection()
    col.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    return len(chunks)
