# app/main.py — FastAPI application.
# Defines all HTTP routes. Calls store.py for data operations.
# Never touches ChromaDB directly — that's store.py's job.

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from app.store import add_note, search_notes, list_notes, delete_note, count_notes

# FastAPI() creates the application instance.
# title and version show up in the auto-generated /docs page.

app = FastAPI(title = "Smart Notes API", version = "1.0.0")

# ---------------------------------------------------------------------------
# REQUEST MODELS (Pydantic)
# ---------------------------------------------------------------------------
# Pydantic models define the shape of incoming JSON request bodies.
# FastAPI validates the request against this automatically —
# if "text" is missing, it returns a 422 error without you writing any code.
# Think of these as DTOs (Data Transfer Objects) in ASP.NET.

class NoteCreate (BaseModel):
    text:str
    tag:str = "general"

# ---------------------------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------------------------
# Standard in every production API. Load balancers and Docker health checks
# hit this endpoint to know if the service is alive.
# Returns 200 OK with a simple message — that's all that's needed.

@app.get("/health")
def health_check():
    return {"status" : "ok" , "notes_count" : count_notes()}


# ---------------------------------------------------------------------------
# ADD NOTE
# ---------------------------------------------------------------------------
# POST /notes
# Request body: { "text": "...", "tag": "..." }
# Response:     { "id": "note_...", "text": "...", "tag": "..." }
#
# status_code=201 — HTTP 201 Created is the correct code when a resource
# is created, not 200 OK. Small detail but correct REST practice.

@app.post("/notes", status_code = 201)
def create_note(note : NoteCreate):
    # FastAPI automatically parses the JSON body into a NoteCreate object.
    # If "text" is missing from the request, FastAPI returns 422 before
    # this function is even called.
    note_id = add_note(note.text, note.tag)
    return { "id" : note_id, "text" : note.text, "tag" : note.tag}

# ---------------------------------------------------------------------------
# SEARCH NOTES
# ---------------------------------------------------------------------------
# GET /notes/search?q=your+query&top=3
#
# Query parameters (the ?key=value part of the URL) are defined as
# function parameters with Query(). FastAPI reads them automatically.
# Query(...) means required. Query(3) means optional with default 3.

@app.get("/notes/search")
def search(q:str = Query(...,description="Search Query"), top:int = Query(3,description = "Number of results to return")):
    if not q.strip():
        raise HTTPException(status_code= 400, detail="Query cannot be empty")
    results = search_notes(q,top)
    return {"query":q, "results":results}


# ---------------------------------------------------------------------------
# LIST ALL NOTES
# ---------------------------------------------------------------------------
# GET /notes
@app.get("/notes")
def get_all_notes():
    notes = list_notes()
    return {"count" : len(notes), "notes":notes}

# ---------------------------------------------------------------------------
# DELETE NOTE
# ---------------------------------------------------------------------------
# DELETE /notes/{id}
#
# Path parameters (the {id} part of the URL) are defined as function
# parameters matching the name in the route decorator.
# FastAPI extracts them automatically.

@app.delete("/notes/{note_id}")
def remove_note(note_id:str):
    isSuccess = delete_note(note_id)
    if not isSuccess:
        raise HTTPException(status_code= 404, detail=f"Note '{note_id}' not found")
    return {"deleted" : note_id}
