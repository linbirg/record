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


class user(RakeMigrate):
    def __init__(self):
        super().__init__()
        self.db_conn = self._get_connection()

    def _get_connection(self):
        self.db_conn = pymysql.connect(host=db.rec_db.get('host'),
                                       user=db.rec_db.get('user'),
                                       password=db.rec_db.get('password'),
                                       database=db.rec_db.get('db'))

        return self.db_conn

    def up(self):
        self.create_table(
            'user', fd.UserIDField(primary_key=True, auto_increment=True),
            fd.UserNameField(unique=True), fd.NickNameField(),
            fd.PasswdField(), fd.UpdatedAtField(), fd.CreatedAtField())

    def down(self):
        self.drop('user')
