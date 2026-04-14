# store.py — the only file that talks to ChromaDB.
# Think of it as the Repository / data access layer.
# If we swap ChromaDB for pgvector in Week 4, only this file changes.
import chromadb
import ollama
from datetime import datetime
embedding_model = "nomic-embed-text"
# PersistentClient saves everything to the "chroma_db/" folder on disk.
# Compare:
#   chromadb.Client()           → in-memory only, dies on restart (like Week 1)
#   chromadb.PersistentClient() → survives restarts (what we want)
client = chromadb.PersistentClient(path="chroma_db")

# A Collection is like a database table, but for vectors.
# get_or_create: loads existing data if the folder exists, creates fresh if not.
# hnsw:space tells ChromaDB which distance formula to use.
# "cosine" = same concept as Week 1's cosine similarity.
# Default is "l2" (Euclidean) which gives huge distances that break our formula.
collection = client.get_or_create_collection(
    name="notes",
    metadata={"hnsw:space": "cosine"}
)
def _get_embeddings(text:str)->list[float]:
    # Identical to Week 1's get_embedding.py.
    # The underscore prefix means "internal use only" — main.py never calls this.
    response = ollama.embeddings(model = embedding_model, prompt = text)
    return response["embedding"]

def add_note(text:str,tag:str ="general")->str:
    # Build a unique ID from the current timestamp.
    # e.g. "note_20260412_143022_123456"
    note_id = "note_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    embedding = _get_embeddings(text)
    # .add() takes parallel lists — even for a single item, wrap in [].
    # ChromaDB stores all three together: the text, the math, and the metadata.
    collection.add(
        ids=[note_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "tag":tag,
            "created_at": datetime.now().isoformat(),
        }]
    )
    return note_id

def search_notes(query: str , top_k: int =3)-> list[dict]:
    if collection.count() == 0:
        return []
    print("Embedding query...(calling ollama)")
    query_embeddings = _get_embeddings(query)
    results = collection.query(
        query_embeddings = [query_embeddings],
        n_results = min(top_k, collection.count()),
        include =['documents','metadatas','distances']
    )

# ChromaDB returns distance, not similarity.
# Distance ~0.0 means very similar. Distance ~2.0 means very different.
# We convert: similarity = 1 / (1 + distance)
# So distance 0 → similarity 1.0, distance 1 → similarity 0.5
#
# Results are wrapped in an extra list because ChromaDB supports
# batch queries (multiple queries at once). We're using one, so [0] unwraps it.
    notes = []
    for doc,meta,dist,note_id in zip(results["documents"][0],results["metadatas"][0],results["distances"][0],results["ids"][0]):
        notes.append({
            "id":note_id,
            "text":doc,
            "tag":meta.get("tag","-"),
            "created_at":meta.get("created_at","-"),
            # cosine distance range: 0 (identical) → 2 (opposite)
            # 1 - dist/2 maps that to: 1.0 (identical) → 0.0 (opposite)
            "similarity": round(1 - dist / 2, 4),
        })
    return notes

def list_notes()-> list[dict]:
    if collection.count() == 0:
        return []
    # .get() with no filters returns everything.
    # We don't need embeddings here — just the human-readable data.
    results = collection.get(include=['documents','metadatas'])
    notes = []
    for doc, meta,note_id in zip(results["documents"], results["metadatas"], results["ids"]):
        notes.append({
            "id":note_id,
            "text":doc,
            "tag":meta.get("tag","-"),
            "created_at":meta.get("created_at","-"),
        })
    return notes

def delete_note(note_id:str)-> bool:
    exisiting_ids = collection.get(ids=[note_id])
    if not exisiting_ids["ids"]:
        return False
    collection.delete(ids=[note_id])
    return True

def count_notes()-> int:
    return collection.count()