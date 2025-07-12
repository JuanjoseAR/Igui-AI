import json
from data.db import get_connection
from config import RUTA_JSON_CONTEXTO

def migrar_contexto():
    with open(RUTA_JSON_CONTEXTO, encoding='utf-8') as f:
        contexto = json.load(f)

    with get_connection() as conn:
        with conn.cursor() as cur:
            for item in contexto:
                pregunta = item["pregunta"]
                contexto_txt = item["respuesta"]  # lo renombrarás como "contexto"
                respuesta_rapida = item.get("respuesta_rapida", None)

                # Insertar en preguntas
                cur.execute("""
                    INSERT INTO preguntas (pregunta, contexto, respuesta_rapida)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (pregunta, contexto_txt, respuesta_rapida))
                id_pregunta = cur.fetchone()["id"]

                for doc in item.get("documentos", []):
                    nombre = doc["nombre"]
                    referencia = doc["referencia"]
                    articulo = doc.get("articulo_o_pagina", None)

                    # Revisar si el documento ya existe
                    cur.execute("""
                        SELECT id FROM documentos WHERE nombre = %s AND referencia = %s
                    """, (nombre, referencia))
                    doc_existente = cur.fetchone()

                    if doc_existente:
                        id_doc = doc_existente["id"]
                    else:
                        cur.execute("""
                            INSERT INTO documentos (nombre, referencia, articulo_o_pagina)
                            VALUES (%s, %s, %s)
                            RETURNING id
                        """, (nombre, referencia, articulo))
                        id_doc = cur.fetchone()["id"]

                    # Insertar relación
                    cur.execute("""
                        INSERT INTO pregunta_documento (id_pregunta, id_documento)
                        VALUES (%s, %s)
                    """, (id_pregunta, id_doc))

        conn.commit()

if __name__ == "__main__":
    migrar_contexto()
