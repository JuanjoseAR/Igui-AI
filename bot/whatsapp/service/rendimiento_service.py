from data.db import get_connection
from datetime import datetime
from bot.whatsapp.service.hora_colombia import zona_colombia

def registrar_rendimiento(
    id_usuario: int,
    pregunta_mas_cercana: str,
    contexto: str,
    similitud: float,
    pregunta_usuario: str,
    respuesta_modelo: str,
    tiempo_respuesta: float
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO rendimiento_modelo (
                    id_usuario,
                    pregunta_mas_cercana,
                    contexto,
                    similitud,
                    pregunta_usuario,
                    respuesta_modelo,
                    fecha_y_hora,
                    tiempo_respuesta
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                id_usuario,
                pregunta_mas_cercana,
                contexto,
                similitud,
                pregunta_usuario,
                respuesta_modelo,
                datetime.now(zona_colombia),
                tiempo_respuesta
            ))
