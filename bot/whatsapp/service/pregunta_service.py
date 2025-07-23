from data.db import get_connection


def obtener_todas_las_preguntas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.pregunta, p.contexto, p.respuesta_rapida,
                       ARRAY_AGG(k.palabra) AS keywords
                FROM preguntas p
                LEFT JOIN pregunta_keyword pk ON p.id = pk.id_pregunta
                LEFT JOIN keywords k ON pk.id_keyword = k.id
                GROUP BY p.id
            """)
            return cur.fetchall()


def existe_pregunta_exacta(pregunta: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM preguntas WHERE pregunta = %s", (pregunta,))
            row = cur.fetchone()
            return row["id"] if row else None  # <-- ✅ por clave


def insertar_pregunta(pregunta: str, contexto: str, respuesta_rapida: str = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO preguntas (pregunta, contexto, respuesta_rapida)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (pregunta, contexto, respuesta_rapida))
            return cur.fetchone()["id"]  # <-- ✅ por clave


def insertar_pregunta_repetida(pregunta: str, id_pregunta_original: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO preguntas_repetidas (pregunta, id_pregunta_original)
                VALUES (%s, %s)
            """, (pregunta, id_pregunta_original))


def insertar_documento_si_no_existe(nombre: str, referencia: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM documentos WHERE nombre = %s AND referencia = %s
            """, (nombre, referencia))
            row = cur.fetchone()
            if row:
                return row["id"]  # <-- ✅ por clave

            cur.execute("""
                INSERT INTO documentos (nombre, referencia)
                VALUES (%s, %s)
                RETURNING id
            """, (nombre, referencia))
            return cur.fetchone()["id"]  # <-- ✅ por clave


def insertar_articulo_si_no_existe(nombre: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM articulos_o_paginas WHERE nombre = %s
            """, (nombre,))
            row = cur.fetchone()
            if row:
                return row["id"]  # <-- ✅ por clave

            cur.execute("""
                INSERT INTO articulos_o_paginas (nombre)
                VALUES (%s)
                RETURNING id
            """, (nombre,))
            return cur.fetchone()["id"]  # <-- ✅ por clave


def relacionar_documento_con_articulo(id_documento: int, id_articulo: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM documento_articulo
                WHERE id_documento = %s AND id_articulo = %s
            """, (id_documento, id_articulo))
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO documento_articulo (id_documento, id_articulo)
                    VALUES (%s, %s)
                """, (id_documento, id_articulo))


def relacionar_pregunta_con_documento(id_pregunta: int, id_documento: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM pregunta_documento
                WHERE id_pregunta = %s AND id_documento = %s
            """, (id_pregunta, id_documento))
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO pregunta_documento (id_pregunta, id_documento)
                    VALUES (%s, %s)
                """, (id_pregunta, id_documento))

def insertar_keyword_si_no_existe(palabra: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM keywords WHERE palabra = %s", (palabra,))
            row = cur.fetchone()
            if row:
                return row['id']
            cur.execute("INSERT INTO keywords (palabra) VALUES (%s) RETURNING id", (palabra,))
            return cur.fetchone()['id']


def relacionar_pregunta_con_keyword(id_pregunta: int, id_keyword: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM pregunta_keyword
                WHERE id_pregunta = %s AND id_keyword = %s
            """, (id_pregunta, id_keyword))
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO pregunta_keyword (id_pregunta, id_keyword)
                    VALUES (%s, %s)
                """, (id_pregunta, id_keyword))
