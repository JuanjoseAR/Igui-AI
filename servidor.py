from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

from bot.whatsapp.registro_wpp import manejar_mensaje_wpp
from bot.whatsapp.respuestas_wpp import responder_pregunta_wpp
from config import RUTA_JSON_USUARIOS
from bot.whatsapp.documentos_wpp import listar_documentos_wpp, obtener_ruta_documento
import asyncio  # Asegúrate de tenerlo importado



app = FastAPI()
context = type("Context", (), {})()
context.user_data = {}
class MensajeWhatsApp(BaseModel):
    id_usuario: str
    texto: str

# Diccionario para usuarios en modo "atención humana"
usuarios_suspendidos = set()

# Verificación si el usuario ya está registrado
def usuario_esta_registrado(user_id: str) -> bool:
    if not os.path.exists(RUTA_JSON_USUARIOS):
        return False
    with open(RUTA_JSON_USUARIOS, encoding='utf-8') as f:
        usuarios = json.load(f)
    return user_id in usuarios

@app.get("/")
def leer_inicio():
    return {"mensaje": "Servidor activo"}

@app.post("/webhook")
async def recibir_mensaje(mensaje: MensajeWhatsApp):
    user_id = mensaje.id_usuario
    texto = mensaje.texto.strip()

    # 👉 Usuario está en modo atención humana
    if user_id in usuarios_suspendidos and texto.lower() != "/activar":
        await asyncio.sleep(2)
        return {"respuesta": None}  # No responder nada

    # 👉 Comando /ayuda
    if texto.lower() == "/ayuda":
        usuarios_suspendidos.add(user_id)
        await asyncio.sleep(2)
        return {
            "respuesta": (
                "🤖 Has solicitado atención con un representante humano.\n Por favor espere unos minutos\n\n"
                "🛑 El bot ha sido suspendido temporalmente.\n\n"
                "📞 Contacta a:\n"
                "- Juan Pérez: +57 3000000000\n"
                "- María Gómez: +57 3111111111\n"
                "Cuando quieras reactivar el bot, escribe /activar."
            )
        }

    # 👉 Comando /activar
    if texto.lower() == "/activar":
        await asyncio.sleep(2)
        if user_id in usuarios_suspendidos:
            usuarios_suspendidos.remove(user_id)
            return {"respuesta": "✅ El bot ha sido reactivado. Ya puedes continuar preguntando."}
        else:
            return {"respuesta": "🤖 El bot ya está activo para ti. Puedes hacer preguntas."}
    # 👉 Comando /documentos
    if texto.lower() == "/documentos":
        await asyncio.sleep(2)
        resultado = listar_documentos_wpp()
        if isinstance(resultado, str):
            return {"respuesta": resultado}
        
        respuesta, lista_documentos = resultado
        context.user_data[user_id] = {"estado": "esperando_documento", "lista": lista_documentos}
        return {"respuesta": respuesta}

    # 👉 Si está esperando que el usuario elija un documento
    estado_usuario = context.user_data.get(user_id, {})
    if estado_usuario.get("estado") == "esperando_documento":
        await asyncio.sleep(2)
        lista = estado_usuario.get("lista", [])

        # Opción por número
        if texto.isdigit():
            indice = int(texto) - 1
            if 0 <= indice < len(lista):
                nombre = lista[indice]
            else:
                await asyncio.sleep(2)
                return {"respuesta": "⚠️ Número inválido. Intenta de nuevo."}
        else:
            await asyncio.sleep(2)
            # Opción por nombre
            nombre = texto.strip()
            if nombre not in lista:
                return {"respuesta": "⚠️ Nombre inválido. Intenta de nuevo."}

        ruta = obtener_ruta_documento(nombre)
        if ruta:
            await asyncio.sleep(2)
            context.user_data.pop(user_id)  # limpiar estado
            return {"respuesta": f"📄 Aquí tienes el documento: {nombre}", "documento": ruta}
        else:
            await asyncio.sleep(2)
            return {"respuesta": "❌ El documento no fue encontrado en el servidor."}

    # 👉 Usuario sin registrar: continuar flujo de registro
    if not usuario_esta_registrado(user_id):
        await asyncio.sleep(2)
        respuesta = await manejar_mensaje_wpp(user_id, texto)
    else:
        respuesta = await responder_pregunta_wpp(texto)

    return {"respuesta": respuesta}
