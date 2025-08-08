from openai import OpenAI
from config import MODELO_GPT  # Tu API key
from datetime import datetime

class ModeloGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=MODELO_GPT)

    def generar_respuesta(self, mensaje: str, contexto: str) -> str:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Eres IGUI, un asistente universitario útil y cordial del movimiento intercultural. "
                        f"Hoy es {fecha_actual}. Si el usuario envía un saludo, devuélvelo cordialmente. "
                        f"Si menciona que es 'Talento Magdalena', significa que tiene una beca. "
                        f"Nunca debes exceder los 1000 caracteres en tu respuesta, incluso si el usuario lo solicita. "
                        f"Responde únicamente con base en este contexto:\n\n{contexto}"
                    )
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ],
            max_tokens=200,  # Aprox. 800-1000 caracteres
            temperature=0.0
        )

        return response.choices[0].message.content.strip()
