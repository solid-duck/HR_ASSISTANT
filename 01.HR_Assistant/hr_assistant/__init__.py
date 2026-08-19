import chainlit as cl
import ollama
import chromadb
import os, uuid
import httpx

documents_dir = "resumes"

documents = []
metadatas = []
ids = []

for filename in os.listdir(documents_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(documents_dir, filename), "r") as file:
            chuncks = file.read().replace("\n", ".").split("### ")

            for chunk in chuncks:
                if not chunk.isspace() and not chunk == "":
                    documents.append(chunk)
                    metadatas.append({"source": filename})
                    guid = str(uuid.uuid4())
                    ids.append(guid)

class OllamaEF:
    def __init__(self, model_name="bge-m3"):
        self.url = "http://localhost:11434/api/embed"
        self.model = model_name
        self.client = httpx.Client(timeout=120.0)

    def __call__(self, input):
        response = self.client.post(
            self.url, 
            json={"model": self.model, "input": input}
        )
        return response.json()["embeddings"]

ollama_ef = OllamaEF(model_name="bge-m3")

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(
    name="CVs", embedding_function=ollama_ef
)

if collection.count() == 0:
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

@cl.on_chat_start
def on_chat_start():
    cl.user_session.set(
        "messages",
        [
            {
                "role": "system",
                "content": """Sei un assistente specializzato nel mondo HR, rispondi in modo professionale, sintetico e pragmatico. Il tuo ruolo è individuare il candidato ideale rispetto alle richieste dell'utente.""",
            }
        ],
    )

@cl.on_message
async def handle_message(message: cl.Message):
    user_question = message.content

    results = collection.query(query_texts=[user_question], n_results=1)

    source_file = results["metadatas"][0][0]["source"]
    chunk_text = results["documents"][0][0]

    context = f"CONTESTO: File sorgente '{source_file}'. Paragrafo trovato: {chunk_text}"

    prompt = f"""
        Dato il seguente contesto:
        [[[
        {context}
        ]]].
        Rispondi alla domanda dell'utente: [[[ {user_question} ]]].
        
        Istruzioni:
        1. Indica il nome del file individuato ({source_file}).
        2. Individua ed indica il nome del candidato presente nel contesto.
        3. Argomenta la scelta utilizzando il testo fornito.
        Se non trovi corrispondenza, non inventare."""

    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": prompt})

    response_message = cl.Message(content="")
    await response_message.send()

    try:
        stream = ollama.chat(model="llama3.2", messages=messages, stream=True)

        for chunk in stream:
            await response_message.stream_token(chunk["message"]["content"])

        messages.append({"role": "assistant", "content": response_message.content})
        await response_message.update()
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        cl.Message(content=error_message).send()

    cl.user_session.set("messages", messages)

@cl.on_chat_end
def on_chat_end():
    cl.Message(
        content="""Grazie per aver utilizzato il nostro assistente. Buona giornata!"""
    ).send()