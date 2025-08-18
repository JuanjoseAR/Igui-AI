# ---registro_wpp.py

import re
from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular, insertar_usuario

usuarios_en_memoria = {}  # user_id -> {"estado": ..., "registro": {...}}

def es_texto_valido(texto: str) -> bool:
    """
    Valida que el texto solo contenga letras (incluyendo tildes) y espacios.
    """
    return bool(re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", texto))

async def manejar_mensaje_wpp(user_id: str, texto: str) -> str:
    texto = texto.strip()

    # Si ya está registrado
    if obtener_usuario_por_id_celular(user_id) is not None:
        usuarios_en_memoria[user_id] = {"estado": "registrado"}
        return "✅ Ya estás registrado. Puedes hacer tu pregunta."

    # Estado actual del usuario
    usuario = usuarios_en_memoria.get(user_id)

    if not usuario:
        usuarios_en_memoria[user_id] = {
            "estado": "esperando_nombre",
            "registro": {}
        }
        return (
            "👋 Bienvenido al asistente del Movimiento Universitario Intercultural de Unimagdalena.\n\n"
            "📝 Por favor ingresa tu *nombre completo* (solo letras y espacios):"
        )

    estado = usuario["estado"]

    if estado == "esperando_nombre":
        if not es_texto_valido(texto):
            return "❌ Nombre inválido. Usa solo letras y espacios, sin números ni caracteres especiales.\n\n📝 Ingresa tu *nombre completo*:"
        usuario["registro"]["nombre_completo"] = texto
        usuario["estado"] = "esperando_programa"
        return "🎓 Ingresa tu *programa académico* (solo letras y espacios):"

    elif estado == "esperando_programa":
        if not es_texto_valido(texto):
            return "❌ Programa inválido. Usa solo letras y espacios, sin números ni caracteres especiales.\n\n🎓 Ingresa tu *programa académico*:"
        usuario["registro"]["programa_que_pertenece"] = texto
        usuario["registro"]["correo_electronico"] = "N/A"
        usuario["estado"] = "esperando_aceptacion"
        return (
            "🔐 *Políticas de Tratamiento de Datos:*\n\n"
            "Tu información será usada únicamente para fines académicos relacionados con el Movimiento Universitario Intercultural.\n\n"
            "En este enlace puede accedera nuestras polícitas:\n\n"
            "https://docs.google.com/document/d/1hgwytGenfZzhH27jkm4yO51aa-V9Dzy9/edit?usp=share_link&ouid=105206836791597668068&rtpof=true&sd=true"
            "¿Aceptas nuestras políticas?\n\n"
            "1. ✅ Acepto\n"
            "2. ❌ No acepto"
        )

    elif estado == "esperando_aceptacion":
        if texto == "1":
            datos = usuario["registro"]
            datos["numero_celular_1"] = ""
            datos["numero_celular_id"] = user_id
            datos["aceptacion_de_politicas"] = True

            insertar_usuario(datos)

            usuarios_en_memoria[user_id]["estado"] = "registrado"
            return "✅ Registro completado. Puedes hacer tu pregunta."
        elif texto == "2":
            usuarios_en_memoria.pop(user_id)
            return "🚫 No podrás usar el asistente si no aceptas las políticas."
        else:
            return "❓ Opción inválida. Escribe:\n1 para aceptar\n2 para rechazar."

    elif estado == "registrado":
        return "✅ Ya estás registrado. Puedes hacer tu pregunta."

    return "⚠️ Algo salió mal. Escribe cualquier cosa para volver a comenzar."
