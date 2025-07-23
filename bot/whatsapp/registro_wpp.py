
# ---registro_wpp.py

from bot.whatsapp.service.usuario_service import obtener_usuario_por_id_celular, insertar_usuario


usuarios_en_memoria = {}  # user_id -> {"estado": ..., "registro": {...}}





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
            "📝 Por favor ingresa tu *nombre completo*:"
        )

    estado = usuario["estado"]

    if estado == "esperando_nombre":
        usuario["registro"]["nombre_completo"] = texto
        usuario["estado"] = "esperando_programa"
        return "🎓 Ingresa tu *programa académico*:"

    elif estado == "esperando_programa":
        usuario["registro"]["programa_que_pertenece"] = texto
        usuario["estado"] = "esperando_correo"
        return "📧 Ingresa tu *correo electrónico*:"

    elif estado == "esperando_correo":
        usuario["registro"]["correo_electronico"] = texto
        usuario["estado"] = "esperando_aceptacion"
        return (
            "🔐 *Políticas de Tratamiento de Datos:*\n\n"
            "Tu información será usada únicamente para fines académicos relacionados con el Movimiento Universitario Intercultural.\n\n"
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
