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


class week_note(RakeMigrate):
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.db_conn = self._get_connection()

    def up(self):
        self.create_table("""
            CREATE TABLE IF NOT EXISTS t_week_note (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_name TEXT,
                week_count TEXT,
                week_day TEXT,
                rec_date TEXT,
                year TEXT,
                updated_at TEXT,
                created_at TEXT
            )
        """)

    def down(self):
        self.drop("t_week_note")


if __name__ == "__main__":
    migration = week_note()
    migration.up()
    migration.close()
    print("Migration completed: 3_week_note.py")
