import os
import json
from config import RUTA_JSON_CONTEXTO, RUTA_DOCUMENTOS

# Lista los documentos disponibles
def listar_documentos_wpp():
    if not os.path.exists(RUTA_JSON_CONTEXTO):
        return "❌ No se encontró el archivo de contexto."

    with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
        contexto = json.load(f)

    lista = []
    for item in contexto:
        for doc in item.get("documentos", []):
            if doc["nombre"] not in lista:
                lista.append(doc["nombre"])

    if not lista:
        return "📂 No hay documentos disponibles."

    texto = "📚 *Documentos disponibles:*\n"
    for i, nombre in enumerate(lista, start=1):
        texto += f"{i}. {nombre}\n"

    texto += "\nEscribe el *número* o el *nombre exacto* del documento que deseas recibir."
    return texto, lista

# Devuelve la ruta de un documento si existe
def obtener_ruta_documento(nombre):
    ruta = os.path.join(RUTA_DOCUMENTOS, nombre)
    return ruta if os.path.exists(ruta) else None
