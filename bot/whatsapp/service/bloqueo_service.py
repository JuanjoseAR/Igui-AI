from data.db import get_connection

def obtener_usuarios_bloqueados():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT numero_celular_id FROM usuarios_bloqueados")
            return set(row["numero_celular_id"] for row in cur.fetchall())

def bloquear_usuario(numero_celular_id: str, motivo: str, cantidad: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios_bloqueados (numero_celular_id, motivo_bloqueo, cantidad_mensajes)
                VALUES (%s, %s, %s)
                ON CONFLICT (numero_celular_id)
                DO UPDATE SET motivo_bloqueo = EXCLUDED.motivo_bloqueo,
                              cantidad_mensajes = EXCLUDED.cantidad_mensajes,
                              fecha_bloqueo = NOW();
            """, (numero_celular_id, motivo, cantidad))
