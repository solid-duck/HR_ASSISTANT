import os

class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    MODEL_NAME = "bge-m3"
    OPENAI_KEY = "ollama"
    LLM_MODEL = "llama3.2"
    LLM_MODEL_LOW = "llama3.2"
    AI_API_URL = "http://localhost:11434/v1"
    AI_API_KEY = "ollama"