import os
import chromadb
import ollama
from datetime import datetime

EMBED_MODEL = 'nomic-embed-text'
# Read Ollama host from environment. Default to localhost for local dev.
# In Docker, we'll set OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_HOST = os.getenv("OLLAMA_HOST","http://localhost:11434")

# ollama.Client lets us specify which host to connect to.
# In Week 2 we used ollama.embeddings() directly — that always hits localhost.
# Now we create a client pointed at the right host.
ollama_client = ollama.Client(host = OLLAMA_HOST)

# PersistentClient — same as Week 2.
# Path is also configurable so Docker can mount a volume here.
CHROMA_PATH = os.getenv("CHROMA_PATH","chroma_db")
chroma_client = chromadb.PersistentClient(path = CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name = "notes",
    metadata = {"hnsw:space" : "cosine"}
)

def _get_embeddings(text:str) ->list[float]:
    response = ollama_client.embeddings(model= EMBED_MODEL, prompt= text)
    return response['embedding']

def add_note(text:str,tag:str ="general")->str:
    note_id = "note_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    embedding = _get_embeddings(text)
    collection.add(
        ids = [note_id],
        documents= [text],
        embeddings= [embedding],
        metadatas=[{
            "tag":tag,
            "created_at":datetime.now().isoformat(),
        }]
    )
    return note_id

def search_notes(query:str,top_k:int=3)->list[dict]:
    if collection.count()==0:
        return []
    query_embedding = _get_embeddings(query)
    results = collection.query(
        query_embeddings= [query_embedding],
        n_results= min(top_k,collection.count()),
        include= ["documents","metadatas","distances"]
    )
    notes = []
    for doc,meta,dist,note_id in zip(results["documents"][0],results["metadatas"][0],results["distances"][0],results["ids"][0]):
        notes.append({
            "id": note_id,
            "text": doc,
            "tag": meta.get("tag", "—"),
            "created_at": meta.get("created_at", "—"),
            "similarity": round(1 - dist / 2, 4),
        })
    return notes

def list_notes() -> list[dict]:
    if collection.count() == 0:
        return []

    results = collection.get(include=["documents", "metadatas"])

    notes = []
    for doc, meta, note_id in zip(
        results["documents"],
        results["metadatas"],
        results["ids"],
    ):
        notes.append({
            "id": note_id,
            "text": doc,
            "tag": meta.get("tag", "—"),
            "created_at": meta.get("created_at", "—"),
        })

    return notes

def delete_note(note_id:str)->bool:
    existing = collection.get(ids=[note_id])
    if not existing["ids"]:
        return False

    collection.delete(ids=[note_id])
    return True

def count_notes() -> int:
    return collection.count()
