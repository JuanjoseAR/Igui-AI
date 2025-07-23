import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_NAME, DB_PASWORD, DB_USER

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASWORD,
        host='localhost',
        port='5432',
        cursor_factory=RealDictCursor
    )
