# config.py
import os


class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    # Embedding
    MODEL_NAME = "text-embedding-3-small"
    OPENAI_KEY = "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"
    # Completamento
    ### ollama
    # LLM_MODEL = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b"
    # AI_API_URL = "http://localhost:11434/v1"
    # AI_API_KEY = "ollama"
    ### openai
    LLM_MODEL = "gpt-4o-mini"
    AI_API_URL = "https://api.openai.com/v1/"
    AI_API_KEY = "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"
