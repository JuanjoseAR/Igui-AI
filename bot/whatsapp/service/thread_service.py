# thread_service.py
from datetime import date
from data.db import get_connection

def obtener_o_crear_thread(client, usuario_id: int) -> str:
    hoy = date.today()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT thread_id FROM threads
                WHERE usuario_id = %s AND fecha = %s
            """, (usuario_id, hoy))
            row = cur.fetchone()

            if row:
                return row["thread_id"]

            # si no existe, crear uno nuevo
            thread = client.beta.threads.create()
            thread_id = thread.id

            cur.execute("""
                INSERT INTO threads (usuario_id, fecha, thread_id)
                VALUES (%s, %s, %s)
            """, (usuario_id, hoy, thread_id))
            conn.commit()

            return thread_id
