#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author:linbirg

from www.common.vo import ViewObj
from www.dao.field_desc import StatusField


class VoWeekNote(ViewObj):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_model(cls, model):
        vo = cls()
        vo.id = model.note_id

        vo.userId = model.user_id
        vo.userName = model.user_name

        vo.weekCount = model.week_count
        vo.weekDay = model.week_day
        vo.details = []

        return vo

    @classmethod
    def from_other(cls, other):
        vo = cls()
        # vo.id = other.id

        vo.userId = other.userId
        vo.userName = other.userName

        vo.weekCount = other.weekCount
        vo.weekDay = other.weekDay
        # details 置空，只复制基础属性
        vo.details = []

        return vo


class VoWeekDetail(ViewObj):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_model(cls, model):
        vo = cls()
        vo.no = model.detail_id

        vo.noteId = model.note_id
        vo.userId = model.user_id
        vo.userName = model.user_name
        vo.weekDay = model.week_day
        vo.completed = True if model.status == StatusField.STATUS_DONE else False
        vo.desc = model.desc

        return vo
