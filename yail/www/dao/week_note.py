from os import name
from lib.yom import Model

from . import field_desc as fd
from .base import AutoIdModel

import asyncio

import datetime


class WeekNote(AutoIdModel):
    __table__ = "t_week_note"



    note_id = fd.IntField(name='id', primary_key=True, auto_increment=True)
    user_id = fd.UserIDField(desc='用户id')
    user_name = fd.UserNameField()
    week_count = fd.WeekCountField()
    week_day = fd.WeekCountField(name='week_day', desc='Week Day')

    rec_date = fd.RegDateField(name='rec_date', desc='rec_date')
    year = fd.IntField(name='year', desc='rec year')

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()




class Detail(AutoIdModel):
    __table__ = "t_note_detail"
    detail_id = fd.IntField(name='id', primary_key=True, auto_increment=True)

    note_id = fd.IntField(name='note_id', desc='ref key note id')

    user_id = fd.UserIDField(desc='用户id')
    user_name = fd.UserNameField()

    rec_date = fd.RegDateField(name='rec_date', desc='rec_date')
    week_day = fd.WeekCountField(name='week_day', desc='Week Day')

    status = fd.StatusField(name='status', desc='status')
    desc = fd.NoteJobField(name='job')
    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()


    @classmethod
    @asyncio.coroutine
    def find_between(cls, user_id,start,end,status=fd.StatusField.STATUS_DONE):
        details = yield from cls.find_where('user_id = ? and status=? and rec_date between ? and ?',user_id,status, start,end)
        return details
