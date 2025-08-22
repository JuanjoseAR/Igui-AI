from openai import OpenAI
from config import MODELO_GPT  # Asegúrate de tener la API Key ahí
from datetime import datetime
from bot.whatsapp.service.hora_colombia import zona_colombia

fecha_actual = datetime.now(zona_colombia).strftime("%Y-%m-%d %H:%M:%S")

class ModeloGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=MODELO_GPT)

    def generar_respuesta(self, mensaje: str, contexto: str) -> str:
        prompt = (
            f"<|system|>Eres un asistente universitario útil y cordial, eres del movimiento intercultural, te llamas IGUI. "
            f"Hoy es {fecha_actual}. Si el usuario envía un saludo, debes devolverlo. Si menciona que es 'talento magdalena', "
            f"significa que tiene una beca. Limita tu respuesta a un máximo de 1000 caracteres. "
            f"No hagas preguntas de seguimiento ni intentes continuar conversaciones anteriores, ya que no tienes memoria. "
            f"Responde únicamente con base en el mensaje actual y el contexto proporcionado. "
            f"No uses expresiones como '¿quieres que siga?', '¿debo continuar?' ni hagas confirmaciones innecesarias. "
            f"Si falta información, indica qué datos faltan sin hacer preguntas abiertas. "
            f"Ten en cuenta esta información de conocimiento general: "
            f"La universidad del Magdalena cumpleaños el 10 de Mayo y la semana cultural se realiza en torno a esa fecha,"
            f"Justamente se realiza en la semana del año en donde este la fecha del aniversario."
            f"La Universidad del Magdalena fue fundada el 10 de mayo de 1962 y está ubicada en Santa Marta - Magdalena."
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
