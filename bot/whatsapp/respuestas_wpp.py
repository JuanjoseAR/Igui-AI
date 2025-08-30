# respuesta_wpp.py
import re
import asyncio
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from modelos.worker_llm import cola_llm

async def responder_pregunta_wpp(user_id: str, mensaje_usuario: str) -> str:
    if es_input_malicioso(mensaje_usuario):
        return "⚠️ Tu mensaje contiene caracteres no permitidos. Reformúlalo sin símbolos especiales ni comandos."

    usuario = obtener_usuario_por_id_celular(user_id)
    if not usuario:
        return "⚠️ Usuario no registrado. Usa /ayuda para contactar con un representante."

    # enviar a la cola del worker
    future = asyncio.get_event_loop().create_future()
    await cola_llm.put((usuario["id"], mensaje_usuario, future))
    return await future

def es_input_malicioso(texto: str) -> bool:
    patrones = [
        r"(--|\b(SELECT|INSERT|DELETE|UPDATE|DROP|TRUNCATE|EXEC|UNION|OR|AND)\b)",
        r"[<>;]|(\*{2,})|['\"\\]"
    ]
    return any(re.search(patron, texto, re.IGNORECASE) for patron in patrones)
