# worker_llm.py
import asyncio
import time
from bot.whatsapp.service.rendimiento_service import registrar_rendimiento
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from modelos.GPT_api import ModeloGPTAPI

cola_llm = asyncio.Queue()
modelo_llm = ModeloGPTAPI()

async def worker_llm():
    while True:
        user_id, mensaje_usuario, future = await cola_llm.get()
        inicio = time.time()
        try:
            texto_generado = modelo_llm.generar_respuesta(user_id, mensaje_usuario)
            duracion = round(time.time() - inicio, 2)
            user =obtener_usuario_por_id_celular(user_id)

            registrar_rendimiento(
                id_usuario=user["id"],
                pregunta_usuario=mensaje_usuario,
                respuesta_modelo=texto_generado,
                tiempo_respuesta=duracion,
                contexto=None,
                similitud=None,
                pregunta_mas_cercana=None
            )

            future.set_result(f"💡 {texto_generado}")
        except Exception as e:
            future.set_exception(e)
        finally:
            cola_llm.task_done()

async def iniciar_workers_llm(num_workers=5):
    for _ in range(num_workers):
        asyncio.create_task(worker_llm())

def contar_mensajes_en_cola(user_id: str) -> int:
    return sum(1 for item in cola_llm._queue if item[0] == user_id)
