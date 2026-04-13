#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import os
import sys
import sqlite3

__abs_file__ = os.path.abspath(__file__)
mig_dir = os.path.dirname(__abs_file__)
tool_dir = os.path.dirname(mig_dir)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

from tools.migrate_sqlite.rake_sqlite_migrate import RakeMigrate

import hashlib
from datetime import datetime


class user(RakeMigrate):
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.db_conn = self._get_connection()

    def up(self):
        self.create_table("""
            CREATE TABLE IF NOT EXISTS user (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE,
                nickname TEXT,
                password TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        now = datetime.now().isoformat()
        pwd = hashlib.md5("admin".encode("utf8")).hexdigest()
        self.execute(
            "INSERT INTO user (user_name, nickname, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin", pwd, now, now),
        )
        pwd2 = hashlib.md5("123456".encode("utf8")).hexdigest()
        self.execute(
            "INSERT INTO user (user_name, nickname, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("linbirg", "linbirg", pwd2, now, now),
        )

    def down(self):
        self.drop("user")


if __name__ == "__main__":
    migration = user()
    migration.up()
    migration.close()
    print("Migration completed: 1_user.py")
