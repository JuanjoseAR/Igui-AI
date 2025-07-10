import json, os
from config import RUTA_JSON_USUARIOS

usuarios_en_memoria = {}  # user_id -> {"estado": ..., "registro": {...}}

def _cargar_usuarios():
    if not os.path.exists(RUTA_JSON_USUARIOS):
        return {}
    with open(RUTA_JSON_USUARIOS, encoding='utf-8') as f:
        return json.load(f)

def _guardar_usuarios(data):
    with open(RUTA_JSON_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def manejar_mensaje_wpp(user_id: str, texto: str) -> str:
    texto = texto.strip()
    usuarios_registrados = _cargar_usuarios()

    # Si ya está registrado
    if user_id in usuarios_registrados:
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
            datos["numero_celular_2"] = user_id
            datos["aceptacion_de_politicas"] = True

            usuarios_registrados[user_id] = datos
            _guardar_usuarios(usuarios_registrados)

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
