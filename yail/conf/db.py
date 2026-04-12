import os
from pathlib import Path

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

ROOT = "D:/project/linbirg/ww/ww/record/yail"
PIC_DIR = "D:/project/linbirg/ww/ww/record/frontEnd/static/car"
PIC_URL = "static/car"

rec_db = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "record",
    "password": "ww123456",
    "db": "record",
}

_sqlite_dir = Path(__file__).parent.parent
SQLITE_DB_PATH = str(_sqlite_dir / "app.db")
