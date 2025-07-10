import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import RUTA_JSON_USUARIOS

# Paso inicial: verificar si el usuario ya está registrado
async def manejar_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    usuarios = _cargar_usuarios()
    if user_id in usuarios:
        context.user_data['estado_registro'] = True
        await update.message.reply_text("✅ Usuario valido. Puedes comenzar a preguntar.")
    else:
        context.user_data['registro'] = {}
        context.user_data['estado_registro'] = 'esperando_nombre'
        await update.message.reply_text("👋 Bienvenido al asistente del Movimiento Universitario Intercultural de Unimagdalena.\n\n📝 Por favor ingresa tu *nombre completo*:")
      

# Paso final: aceptar o rechazar políticas
async def manejar_callback_politica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "acepto_politicas":
        datos = context.user_data.get('registro', {})
        if datos:
            datos["numero_celular_1"] = ""  # opcional a completar luego
            datos["numero_celular_2"] = user_id
            datos["aceptacion_de_politicas"] = True

            usuarios = _cargar_usuarios()
            usuarios[user_id] = datos
            with open(RUTA_JSON_USUARIOS, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, indent=2, ensure_ascii=False)

            context.user_data['estado_registro'] = True
            await query.edit_message_text("✅ Registro completado. Puedes hacer tu pregunta.")
        else:
            await query.edit_message_text("⚠️ Error: no se encontraron tus datos.")
    else:
        context.user_data.clear()
        await query.edit_message_text("🚫 No podrás usar el asistente si no aceptas las políticas.")

# Flujo de entrada de datos paso a paso
async def manejar_respuesta_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = context.user_data.get('estado_registro')
    texto = update.message.text.strip()
    user_id = str(update.effective_user.id)
    usuarios = _cargar_usuarios()
    if user_id in usuarios:
       context.user_data['estado_registro'] = True
       await update.message.reply_text("Verificando usuario.")
       await update.message.reply_text("✅ Usuario valido. Puedes comenzar a preguntar.")
       return
    if estado == 'esperando_nombre':
        context.user_data['registro'] = {'nombre_completo': texto}
        context.user_data['estado_registro'] = 'esperando_programa'
        await update.message.reply_text("🎓 Ingresa tu *programa académico*:")
        return

    if estado == 'esperando_programa':
        context.user_data['registro']['programa_que_pertenece'] = texto
        context.user_data['estado_registro'] = 'esperando_correo'
        await update.message.reply_text("📧 Ingresa tu *correo electrónico*:")
        return

    if estado == 'esperando_correo':
        context.user_data['registro']['correo_electronico'] = texto
        context.user_data['estado_registro'] = 'esperando_aceptacion'
        texto_politicas = (
            "🔐 *Políticas de Tratamiento de Datos:*\n\n"
            "Tu información será usada únicamente para fines académicos relacionados con el Movimiento Universitario Intercultural.\n\n"
            "¿Aceptas nuestras políticas?"
        )
        botones = [
            [InlineKeyboardButton("✅ Acepto", callback_data="acepto_politicas")],
            [InlineKeyboardButton("❌ No acepto", callback_data="no_acepto")]
        ]
        await update.message.reply_text(texto_politicas, reply_markup=InlineKeyboardMarkup(botones), parse_mode='Markdown')
        
        return

    # Si ya está registrado, responder normalmente
    if context.user_data.get('estado_registro') is True:
        await update.message.reply_text("✅ Ya estás registrado. Haz tu pregunta.")

def _cargar_usuarios():
    if not os.path.exists(RUTA_JSON_USUARIOS):
        return {}
    with open(RUTA_JSON_USUARIOS, encoding='utf-8') as f:
        return json.load(f)
