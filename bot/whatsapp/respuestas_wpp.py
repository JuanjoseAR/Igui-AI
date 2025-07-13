# === respuesta_wpp.py ===
from sentence_transformers import SentenceTransformer, util
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from bot.whatsapp.service.preguntas_bajas_service import registrar_pregunta_baja
from modelos.worker_llm import cola_llm  # Asegúrate de importar desde donde lo pongas
from bot.whatsapp.service.pregunta_service import obtener_todas_las_preguntas
import asyncio
import re

modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

# Cargar contexto

datos = obtener_todas_las_preguntas()
preguntas = [fila["pregunta"] for fila in datos]
respuestas = [fila["contexto"] for fila in datos]
respuesta_rapida = [fila["respuesta_rapida"] for fila in datos]
embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)

def recargar_contexto():
    global preguntas, respuestas, respuesta_rapida, embeddings

    datos = obtener_todas_las_preguntas()
    nuevas_preguntas = [fila["pregunta"] for fila in datos]
    nuevas_respuestas = [fila["contexto"] for fila in datos]
    nuevas_rapida = [fila["respuesta_rapida"] for fila in datos]

    modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')
    nuevos_embeddings = modelo_embedding.encode(nuevas_preguntas, convert_to_tensor=True)

    # 🚀 Asignación atómica
    preguntas = nuevas_preguntas
    respuestas = nuevas_respuestas
    respuesta_rapida = nuevas_rapida
    embeddings = nuevos_embeddings

# Función adaptada para WhatsApp
async def responder_pregunta_wpp(user_id: str, mensaje_usuario: str) -> str:
    if es_input_malicioso(mensaje_usuario):
        return "⚠️ Tu mensaje contiene caracteres no permitidos. Reformúlalo sin símbolos especiales ni comandos."
    
    embedding_usuario = modelo_embedding.encode(mensaje_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(embedding_usuario, embeddings)[0]
    indice_max = similitudes.argmax().item()
    score_max = similitudes[indice_max].item()
    usuario = obtener_usuario_por_id_celular(user_id)

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
    
def es_input_malicioso(texto):
    patrones = [
        r"(--|\b(SELECT|INSERT|DELETE|UPDATE|DROP|TRUNCATE|EXEC|UNION|OR|AND)\b)",
        r"[<>;]|(\*{2,})|['\"\\]"
    ]
    for patron in patrones:
        if re.search(patron, texto, re.IGNORECASE):
            return True
    return False
