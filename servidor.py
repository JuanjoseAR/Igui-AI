# ---servidor.py
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import asyncio

from bot.whatsapp.registro_wpp import manejar_mensaje_wpp
from bot.whatsapp.respuestas_wpp import responder_pregunta_wpp
from bot.whatsapp.documentos_wpp import listar_documentos_wpp, obtener_ruta_documento
from bot.whatsapp.service.bloqueo_service import bloquear_usuario, obtener_usuarios_bloqueados
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular, es_usuario_admin
from bot.whatsapp.service.pqrs_service import insertar_pqrs
from modelos.worker_llm import contar_mensajes_en_cola, iniciar_workers_llm
from bot.whatsapp.service.archivos_preguntas import procesar_archivo_preguntas

app = FastAPI()

context = type("Context", (), {})()
context.user_data = {}
usuarios_suspendidos = set()
pqrs_en_memoria = {}
usuarios_bloqueados = set()

class MensajeWhatsApp(BaseModel):
    id_usuario: str
    texto: str

@app.get("/")
def leer_inicio():
    return {"mensaje": "Servidor activo"}

@app.on_event("startup")
async def iniciar_workers():
    await iniciar_workers_llm(num_workers=2)  # puedes subir a 4 si quieres
    usuarios_bloqueados.update(obtener_usuarios_bloqueados())
    asyncio.create_task(actualizar_bloqueados_periodicamente())
    
@app.post("/webhook")
async def recibir_mensaje(mensaje: MensajeWhatsApp):
    user_id = mensaje.id_usuario.strip()
    texto = mensaje.texto.strip()

    # Atención humana
    if user_id in usuarios_suspendidos and texto.lower() != "/activar":
        await asyncio.sleep(2)
        return {"respuesta": None}
    if user_id in usuarios_bloqueados:
        await asyncio.sleep(2)
        return None

    if texto.lower() == "/ayuda":
        usuarios_suspendidos.add(user_id)
        await asyncio.sleep(2)
        return {
            "respuesta": (
                "🤖 Has solicitado atención con un representante humano.\n"
                "🛑 El bot ha sido suspendido temporalmente.\n\n"
                "📞 Contacta a:\n"
                "- Juan Pérez: +57 3000000000\n"
                "- María Gómez: +57 3111111111\n"
                "Cuando quieras reactivar el bot, escribe /activar."
            )
        }

    if texto.lower() == "/activar":
        if user_id in usuarios_suspendidos:
            usuarios_suspendidos.remove(user_id)
            await asyncio.sleep(2)
            return {"respuesta": "✅ El bot ha sido reactivado. Ya puedes continuar preguntando."}
        return {"respuesta": "🤖 El bot ya está activo para ti. Puedes hacer preguntas."}

    if texto.lower() == "/documentos":
        await asyncio.sleep(2)
        resultado = listar_documentos_wpp()
        if isinstance(resultado, str):
            return {"respuesta": resultado}
        
        respuesta, lista_documentos = resultado
        context.user_data[user_id] = {"estado": "esperando_documento", "lista": lista_documentos}
        return {"respuesta": respuesta}

    estado_usuario = context.user_data.get(user_id, {})
    if estado_usuario.get("estado") == "esperando_documento":
        lista = estado_usuario.get("lista", [])
        nombre = ""

        if texto.isdigit():
            indice = int(texto) - 1
            if 0 <= indice < len(lista):
                nombre = lista[indice]
            else:
                await asyncio.sleep(2)
                return {"respuesta": "⚠️ Número inválido. Intenta de nuevo."}
        else:
            nombre = texto.strip()
            if nombre not in lista:
                await asyncio.sleep(2)
                return {"respuesta": "⚠️ Nombre inválido. Intenta de nuevo."}

        ruta = obtener_ruta_documento(nombre)
        context.user_data.pop(user_id, None)
        if ruta:
            await asyncio.sleep(2)
            return {"respuesta": f"📄 Aquí tienes el documento: {nombre}", "documento": ruta}
        await asyncio.sleep(2)
        return {"respuesta": "❌ El documento no fue encontrado en el servidor."}

    # 👉 Iniciar flujo PQRS
    if texto.lower() == "/pqrs":
        await asyncio.sleep(2)
        pqrs_en_memoria[user_id] = {
            "estado": "esperando_tipo"
        }
        return {"respuesta": "📌 Ingresa el *tipo* de PQRS (Petición, Queja, Reclamo o Sugerencia):"}

    # 👉 Manejo del flujo PQRS paso a paso
    if user_id in pqrs_en_memoria:
        pqrs_actual = pqrs_en_memoria[user_id]
        estado = pqrs_actual["estado"]

        if estado == "esperando_tipo":
            pqrs_actual["tipo"] = texto
            pqrs_actual["estado"] = "esperando_descripcion"
            await asyncio.sleep(2)
            return {"respuesta": "📝 Escribe la *descripción* de tu PQRS:"}

        elif estado == "esperando_descripcion":
            pqrs_actual["descripcion"] = texto
            pqrs_actual["estado"] = "esperando_confirmacion"
            await asyncio.sleep(2)
            return {
                "respuesta": (
                    "📤 ¿Qué deseas hacer con tu PQRS?\n"
                    "1. Enviar\n"
                    "2. Editar descripción\n"
                    "3. Cancelar"
                )
            }

        elif estado == "esperando_confirmacion":
            if texto == "1":
                usuario_bd = obtener_usuario_por_id_celular(user_id)
                if usuario_bd:
                    insertar_pqrs(
                        id_usuario=usuario_bd["id"],
                        tipo=pqrs_actual["tipo"],
                        descripcion=pqrs_actual["descripcion"]
                    )
                    pqrs_en_memoria.pop(user_id)
                    await asyncio.sleep(2)
                    return {"respuesta": "✅ Tu PQRS ha sido enviada correctamente."}
                else:
                    pqrs_en_memoria.pop(user_id)
                    await asyncio.sleep(2)
                    return {"respuesta": "❌ No estás registrado. Debes registrarte antes de enviar PQRS."}

            elif texto == "2":
                pqrs_actual["estado"] = "esperando_descripcion"
                await asyncio.sleep(2)
                return {"respuesta": "✏️ Por favor, escribe nuevamente la *descripción* de tu PQRS:"}

            elif texto == "3":
                pqrs_en_memoria.pop(user_id)
                await asyncio.sleep(2)
                return {"respuesta": "🚫 PQRS cancelada."}
            else:
                await asyncio.sleep(2)
                return {"respuesta": "❓ Opción inválida. Escribe:\n1 para enviar\n2 para editar\n3 para cancelar."}

    # 👉 Consultar o registrar usuario
    usuario_bd = obtener_usuario_por_id_celular(user_id)
    if not usuario_bd:
        await asyncio.sleep(2)
        respuesta = await manejar_mensaje_wpp(user_id, texto)
    else:
        en_cola = contar_mensajes_en_cola(user_id)
        if en_cola >= 4:
            bloquear_usuario(user_id, motivo="llm", cantidad=en_cola + 1)
            usuarios_bloqueados.add(user_id)
            return "🚫 Has sido bloqueado por enviar demasiados mensajes seguidos. Escribe /ayuda si crees que fue un error."
        respuesta = await responder_pregunta_wpp(user_id, mensaje_usuario=texto)

    return {"respuesta": respuesta}

@app.post("/cargar-preguntas")
async def cargar_preguntas(id_usuario: str = Form(...), archivo: UploadFile = File(...)):
    usuario_bd = obtener_usuario_por_id_celular(id_usuario)
    
    if not usuario_bd or not es_usuario_admin(usuario_bd["id"]):
        await asyncio.sleep(2)
        return {"respuesta": "🚫 No estás autorizado para subir preguntas."}

    contenido = await archivo.read()
    exito, errores = await procesar_archivo_preguntas(contenido, archivo.filename, usuario_bd["id"])

    if exito:
        await asyncio.sleep(2)
        return {"respuesta": "✅ Preguntas procesadas correctamente."}
    else:
        await asyncio.sleep(2)
        return {"respuesta": f"⚠️ Algunas preguntas no se pudieron guardar:\n{errores}"}

async def actualizar_bloqueados_periodicamente():
    while True:
        usuarios_bloqueados.clear()
        usuarios_bloqueados.update(obtener_usuarios_bloqueados())
        await asyncio.sleep(300)  # 5 minutos
