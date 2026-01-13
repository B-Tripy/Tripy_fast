import os
import warnings
import sys

# Suppress TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="keras.src.export.tf2onnx_lib")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*np.object.*")

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
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = chroma_client.get_or_create_collection(name="samsung_docs", embedding_function=sentence_transformer_ef)
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
        return 0 # Unsupported

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

def query_rag(query_text: str, source_filter: str = None):
    # 1. Retrieve relevant docs
    where_clause = None
    if source_filter and source_filter != "All Documents":
        where_clause = {"source": source_filter}

    if source_filter and source_filter != "All Documents":
        where_clause = {"source": source_filter}

    col = get_collection()
    results = col.query(
        query_texts=[query_text],
        n_results=3,
        where=where_clause
    )
    
    context_text = "\n\n".join(results['documents'][0])
    
    # 2. Construct Prompt
    prompt = f"""
    You are a helpful assistant for Samsung Electronics employees.
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know.
    
    Context:
    대답은 한글로 해줘. 짧게 단답형으로 핵심만
    {context_text}
    
    Question: {query_text}
    
    Answer:
    """
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

def get_document_count():
    col = get_collection()
    return col.count()

def get_unique_sources():
    # ChromaDB doesn't have a direct 'select distinct metadata' fast path, 
    # but for a local agent, fetching metadata is okay.
    # Optimized approach: get all items, extract sources.
    # Note: potentially slow for HUGE dbs, but fine for local RAG.
    col = get_collection()
    all_data = col.get(include=["metadatas"])
    sources = set()
    for meta in all_data["metadatas"]:
        if "source" in meta:
            sources.add(meta["source"])
    return list(sources)

def reset_database():
    global chroma_client, collection
    
    # Ensure initialized to delete? Or just try?
    if chroma_client is None: 
         get_collection() # Initialize first
         
    chroma_client.delete_collection("samsung_docs")
    # Re-create immediately
    # Force re-init of collection obj
    collection = None
    get_collection()
    return True
