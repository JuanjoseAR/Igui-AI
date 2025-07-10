import json
from sentence_transformers import SentenceTransformer, util
from config import RUTA_JSON_CONTEXTO
from modelos.modelo import ModeloMistral
import asyncio
modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')
modelo_llm = ModeloMistral()

# Cargar contexto
with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
    contexto = json.load(f)
    preguntas = [item['pregunta'] for item in contexto]
    respuestas = [item['respuesta'] for item in contexto]
    respuesta_rapida = [item['respuesta_rapida'] for item in contexto]
    documentos = [item['documentos'] for item in contexto]
    embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)

# Función adaptada para WhatsApp
async def responder_pregunta_wpp(mensaje_usuario: str) -> str:
    embedding_usuario = modelo_embedding.encode(mensaje_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(embedding_usuario, embeddings)[0]
    indice_max = similitudes.argmax().item()
    score_max = similitudes[indice_max].item()

    print(f"🧠 Pregunta usuario: {mensaje_usuario}")
    print(f"🔎 Pregunta más cercana: {preguntas[indice_max]}")
    print(f"🎯 Similitud: {score_max}")

    if score_max >= 0.90:
        await asyncio.sleep(2)
        return f"🧠 {respuesta_rapida[indice_max]}"
    
    elif 0.65 <= score_max < 0.90:
        contexto_relacionado = respuestas[indice_max]
        texto_generado = modelo_llm.generar_respuesta(mensaje_usuario, contexto_relacionado)
        return f"💡 {texto_generado}"
    
    else:
        respuesta_fallback = "Vas a devolver un saludo si el usuario mando algun mensaje que corresponda a un saludo. Si el usuario no envio ningun saludo responde que no tienes respuesta para esa información, que reformule mejor su pregunta o si desea que se contacte con un representate a traves del comando /ayuda. Prioriza el comando /ayuda si no sabes la respuesta"
        texto = modelo_llm.generar_respuesta(mensaje_usuario, respuesta_fallback)
        return f"💡 {texto}"
