from data.db import get_connection

def obtener_usuario_por_id_celular(id_celular):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE numero_celular_id = %s", (id_celular,))
            return cur.fetchone()

def insertar_usuario(data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (
                    numero_celular_id, nombre_completo, programa_que_pertenece,
                    correo_electronico, numero_celular_1, aceptacion_de_politicas
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["numero_celular_id"], data["nombre_completo"], data["programa_que_pertenece"],
                data["correo_electronico"], data["numero_celular_1"], data["aceptacion_de_politicas"]
            ))
            return cur.fetchone()["id"]
        
def es_usuario_admin(id_usuario: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT numero_celular_1 FROM usuarios WHERE id = %s", (id_usuario,))
            row = cur.fetchone()
            if row:
                return row["numero_celular_1"] == "1"
            return False
