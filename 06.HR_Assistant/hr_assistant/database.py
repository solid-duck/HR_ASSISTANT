import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from langchain_ollama import OllamaEmbeddings
from config import Config

class OllamaChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name, base_url):
        self.ollama_embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )

    def __call__(self, input):
        # Supporta sia stringhe singole che liste di stringhe
        return self.ollama_embeddings.embed_documents(input)

class Database:
    def __init__(self):
        # Utilizziamo la nostra classe compatibile con ChromaDB
        ef = OllamaChromaEmbeddingFunction(
            model_name=Config.MODEL_NAME,
            base_url=Config.OLLAMA_BASE_URL
        )
        self.client = chromadb.PersistentClient(path=Config.PERSISTENT_DIR)
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME, 
            embedding_function=ef
        )

    def add_documents(self, documents, metadatas, ids):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def get_tracked_files(self):
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