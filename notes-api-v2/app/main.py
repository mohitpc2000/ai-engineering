from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from app.store import add_note, search_notes, delete_note, list_notes

app = FastAPI(title="Smart notes API v2", version = "2.0.0")
class NoteCreate(BaseModel):
    text:str
    tag:str="general"

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/notes", status_code=201)
def create_notes(note:NoteCreate):
    add_note(note.text, note.tag)
    return {"message": "Note added successfully"}

@app.get("/notes/search")
def search(q:str = Query(...), top_k:int = Query(5)):
    results = search_notes(q, top_k)
    return {"results": results}

@app.get("/notes")
def get_notes():
    return {"notes": list_notes()}

@app.delete("/notes/{note_id}")
def remove_note(note_id: str):
    delete_note(note_id)
    return {"message": "Note deleted successfully"}