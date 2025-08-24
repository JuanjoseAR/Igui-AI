# servidor.py
from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel

app = FastAPI()

# Configuración PostgreSQL con tunel SSH (puedes usar paramiko o pgAdmin con túnel)
conn = psycopg2.connect(
    host="127.0.0.1",  # luego del túnel
    port="5432",
    database="qr",
    user="admin",
    password="Chatbot1234"
)

class QRRequest(BaseModel):
    codigo: str

@app.post("/usar_qr")
def usar_qr(data: QRRequest):
    cur = conn.cursor()
    cur.execute("SELECT usado FROM codigos WHERE codigo = %s", (data.codigo,))
    row = cur.fetchone()
    if not row:
        return {"status": "error", "msg": "Código no existe"}
    if row[0]:
        return {"status": "usado", "msg": "Código ya fue reclamado"}
    cur.execute("UPDATE codigos SET usado = TRUE WHERE codigo = %s", (data.codigo,))
    conn.commit()
    return {"status": "ok", "msg": "Código marcado como usado"}

@app.post("/salida_qr")
def salida_qr(data: QRRequest):
    cur = conn.cursor()
    cur.execute("SELECT usado FROM codigos WHERE codigo = %s", (data.codigo,))
    row = cur.fetchone()
    if not row:
        return {"status": "error", "msg": "Código no existe"}
    if not row[0]:
        return {"status": "error", "msg": "El código no estaba marcado"}
    cur.execute("UPDATE codigos SET usado = FALSE WHERE codigo = %s", (data.codigo,))
    conn.commit()
    return {"status": "ok", "msg": "Código liberado para volver a entrar"}
