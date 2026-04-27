import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DB_CON_STR")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

SCHEMA = "maria"
DATABASE_URL = f"{DATABASE_URL}/{SCHEMA}"

