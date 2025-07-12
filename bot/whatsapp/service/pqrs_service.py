from data.db import get_connection

def insertar_pqrs(id_usuario, tipo, descripcion):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pqrs (id_usuario, tipo, descripcion)
                VALUES (%s, %s, %s)
            """, (id_usuario, tipo, descripcion))

def actualizar_estado_pqrs(id_pqrs, estado):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pqrs SET estado = %s WHERE id = %s
            """, (estado, id_pqrs))
