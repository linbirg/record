#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr
# Rename tables: user→t_user, note_risk→t_note_risk

import sys, os

__abs_file__ = os.path.abspath(__file__)
mig_dir = os.path.dirname(__abs_file__)
tool_dir = os.path.dirname(mig_dir)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

from tools.migrate_sqlite.rake_sqlite_migrate import RakeMigrate


class rename_tables(RakeMigrate):
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.db_conn = self._get_connection()

    def up(self):
        self.execute("ALTER TABLE user RENAME TO t_user")
        self.execute("ALTER TABLE note_risk RENAME TO t_note_risk")

    def down(self):
        self.execute("ALTER TABLE t_user RENAME TO user")
        self.execute("ALTER TABLE t_note_risk RENAME TO note_risk")

    def close(self):
        if self.db_conn:
            self.db_conn.close()


if __name__ == "__main__":
    migration = rename_tables()
    migration.up()
    migration.close()
    print("Migration completed: 8_rename_tables.py")
