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

        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=Config.PERSISTENT_DIR)
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME, 
            embedding_function=self.ollama_ef,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents, metadatas, ids):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def get_tracked_files(self):
        """Get all unique files and their metadata from the database"""
        result = self.collection.get()
        tracked_files = {}

        if result and result["metadatas"]:
            for metadata in result["metadatas"]:
                if metadata["source"] not in tracked_files:
                    tracked_files[metadata["source"]] = {
                        "hash": metadata["hash"],
                        "last_modified": metadata["last_modified"],
                        "source": metadata["source"],
                    }

        return tracked_files

    def remove_document_by_source(self, source):
        """Remove all entries for a specific source file"""
        result = self.collection.get(where={"source": source})
        if result and result["ids"]:
            self.collection.delete(ids=result["ids"])

    def get_stats(self):
        result = self.collection.get()
        valori_distinti = set(d["source"] for d in result["metadatas"])
        numero_files = len(valori_distinti)
        
        return f"""
            Nome Collezione: {self.collection.name}
            Numero totale Frammenti: {self.collection.count()}
            Numero Files Elaborati: {numero_files}
        """
    def get_random_candidate(self):
        result = self.collection.get()
        if not result or not result["metadatas"]:
            return None
        
        import random
        
        sources = list(set(d["source"] for d in result["metadatas"]))
        if not sources:
            return None
            
        chosen_source = random.choice(sources)
        
        
        file_docs = [
            doc for doc, meta in zip(result["documents"], result["metadatas"])
            if meta["source"] == chosen_source
        ]
        
        return {
            "source": chosen_source,
            "content": "\n".join(file_docs)
        }