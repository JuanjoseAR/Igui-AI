# === modelos/modelo.py ===
from config import RUTA_MODELO, MAX_TOKENS
from llama_cpp import Llama
from datetime import datetime

fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ModeloMistral:
    def __init__(self):
        self.modelo = Llama(
            model_path=RUTA_MODELO,
            n_ctx=MAX_TOKENS,
            n_threads=8,  # Usa los 8 núcleos del i5
            n_gpu_layers=20,  # Ajusta según los 4GB de VRAM
            verbose=False
        )

    def generar_respuesta(self, mensaje: str, contexto) -> str:
        prompt = f"""[INST] Eres un asistente útil del movimiento intercultural, estas para ayudar a estudiantes universitarios. Si el usuario manda un saludo, se cordial y añade un saludo a tu respuesta. Hoy es {fecha_actual}. Ten en cuenta esta fecha para responder preguntas relacionadas con periodos, fechas o vigencias de normas. Si un estudiante te dice que algo como "soy talento magdalena" se refiere a que tiene la beca del programa de talento magdalena.  Si no sabes algo, sé honesto. Contesta al usuario de forma clara y precisa basándote únicamente en el siguiente contexto. Limita tu respuesta a un maximo de 1000 caracteres o maximo 200 palabras, no excedas ninguna de las dos cantidades asi el usuario lo solicite.\n\nContexto:\n{contexto}\n\nUsuario: {mensaje} [/INST]"""
        respuesta = self.modelo(prompt, max_tokens=MAX_TOKENS)
        return respuesta['choices'][0]['text'].strip()