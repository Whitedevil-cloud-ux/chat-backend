import chromadb
from chromadb import PersistentClient
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

chroma_client = PersistentClient(path=".chroma_db")

collection_name = "conversations"
try:
    chroma_client.delete_collection(collection_name)
except Exception:
    pass  

collection = chroma_client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}  
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables")

client = Groq(api_key=GROQ_API_KEY)
EMBED_MODEL = "text-embedding-ada-002"  

def embed_text(text: str) -> list:
    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("Groq embedding error:", e)
        return [0.0] * 1536  

def upsert_conversation(conv_id: str, text: str, metadata=None):
    embedding = embed_text(text)
    collection.upsert(
        ids=[str(conv_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata or {}],
    )

def query_conversations(question: str, top_k: int = 3):
    query_embedding = embed_text(question)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
