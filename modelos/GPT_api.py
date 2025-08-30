# GPT_API.py
from openai import OpenAI
from config import MODELO_GPT, ASSISTANT_ID
from bot.whatsapp.service.thread_service import obtener_o_crear_thread

class ModeloGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=MODELO_GPT)

    def generar_respuesta(self, user_id: int, mensaje: str) -> str:
        # 1. obtener o crear thread_id para este usuario (diario)
        thread_id = obtener_o_crear_thread(self.client, user_id)

        # 2. añadir mensaje al thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=mensaje
        )

        # 3. ejecutar el Assistant
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # 4. leer la respuesta
        if run.status == "completed":
            mensajes = self.client.beta.threads.messages.list(thread_id=thread_id)
            return mensajes.data[0].content[0].text.value.strip()
        else:
            return "⚠️ Ocurrió un error procesando tu mensaje. Intenta de nuevo."
