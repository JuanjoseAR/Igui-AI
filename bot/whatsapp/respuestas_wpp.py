# === respuesta_wpp.py ===
import json
from sentence_transformers import SentenceTransformer, util
from config import RUTA_JSON_CONTEXTO
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from bot.whatsapp.service.preguntas_bajas_service import registrar_pregunta_baja
from modelos.worker_llm import cola_llm  # Asegúrate de importar desde donde lo pongas
import asyncio

modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

# Cargar contexto
with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
    contexto = json.load(f)
    preguntas = [item['pregunta'] for item in contexto]
    respuestas = [item['respuesta'] for item in contexto]
    respuesta_rapida = [item['respuesta_rapida'] for item in contexto]
    documentos = [item['documentos'] for item in contexto]
    embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)

# Función adaptada para WhatsApp
async def responder_pregunta_wpp(user_id: str, mensaje_usuario: str) -> str:
    embedding_usuario = modelo_embedding.encode(mensaje_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(embedding_usuario, embeddings)[0]
    indice_max = similitudes.argmax().item()
    score_max = similitudes[indice_max].item()
    usuario = obtener_usuario_por_id_celular(user_id)
    print(f"🧠 Pregunta usuario: {mensaje_usuario}")
    print(f"🔎 Pregunta más cercana: {preguntas[indice_max]}")
    print(f"🎯 Similitud: {score_max}")
    
    if score_max >= 0.90:
        await asyncio.sleep(2)
        return f"🧠 {respuesta_rapida[indice_max]}"

    elif 0.65 <= score_max < 0.90:
        contexto_relacionado = respuestas[indice_max]
        future = asyncio.get_event_loop().create_future()
        await cola_llm.put((
            usuario["id"],
            mensaje_usuario,
            contexto_relacionado,
            None,  # fallback = None porque usamos contexto
            future,
            score_max,
            preguntas[indice_max]  # esta es la pregunta más cercana (para el campo pregunta_mas_cercana)
        ))

        return await future

    else:
        usuario = obtener_usuario_por_id_celular(user_id)
        if usuario:
            registrar_pregunta_baja(usuario["id"], mensaje_usuario)
        respuesta_fallback = (
            "Vas a devolver un saludo si el usuario mando algun mensaje que corresponda a un saludo. "
            "Si el usuario no envio ningun saludo responde que no tienes respuesta para esa información, "
            "que reformule mejor su pregunta o si desea que se contacte con un representante a traves del comando /ayuda."
        )
        future = asyncio.get_event_loop().create_future()
        await cola_llm.put((
            usuario["id"],
            mensaje_usuario,
            None,
            respuesta_fallback,
            future,
            score_max,
            preguntas[indice_max]
        ))

        return await future
