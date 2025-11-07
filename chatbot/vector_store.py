import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

chroma_client = PersistentClient(path=".chroma_db")

collection = chroma_client.get_or_create_collection("conversations")

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Store the conversation in vector db
def upsert_conversation(conv_id, text, metadata=None):
    embedding = embedder.encode(text).tolist()
    collection.upsert(
        ids=[str(conv_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata or {}],
    )

# search similar conversations
def query_conversations(question, top_k=3):
    query_embedding = embedder.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    return results