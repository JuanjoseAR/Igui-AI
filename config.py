import os

try:
    from env import (
        DB_HOST_env, DB_NAME_env, DB_PASWORD_env, DB_USER_env, MODELO_GPT_env, ASSISTANT_ID_env
    )
except ImportError:
    DB_HOST_env = DB_NAME_env = DB_PASWORD_env = DB_USER_env = MODELO_GPT_env = ASSISTANT_ID_env= None

DB_NAME = os.getenv("DB_NAME", DB_NAME_env)
DB_USER = os.getenv("DB_USER", DB_USER_env)
DB_PASWORD = os.getenv("DB_PASSWORD", DB_PASWORD_env)
DB_HOST = os.getenv("DB_HOST", DB_HOST_env) 
MODELO_GPT = os.getenv("MODELO_GPT", MODELO_GPT_env)
ASSISTANT_ID = os.getenv("ASSISTANT_ID", ASSISTANT_ID_env)
