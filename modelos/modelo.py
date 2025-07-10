# === modelos/modelo.py ===
from config import RUTA_MODELO, MAX_TOKENS
from llama_cpp import Llama

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
        prompt = f"""[INST] Eres un asistente útil del movimiento intercultural, estas para ayudar a estudiantes universitarios. Si no sabes algo, sé honesto. Contesta al usuario de forma clara y precisa basándote únicamente en el siguiente contexto. Si el contexto contiene un saludo, se cordial y añade un saludo a tu respuesta.\n\nContexto:\n{contexto}\n\nUsuario: {mensaje} [/INST]"""
        respuesta = self.modelo(prompt, max_tokens=MAX_TOKENS)
        return respuesta['choices'][0]['text'].strip()