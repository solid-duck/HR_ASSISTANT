# config.py
import os

class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    
    # Embedding locali con Ollama (bge-m3 o nomic-embed-text)
    MODEL_NAME = "bge-m3"
    
    # Completamento con Ollama
    LLM_MODEL = "llama3.2"
    AI_API_URL = "http://localhost:11434/v1"
    AI_API_KEY = "ollama"  # Ollama richiede una stringa qualsiasi ma non vuota