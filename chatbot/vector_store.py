import chromadb
from chromadb import PersistentClient
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Connect to ChromaDB (local persistent storage)
chroma_client = PersistentClient(path=".chroma_db")
collection = chroma_client.get_or_create_collection("conversations")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables")

client = Groq(api_key=GROQ_API_KEY)
EMBED_MODEL = "text-embedding-3-small"

def embed_text(text: str) -> list:
    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("Groq embedding error:", e)
        return [0.0] * 1536  # fallback dummy vector

# Store conversation in vector DB
def upsert_conversation(conv_id: str, text: str, metadata=None):
    embedding = embed_text(text)
    collection.upsert(
        ids=[str(conv_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata or {}],
    )

# Search for similar conversations
def query_conversations(question: str, top_k: int = 3):
    query_embedding = embed_text(question)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
