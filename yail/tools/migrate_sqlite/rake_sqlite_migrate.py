#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import sys
import os
import sqlite3

__abs_file__ = os.path.abspath(__file__)
mig_dir = os.path.dirname(__abs_file__)
tool_dir = os.path.dirname(mig_dir)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

from lib import logger


class RakeMigrate:
    def __init__(self, db_path=None):
        self.db_conn = None
        self.db_path = db_path or os.path.join(code_dir, "app.db")

    def _get_connection(self):
        self.db_conn = sqlite3.connect(self.db_path)
        return self.db_conn

    def execute(self, sql, args=None):
        try:
            cur = self.db_conn.cursor()
            if args is None:
                args = ()
            logger.LOG_TRACE("execute sql:%s args:%s", sql, args)
            cur.execute(sql, args)
            self.db_conn.commit()
            affected = cur.rowcount
            cur.close()
        except BaseException as e:
            raise e
        return affected

    def create_table(self, sql):
        self.execute(sql)

    def drop(self, table):
        try:
            __ddl_drop_table__ = "DROP TABLE IF EXISTS %s" % table
            self.execute(__ddl_drop_table__)
        except Exception as e:
            print("drop table error:", e)
            logger.LOG_FATAL("drop table error:%s" % str(e))

    def rename_table(self, old_name, new_name):
        __ddl_rename = "ALTER TABLE %s RENAME TO %s" % (old_name, new_name)
        self.execute(__ddl_rename)

    def add_column(self, table, column_def):
        __ddl_add_column__ = "ALTER TABLE %s ADD COLUMN %s" % (table, column_def)
        self.execute(__ddl_add_column__)

    def rename_column(self, table, old_col_name, new_col_name):
        __ddl_rename_col__ = "ALTER TABLE %s RENAME COLUMN %s TO %s" % (
            table,
            old_col_name,
            new_col_name,
        )
        self.execute(__ddl_rename_col__)

    def create_index(self, index_name, table, columns):
        __ddl_create_index__ = "CREATE INDEX IF NOT EXISTS %s ON %s(%s)" % (
            index_name,
            table,
            columns,
        )
        self.execute(__ddl_create_index__)

    def close(self):
        if self.db_conn:
            self.db_conn.close()


def run_migrations(db_path=None):
    import tools.migrate_sqlite as mig

    mig_dir = os.path.dirname(mig.__file__)

    migration_files = [
        ("1_user", "user"),
        ("2_note_risk", "note_risk"),
        ("3_week_note", "week_note"),
        ("4_t_note_detail", "t_note_detail"),
        ("5_t_car_info", "car_info"),
        ("6_t_car_pics", "car_pics"),
        ("7_chat_message", "chat_message"),
        ("8_rename_tables", "rename_tables"),
    ]

    for file_name, class_name in migration_files:
        mod_name = "tools.migrate_sqlite.%s" % file_name
        mod = __import__(mod_name, fromlist=[file_name])
        cls = getattr(mod, class_name)
        migration = cls(db_path)
        logger.LOG_INFO("running migration: %s", file_name)
        migration.up()
        logger.LOG_INFO("migration completed: %s", file_name)
