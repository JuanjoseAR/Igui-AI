import re
import docx
from typing import Tuple
from io import BytesIO
from bot.whatsapp.respuestas_wpp import recargar_contexto
from bot.whatsapp.service import pregunta_service as ps
from data.db import get_connection


async def procesar_archivo_preguntas(contenido: bytes, filename: str, id_usuario: int) -> Tuple[bool, str]:
    errores = []

    try:
        entradas = []

        if filename.endswith(".txt"):
            texto = contenido.decode("utf-8")
        elif filename.endswith(".docx"):
            doc = docx.Document(BytesIO(contenido))
            texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        else:
            return False, "Formato no soportado. Usa .txt o .docx"

        bloques = re.split(r"(?=PREGUNTA:)", texto)

        for i, bloque in enumerate(bloques):
            if not bloque.strip():
                continue

            pregunta_match = re.search(r"PREGUNTA:\s*(.+)", bloque)
            contexto_match = re.search(r"CONTEXT:\s*(.*?)\nRESPUESTA_RAPIDA:", bloque, re.DOTALL)
            rapida_match = re.search(r"RESPUESTA_RAPIDA:\s*(.+)", bloque)
            keywords_match = re.search(r"KEYWORDS:\s*\[(.*?)\]", bloque, re.DOTALL)

            docs_match = re.findall(
                r"[•\-]\s*nombre:\s*(.+?)\s*referencia:\s*(.+?)\s*articulo:\s*(.+)", bloque, re.DOTALL
            )

            if not pregunta_match:
                errores.append(f"❌ Error en bloque #{i+1}: Falta 'PREGUNTA'\n{bloque.strip()[:100]}...\n")
                continue

            # Procesar keywords si existen
            keywords = []
            if keywords_match:
                raw_keywords = keywords_match.group(1)
                keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]

            entrada = {
                "pregunta": pregunta_match.group(1).strip(),
                "contexto": contexto_match.group(1).strip() if contexto_match else "",
                "respuesta_rapida": rapida_match.group(1).strip() if rapida_match else None,
                "keywords": keywords,
                "documentos": []
            }

            for doc in docs_match:
                if len(doc) != 3:
                    errores.append(f"❌ Documento mal formado en bloque #{i+1}: {doc}")
                    continue

                entrada["documentos"].append({
                    "nombre": doc[0].strip(),
                    "referencia": doc[1].strip(),
                    "articulo": doc[2].strip()
                })

            entradas.append(entrada)

        for entrada in entradas:
            pregunta = entrada["pregunta"]
            id_existente = ps.existe_pregunta_exacta(pregunta)

            if id_existente:
                ps.insertar_pregunta_repetida(pregunta, id_existente)
                continue

            id_pregunta = ps.insertar_pregunta(
                pregunta,
                entrada["contexto"],
                entrada.get("respuesta_rapida")
            )

            # Insertar keywords asociadas
            for palabra in entrada["keywords"]:
                id_keyword = ps.insertar_keyword_si_no_existe(palabra)
                ps.relacionar_pregunta_con_keyword(id_pregunta, id_keyword)

            for doc in entrada["documentos"]:
                id_doc = ps.insertar_documento_si_no_existe(doc["nombre"], doc["referencia"])
                id_art = ps.insertar_articulo_si_no_existe(doc["articulo"])
                ps.relacionar_documento_con_articulo(id_doc, id_art)
                ps.relacionar_pregunta_con_documento(id_pregunta, id_doc)

        recargar_contexto()
        return (True, "") if not errores else (False, "\n".join(errores))

    except Exception as e:
        return False, f"💥 Error inesperado:\n{e}"
