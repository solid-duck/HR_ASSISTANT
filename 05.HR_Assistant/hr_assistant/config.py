# config.py
import os


class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    # Embedding
    MODEL_NAME = "text-embedding-3-large"
    OPENAI_KEY = "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"
    # Completamento
    ### ollama
    # LLM_MODEL = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b"
    # LLM_MODEL_LOW = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b"
    # AI_API_URL = "http://localhost:11434/v1"
    # AI_API_KEY = "ollama"
    ### openai
    LLM_MODEL = "gpt-4o"
    LLM_MODEL_LOW = "gpt-4o-mini"
    AI_API_URL = "https://api.openai.com/v1/"
    AI_API_KEY = "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"
