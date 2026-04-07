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

from tools.migrate.rake_migrate import RakeMigrate
import pymysql
from conf import db
import www.dao.field_desc as fd


class chat_message(RakeMigrate):
    def __init__(self):
        super().__init__()
        self.db_conn = self._get_connection()

    def _get_connection(self):
        self.db_conn = pymysql.connect(
            host=db.rec_db.get('host'),
            user=db.rec_db.get('user'),
            password=db.rec_db.get('password'),
            database=db.rec_db.get('db'))
        return self.db_conn

    def up(self):
        self.create_table(
            't_chat_message',
            fd.IntField(name='id', primary_key=True, auto_increment=True),
            fd.UserIDField(desc='用户ID'),
            fd.SessionIdField(desc='会话ID'),
            fd.RoleField(desc='角色'),
            fd.TextField(name='content', size=4096, desc='消息内容'),
            fd.CreatedAtField()
        )
        self.execute("CREATE INDEX idx_user_session ON t_chat_message(user_id, session_id)")
        self.execute("CREATE INDEX idx_session_time ON t_chat_message(session_id, created_at)")

    def down(self):
        self.drop('t_chat_message')


if __name__ == '__main__':
    migration = chat_message()
    migration.up()
    print("Migration completed.")
