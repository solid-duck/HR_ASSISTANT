import os
import chainlit as cl
from document_processor import DocumentProcessor
from database import Database
from config import Config
from utils import LLMHelper

db = Database()

added, updated, removed = DocumentProcessor.process_documents(db)
print(f"Document sync complete: {added} added, {updated} updated, {removed} removed")


@cl.action_callback("db_stats")
async def on_action(action: cl.Action):
    db_info = db.get_stats()
    response = LLMHelper.get_db_stats(db_info)
    await cl.Message(response).send()


@cl.action_callback("db_reindex")
async def on_action(action: cl.Action):
    added, updated, removed = DocumentProcessor.process_documents(db)
    message = f"DB reindicizzato con successo. Document sync complete: {added} added, {updated} updated, {removed} removed"
    await cl.Message(message).send()


@cl.action_callback("lucky_candidate")
async def on_lucky_action(action: cl.Action):
    async with cl.Step(name="Estrazione Candidato Fortunato", type="tool") as step:
        candidate = db.get_random_candidate()
        if not candidate:
            await cl.Message(content="Nessun candidato trovato nel database!").send()
            return
        step.output = f"Candidato estratto: {candidate['source']}"

    preview = candidate["content"][:400]
    message_content = f"**Candidato Fortunato Estratto!**\n\n**File:** `{candidate['source']}`\n\n**Anteprima CV:**\n{preview}..."
    await cl.Message(content=message_content).send()


@cl.on_chat_start
async def start():
    actions = [
        cl.Action(
            name="db_stats",
            icon="mouse-pointer-click",
            payload={"value": "db_stats"},
            label="Statistiche Database",
        ),
        cl.Action(
            name="db_reindex",
            icon="mouse-pointer-click",
            payload={"value": "db_reindex"},
            label="Reindex Database",
        ),
        cl.Action(
            name="lucky_candidate",
            icon="shuffle",
            payload={"value": "lucky_candidate"},
            label="Mi sento fortunato",
        )
    ]

    await cl.Message(content="Informazioni del sistema:", actions=actions).send()

    cl.user_session.set(
        "messages",
        [
            {
                "role": "system",
                "content": """
                    Sei un assistente specializzato nel mondo HR, rispondi in modo professionale, sintetico e pragmatico.
                    Il tuo ruolo è individuare il candidato ideale rispetto alle richieste dell'utente.
                """,
            }
        ],
    )


@cl.on_message
async def handle_message(message: cl.Message):
    user_question = message.content
    
    async with cl.Step(name="Ricerca e Analisi CV", type="tool") as step:
        step.input = user_question
        results = db.query(user_question, 3)
        print("RESULT DB: ", results)
        
        filename = results["metadatas"][0][0]["source"]
        candidate_info = DocumentProcessor.read_first_lines(
            os.path.join(Config.DOCUMENTS_DIR, filename), 10
        )

        context = f"CONTESTO: nome file {results['metadatas'][0][0]['source']} ecco il paragrafo piu' significativo: {results['documents'][0][0]}, qui trovi le informazioni del candidato: {candidate_info}"

        prompt = LLMHelper.create_prompt(context, user_question)
        step.output = "Candidato individuato e contesto preparato."

    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": prompt})

    response_message = cl.Message(content="")
    await response_message.send()

    try:
        async with cl.Step(name="Generazione Risposta HR", type="llm") as llm_step:
            stream = LLMHelper.chat(messages)
            full_response = ""

            for chunk in stream:
                token = str(chunk.choices[0].delta.content or "")
                full_response += token
                await response_message.stream_token(token)

            llm_step.output = full_response

        messages.append({"role": "assistant", "content": response_message.content})
        await response_message.update()

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await cl.Message(content=error_message).send()
        print(error_message)

    cl.user_session.set("messages", messages)