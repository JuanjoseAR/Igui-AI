from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from config import TOKEN_TELEGRAM, RUTA_DOCUMENTOS, RUTA_JSON_CONTEXTO
from bot.telegram.registro import manejar_inicio, manejar_respuesta_mensaje, manejar_callback_politica
from bot.telegram.respuestas import responder_pregunta
import json, os


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manejar_inicio(update, context)

async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = context.user_data.get('estado_registro')
    
    if estado is None:
        await manejar_inicio(update, context)
    elif estado in ['esperando_nombre','esperando_programa', 'esperando_correo', 'esperando_aceptacion']:
        await manejar_respuesta_mensaje(update, context)
    elif estado is True:
        await responder_pregunta(update, context)
    else:
        await update.message.reply_text("⚠️ Algo salió mal. Escribe /start para comenzar de nuevo.")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manejar_callback_politica(update, context)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Si necesitas ayuda personalizada, puedes contactar a:\n- Juan Pérez: +57 3000000000\n- María Gómez: +57 3111111111\nTambién puedes escribirnos al correo: movimiento@unimagdalena.edu.co")

async def documentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(RUTA_JSON_CONTEXTO):
        await update.message.reply_text("❌ No se encontró el archivo de contexto.")
        return
    with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
        contexto = json.load(f)

    lista = []
    for item in contexto:
        for doc in item.get("documentos", []):
            if doc['nombre'] not in lista:
                lista.append(doc['nombre'])

    if not lista:
        await update.message.reply_text("📂 No hay documentos disponibles.")
        return

    botones = [[InlineKeyboardButton(nombre, callback_data=f"doc::{nombre}")] for nombre in lista]
    await update.message.reply_text("📚 Documentos disponibles:", reply_markup=InlineKeyboardMarkup(botones))

async def enviar_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("doc::"):
        nombre = data.split("::")[1]
        ruta = os.path.join(RUTA_DOCUMENTOS, nombre)
        print(f"📄 Intentando enviar: {ruta}")
        if os.path.exists(ruta):
            try:
                with open(ruta, 'rb') as archivo:
                    msg = await query.message.reply_text("📤 Enviando documento, por favor espera...")
                    await query.message.reply_document(
                        document=InputFile(archivo, filename=nombre),
                        caption=f"📄 {nombre}"
                    )
                    await msg.delete()
            except Exception as e:
                await query.message.reply_text(f"❌ Error al enviar el documento: {e}")
        else:
            await query.message.reply_text("⚠️ No se encontró el documento en el servidor.")

def iniciar_bot():
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("documentos", documentos))
    app.add_handler(CallbackQueryHandler(callback, pattern=r'^(acepto_politicas|no_acepto)$'))
    app.add_handler(CallbackQueryHandler(enviar_documento, pattern=r'^doc::'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    print("🤖 Bot iniciado")
    app.run_polling()
