#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import os
import sys

__abs_file__ = os.path.abspath(__file__)
tool_dir = os.path.dirname(__abs_file__)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

import asyncio
from lib.yom import Pool
from www.dao.week_note import WeekNote

from utils.date_util import DateHelper

from tools.migrate.rake_migrate import RakeMigrate
import www.dao.field_desc as fd
import pymysql
from conf import db

from www.dao.base import Model


class WeekNoteRake(Model):
    __table__ = "t_week_note"

    note_id = fd.IntField(name='id', primary_key=True)
    user_id = fd.UserIDField(desc='用户id')
    user_name = fd.UserNameField()
    week_count = fd.WeekCountField()
    week_day = fd.WeekCountField(name='week_day', desc='Week Day')

    rec_date = fd.RegDateField(name='rec_date', desc='rec_date')
    # year = fd.IntField(name='year', desc='rec year')

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()


class WeekNoteRakeBK(WeekNoteRake):
    __table__ = "t_week_note_bk"

    note_id = fd.IntField(name='id', primary_key=True)
    user_id = fd.UserIDField(desc='用户id')
    user_name = fd.UserNameField()
    week_count = fd.WeekCountField()
    week_day = fd.WeekCountField(name='week_day', desc='Week Day')

    rec_date = fd.RegDateField(name='rec_date', desc='rec_date')
    # year = fd.IntField(name='year', desc='rec year')

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()

    @staticmethod
    def one_from_other(one, other):
        one.note_id = other.note_id
        one.user_id = other.user_id
        one.user_name = other.user_name
        one.week_count = other.week_count
        one.week_day = other.week_day
        one.rec_date = other.rec_date
        one.created_at = other.created_at
        one.updated_at = other.updated_at

        return one

    @classmethod
    def from_old(cls, old):
        one = cls()
        one = cls.one_from_other(one, old)

        return one


@asyncio.coroutine
def init_pool(loop):
    pool = yield from Pool.create_pool(loop=loop,
                                       host='127.0.0.1',
                                       port=3306,
                                       user='record',
                                       password='ww123456',
                                       db='record')

    return pool


@asyncio.coroutine
def handle_detail(week):
    year = DateHelper.to_date(week.rec_date).year

    nWeek = WeekNote()
    nWeek = WeekNoteRakeBK.one_from_other(nWeek, week)

    nWeek.year = year

    yield from nWeek.save()


class weekNoteRM(RakeMigrate):
    def __init__(self):
        super().__init__()
        self.db_conn = self._get_connection()

    def _get_connection(self):
        db_conn = pymysql.connect(host=db.rec_db.get('host'),
                                  user=db.rec_db.get('user'),
                                  password=db.rec_db.get('password'),
                                  database=db.rec_db.get('db'))
        return db_conn

    def create_bk(self):
        self.create_table('t_week_note_bk',
                          fd.IntField(name='id', primary_key=True),
                          fd.UserIDField(desc='用户id'), fd.UserNameField(),
                          fd.WeekCountField(),
                          fd.WeekCountField(name='week_day', desc='Week Day'),
                          fd.RegDateField(name='rec_date', desc='rec_date'),
                          fd.UpdatedAtField(), fd.CreatedAtField())

    def drop_bk(self):
        self.drop('t_week_note_bk')

    def up(self):
        self.create_table(
            't_week_note',
            fd.IntField(name='id', primary_key=True, auto_increment=True),
            fd.UserIDField(desc='用户id'), fd.UserNameField(),
            fd.WeekCountField(),
            fd.WeekCountField(name='week_day', desc='Week Day'),
            fd.RegDateField(name='rec_date', desc='rec_date'),
            fd.IntField(name='year', desc='rec year'), fd.UpdatedAtField(),
            fd.CreatedAtField())

    def down(self):
        self.drop('t_week_note')


def create_bk_table():
    note = weekNoteRM()
    try:
        note.drop_bk()
        note.create_bk()
    except Exception as e:
        print('create table error:', e)


def rake_table():
    note = weekNoteRM()

    note.down()
    note.up()


@asyncio.coroutine
def handler():
    weekNtRakes = yield from WeekNoteRake.find_all()

    # bk
    # create_bk_table()
    # for wnt in weekNtRakes:
    #     bk = WeekNoteRakeBK.from_old(wnt)
    #     yield from bk.save()

    # rake table
    rake_table()

    for wnt in weekNtRakes:
        yield from handle_detail(wnt)


@asyncio.coroutine
def start(loop):
    yield from init_pool(loop)
    yield from handler()


if __name__ == '__main__':
    __loop = asyncio.get_event_loop()
    __loop.run_until_complete(start(__loop))