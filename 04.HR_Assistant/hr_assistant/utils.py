from openai import OpenAI
from config import Config

client = OpenAI(
    base_url=Config.AI_API_URL,
    api_key=Config.AI_API_KEY
)

class LLMHelper:
    @staticmethod
    def chat(messages):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            stream=True
        )
        return response

    @staticmethod
    def create_prompt(context, user_question):
        return f"""
            Usa il seguente contesto per rispondere alla domanda dell'utente in modo professionale e sintetico.
            
            {context}
            
            Domanda: {user_question}
        """

    @staticmethod
    def get_db_stats(db_info):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[
                {"role": "system", "content": "Sei un assistente HR sintetico e formatti le risposte in modo pulito."},
                {"role": "user", "content": f"Formatta queste statistiche del database in modo carino e leggibile:\n{db_info}"}
            ]
        )
        return response.choices[0].message.content