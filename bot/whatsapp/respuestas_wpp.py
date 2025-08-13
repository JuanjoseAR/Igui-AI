#respuesta_wpp.py
from sentence_transformers import SentenceTransformer, util
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from bot.whatsapp.service.preguntas_bajas_service import registrar_pregunta_baja
from modelos.worker_llm import cola_llm
from bot.whatsapp.service.pregunta_service import obtener_todas_las_preguntas
from bot.whatsapp.service.filtro_keyword import filtrar_preguntas_por_keywords
import asyncio
import re

modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

# Cargar contexto
datos = obtener_todas_las_preguntas()
preguntas = [fila["pregunta"] for fila in datos]
respuestas = [fila["contexto"] for fila in datos]
respuesta_rapida = [fila["respuesta_rapida"] for fila in datos]
preguntas_con_keywords = [{"pregunta": fila["pregunta"], "keywords": fila["keywords"]} for fila in datos]
embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)

def recargar_contexto():
    global preguntas, respuestas, respuesta_rapida, embeddings, preguntas_con_keywords

    datos = obtener_todas_las_preguntas()
    preguntas = [fila["pregunta"] for fila in datos]
    respuestas = [fila["contexto"] for fila in datos]
    respuesta_rapida = [fila["respuesta_rapida"] for fila in datos]
    preguntas_con_keywords = [{"pregunta": fila["pregunta"], "keywords": fila["keywords"]} for fila in datos]
    embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)
    print("✅ Contexto recargado.")

async def responder_pregunta_wpp(user_id: str, mensaje_usuario: str) -> str:
    if es_input_malicioso(mensaje_usuario):
        return "⚠️ Tu mensaje contiene caracteres no permitidos. Reformúlalo sin símbolos especiales ni comandos."

    preguntas_filtradas = filtrar_preguntas_por_keywords(mensaje_usuario, preguntas_con_keywords, umbral=0.6, umbral_individual=0.85, debug=False)
    preguntas_uso = preguntas_filtradas if preguntas_filtradas else preguntas

    embeddings_candidatos = modelo_embedding.encode(preguntas_uso, convert_to_tensor=True)
    embedding_usuario = modelo_embedding.encode(mensaje_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(embedding_usuario, embeddings_candidatos)[0]
    indice_max = similitudes.argmax().item()
    score_max = similitudes[indice_max].item()
    mejor_pregunta = preguntas_uso[indice_max]

    # Resolver índice global solo si filtró
    if preguntas_filtradas:
        indice_global = preguntas.index(mejor_pregunta)
    else:
        indice_global = indice_max

    usuario = obtener_usuario_por_id_celular(user_id)
    print(f"🧠 Pregunta usuario: {mensaje_usuario}")
    print(f"🔎 Pregunta más cercana: {mejor_pregunta}")
    print(f"🎯 Similitud: {score_max}")

    if score_max >= 0.90:
        await asyncio.sleep(2)
        return f"🧠 {respuesta_rapida[indice_global]}"

    elif 0.65 <= score_max < 0.90:
        contexto_relacionado = respuestas[indice_global]
        future = asyncio.get_event_loop().create_future()
        await cola_llm.put((
            usuario["id"],
            mensaje_usuario,
            contexto_relacionado,
            None,
            future,
            score_max,
            mejor_pregunta
        ))
        return await future

    else:
        if usuario:
            registrar_pregunta_baja(usuario["id"], mensaje_usuario)
        respuesta_fallback = (
            "<|system|> Vas a devolver un saludo si el usuario mando algun mensaje que corresponda a un saludo. "
            "Si el usuario no envio ningun saludo responde que no tienes respuesta para esa información, "
            "que reformule mejor su pregunta o si desea que se contacte con un representante a traves del comando /ayuda. <|end|>"
        )
        future = asyncio.get_event_loop().create_future()
        await cola_llm.put((
            usuario["id"],
            mensaje_usuario,
            None,
            respuesta_fallback,
            future,
            score_max,
            mejor_pregunta
        ))
        return await future

def es_input_malicioso(texto):
    patrones = [
        r"(--|\b(SELECT|INSERT|DELETE|UPDATE|DROP|TRUNCATE|EXEC|UNION|OR|AND)\b)",
        r"[<>;]|(\*{2,})|['\"\\]"
    ]
    return any(re.search(patron, texto, re.IGNORECASE) for patron in patrones)
