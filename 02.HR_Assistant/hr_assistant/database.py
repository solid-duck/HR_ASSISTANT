# database.py
import chromadb
import httpx
from config import Config

class OllamaEmbeddingFunction:
    def __init__(self, model_name=Config.MODEL_NAME):
        self.url = "http://localhost:11434/api/embed"
        self.model = model_name
        self.client = httpx.Client(timeout=120.0)

    def __call__(self, input):
        response = self.client.post(
            self.url, 
            json={"model": self.model, "input": input}
        )
        return response.json()["embeddings"]

class Database:
    def __init__(self):
        self.ollama_ef = OllamaEmbeddingFunction()

        self.client = chromadb.PersistentClient(path=Config.PERSISTENT_DIR)
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME, embedding_function=self.ollama_ef
        )

    def add_documents(self, documents, metadatas, ids):
        if self.collection.count() == 0:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)