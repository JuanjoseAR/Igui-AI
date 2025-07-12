import re
import docx
from typing import Tuple
from io import BytesIO
from bot.whatsapp.respuestas_wpp import recargar_contexto
from bot.whatsapp.service import pregunta_service as ps


async def procesar_archivo_preguntas(contenido: bytes, filename: str, id_usuario: int) -> Tuple[bool, str]:
    errores = []

    try:
        entradas = []

        if filename.endswith(".txt"):
            texto = contenido.decode("utf-8")
        elif filename.endswith(".docx"):
            doc = docx.Document(BytesIO(contenido))
            texto = "\n".join([p.text for p in doc.paragraphs])
        else:
            return False, "Formato no soportado. Usa .txt o .docx"

        bloques = re.split(r"-{3,}", texto)

        for i, bloque in enumerate(bloques):
            if not bloque.strip():
                continue

            

            pregunta_match = re.search(r"PREGUNTA:\s*(.+)", bloque)
            contexto_match = re.search(r"CONTEXT:\s*(.+)", bloque, re.DOTALL)
            rapida_match = re.search(r"RESPUESTA_RAPIDA:\s*(.+)", bloque)
            docs_match = re.findall(r"- nombre:\s*(.+?)\n\s*referencia:\s*(.+?)\n\s*articulo:\s*(.+)", bloque)

            if not pregunta_match or not contexto_match:
                errores.append(f"❌ Error en bloque #{i+1}: Falta 'PREGUNTA' o 'CONTEXT'\n{bloque.strip()[:100]}...\n")
                continue

            entrada = {
                "pregunta": pregunta_match.group(1).strip(),
                "contexto": contexto_match.group(1).strip(),
                "respuesta_rapida": rapida_match.group(1).strip() if rapida_match else None,
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

            for doc in entrada["documentos"]:
                
                id_doc = ps.insertar_documento_si_no_existe(doc["nombre"], doc["referencia"])
                id_art = ps.insertar_articulo_si_no_existe(doc["articulo"])
                ps.relacionar_documento_con_articulo(id_doc, id_art)
                ps.relacionar_pregunta_con_documento(id_pregunta, id_doc)

        return (True, "") if not errores else (False, "\n".join(errores))

    except Exception as e:
        return False, f"💥 Error inesperado:\n{e}"

recargar_contexto()
