#This file has one job: send text to Ollama, get back a list of numbers.
import ollama
def get_embedding(text):
    response = ollama.embeddings(
        model = "nomic-embed-text",
        prompt = text
    )
    return response['embedding']
