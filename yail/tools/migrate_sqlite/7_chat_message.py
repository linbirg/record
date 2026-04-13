#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import os
import sys

__abs_file__ = os.path.abspath(__file__)
mig_dir = os.path.dirname(__abs_file__)
tool_dir = os.path.dirname(mig_dir)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

from tools.migrate_sqlite.rake_sqlite_migrate import RakeMigrate


class chat_message(RakeMigrate):
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.db_conn = self._get_connection()

    def up(self):
        self.create_table("""
            CREATE TABLE IF NOT EXISTS t_chat_message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT
            )
        """)
        self.create_index("idx_user_session", "t_chat_message", "user_id, session_id")
        self.create_index(
            "idx_session_time", "t_chat_message", "session_id, created_at"
        )

    def down(self):
        self.drop("t_chat_message")


if __name__ == "__main__":
    migration = chat_message()
    migration.up()
    migration.close()
    print("Migration completed: 7_chat_message.py")
