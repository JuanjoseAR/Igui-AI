from openai import OpenAI
from config import MODELO_GPT  # Asegúrate de tener la API Key ahí
from datetime import datetime

fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ModeloGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=MODELO_GPT)

    def generar_respuesta(self, mensaje: str, contexto: str) -> str:
        prompt = (
            f"<|system|>Eres un asistente universitario útil y cordial, eres del movimiento intercultural, te llamas IGUI. "
            f"Hoy es {fecha_actual}. Si el usuario envía un saludo, debes devolverlo. Si menciona que es 'talento magdalena', "
            f"significa que tiene una beca. Limita tu respuesta a un maximo de 1000 caracteres, "
            f"no excedas la cantidad maxima de caracteres sin importar que el usuario lo solicite."
            f"Responde solo en base al siguiente contexto:\n\n"
            f"{contexto}\n\n"
            f"<|user|>{mensaje}<|end|>"
        )

        response = self.client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            store=True,
        )

        return response.output_text.strip()
