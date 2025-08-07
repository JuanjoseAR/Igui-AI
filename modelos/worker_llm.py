# === archivo: worker_llm.py ===
import asyncio
import time
#from modelos.modelo import ModeloMistral
from bot.whatsapp.service.rendimiento_service import registrar_rendimiento
from modelos.GPT_api import ModeloGPTAPI


# Cola global para procesar peticiones LLM
cola_llm = asyncio.Queue()

# Instanciar una sola vez el modelo
modelo_llm = ModeloGPTAPI()

# === Worker ===
async def worker_llm():
    while True:
        user_id, mensaje_usuario, contexto_relacionado, fallback, future, similitud, pregunta_mas_cercana = await cola_llm.get()
        inicio = time.time()
        try:
            contexto_usado = contexto_relacionado or fallback
            texto_generado = modelo_llm.generar_respuesta(mensaje_usuario, contexto_usado)
            duracion = round(time.time() - inicio, 2)

            # ✅ Registrar con orden correcto
            registrar_rendimiento(
                id_usuario=user_id,
                pregunta_mas_cercana=pregunta_mas_cercana,
                contexto=contexto_usado,
                similitud=similitud,
                pregunta_usuario=mensaje_usuario,
                respuesta_modelo=texto_generado,
                tiempo_respuesta=duracion
            )

            future.set_result(f"💡 {texto_generado}")
        except Exception as e:
            future.set_exception(e)
        finally:
            cola_llm.task_done()

# === Arranque de los workers ===
async def iniciar_workers_llm(num_workers=2):
    for _ in range(num_workers):
        asyncio.create_task(worker_llm())

def contar_mensajes_en_cola(user_id: str) -> int:
    return sum(1 for item in cola_llm._queue if item[0] == user_id)

async def filtrar_mensajes_llm_por_usuario(user_id_bloqueado: str):
    nuevos_items = []
    eliminados = 0

    while not cola_llm.empty():
        item = await cola_llm.get()
        uid = item[0]  # user_id está en la posición 0 del item
        if uid != user_id_bloqueado:
            nuevos_items.append(item)
        else:
            eliminados += 1
        cola_llm.task_done()

    for item in nuevos_items:
        await cola_llm.put(item)

    print(f"🧹 Se eliminaron {eliminados} mensajes de {user_id_bloqueado} de la cola LLM.")
