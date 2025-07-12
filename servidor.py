from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from bot.whatsapp.registro_wpp import manejar_mensaje_wpp
from bot.whatsapp.respuestas_wpp import responder_pregunta_wpp
from bot.whatsapp.documentos_wpp import listar_documentos_wpp, obtener_ruta_documento
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular
from bot.whatsapp.service.pqrs_service import insertar_pqrs
from modelos.worker_llm import iniciar_workers_llm

app = FastAPI()

context = type("Context", (), {})()
context.user_data = {}
usuarios_suspendidos = set()
pqrs_en_memoria = {}

class MensajeWhatsApp(BaseModel):
    id_usuario: str
    texto: str

@app.get("/")
def leer_inicio():
    return {"mensaje": "Servidor activo"}

@app.on_event("startup")
async def iniciar_workers():
    await iniciar_workers_llm(num_workers=2)  # puedes subir a 4 si quieres
    
@app.post("/webhook")
async def recibir_mensaje(mensaje: MensajeWhatsApp):
    user_id = mensaje.id_usuario.strip()
    texto = mensaje.texto.strip()

    # Atención humana
    if user_id in usuarios_suspendidos and texto.lower() != "/activar":
        await asyncio.sleep(2)
        return {"respuesta": None}

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
        respuesta = await responder_pregunta_wpp(user_id, mensaje_usuario=texto)

    return {"respuesta": respuesta}
