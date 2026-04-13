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


class note_risk(RakeMigrate):
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.db_conn = self._get_connection()

    def up(self):
        self.create_table("""
            CREATE TABLE IF NOT EXISTS note_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_name TEXT,
                reg_date TEXT,
                week_count TEXT,
                job TEXT,
                new_job TEXT,
                risk TEXT,
                risk_solve_time TEXT,
                updated_at TEXT,
                created_at TEXT
            )
        """)

    def down(self):
        self.drop("note_risk")


if __name__ == "__main__":
    migration = note_risk()
    migration.up()
    migration.close()
    print("Migration completed: 2_note_risk.py")
