import json
from sentence_transformers import SentenceTransformer, util
from telegram import Update
from telegram.ext import ContextTypes
from config import RUTA_JSON_CONTEXTO, MAX_TOKENS
from modelos.modelo import ModeloMistral

modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')
modelo_llm = ModeloMistral()

# Carga el contexto
with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
    contexto = json.load(f)
    preguntas = [item['pregunta'] for item in contexto]
    respuestas = [item['respuesta'] for item in contexto]
    respuesta_rapida =[item['respuesta_rapida'] for item in contexto] 
    documentos = [item['documentos'] for item in contexto]
    embeddings = modelo_embedding.encode(preguntas, convert_to_tensor=True)

# Función principal para responder preguntas
async def responder_pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text
    embedding_usuario = modelo_embedding.encode(mensaje_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(embedding_usuario, embeddings)[0]
    indice_max = similitudes.argmax().item()
    score_max = similitudes[indice_max].item()
    print(f"🧠 Pregunta usuario: {mensaje_usuario}")
    print(f"🔎 Pregunta más cercana: {preguntas[indice_max]}")
    print(f"🎯 Similitud: {score_max}")
    
    if score_max >= 0.90:
        respuesta_rapida = contexto[indice_max].get("respuesta_rapida")
        await update.message.reply_text(f"🧠 {respuesta_rapida}")
        return

    # Score medio: enviar contexto al modelo
    elif 0.65 <= score_max < 0.90:
        respuesta = respuestas[indice_max]
        texto_generado = modelo_llm.generar_respuesta(mensaje_usuario, respuesta)
        await update.message.reply_text(f"💡 {texto_generado}")
    else:
        respuesta_saludo= "Vas a devolver un saludo si el usuario mando algun mensaje que corresponda a un saludo. Si el usuario no envio ningun saludo responde que no tienes respuesta para esa información, que reformule mejor su pregunta o si desea que se contacte con un representate a traves del comando /ayuda. Prioriza el comando /ayuda si no sabes la respuesta"
        texto = modelo_llm.generar_respuesta(mensaje_usuario, respuesta_saludo)
        await update.message.reply_text(f"💡 {texto}"
        )