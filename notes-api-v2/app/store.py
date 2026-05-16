import os
import uuid
import numpy as np
import ollama
import psycopg2
from pgvector.psycopg2 import register_vector

OLLAMA_HOST=os.getenv("OLLAMA_HOST","http://localhost:11434")
ollama_client=ollama.Client(host=OLLAMA_HOST)
def get_connection():
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST","localhost"),
        dbname=os.getenv("POSTGRES_DB","notes"),
        user=os.getenv("POSTGRES_USER","postgres"),
        password=os.getenv("POSTGRES_PASSWORD","password")
    )
    register_vector(connection)
    return connection

def _get_embedding(text):
    response = ollama_client.embeddings(model="nomic-embed-text", prompt=text)
    return np.array(response['embedding'])

def add_note(text,tag):
    embedding = _get_embedding(text)
    note_id = str(uuid.uuid4())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (id,text,tag,embedding) VALUES (%s,%s,%s,%s)",(note_id,text,tag,embedding))
    conn.commit()
    conn.close()

def search_notes(query,top_k):
    embedding = _get_embedding(query)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id,text,tag,1-(embedding<=>%s) AS similarity from notes ORDER BY similarity DESC LIMIT %s",(embedding,top_k))
    results = cur.fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "tag": r[2], "similarity": round(r[3], 4)} for r in results]

def list_notes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id,text,tag FROM notes")
    results = cur.fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "tag": r[2]} for r in results]

def delete_note(note_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    conn.close()