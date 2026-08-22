from config import Config
from openai import OpenAI

client = OpenAI(
    base_url=f"{Config.OLLAMA_BASE_URL}/v1",
    api_key="ollama"
)

class LLMHelper:
    @staticmethod
    def chat(messages):
        return client.chat.completions.create(
            model=Config.LLM_MODEL, messages=messages, stream=True
        )

    @staticmethod
    async def get_candidate_name(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[{"role": "user", "content": f"Dato il contesto {context}, ritorna solo nome e cognome del candidato."}]
        )
        return response.choices[0].message.content

    @staticmethod
    async def get_db_stats(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[{"role": "user", "content": f"Sintetizza queste statistiche: {context}"}]
        )
        return response.choices[0].message.content

    @staticmethod
    def create_prompt(context, question):
        return f"""
            Contesto: {context}.
            Domanda: {question}.
            Individua il profilo adatto, argomenta la scelta, indica il nome e i contatti.
            Nome file solo alla fine.
        """