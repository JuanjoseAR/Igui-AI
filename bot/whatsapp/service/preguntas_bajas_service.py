from data.db import get_connection

def registrar_pregunta_baja(id_usuario, pregunta):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO preguntas_bajas (id_usuario, pregunta)
                VALUES (%s, %s)
            """, (id_usuario, pregunta))
