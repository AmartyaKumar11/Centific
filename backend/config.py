import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_URL = os.getenv("DB_CON_STR", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
SCHEMA = "defaultdb"
DATABASE_URL = f"{DB_URL}/{SCHEMA}"
