#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yom import Model
from .base import AutoIdModel
from . import field_desc as fd

import asyncio


class ChatMessage(AutoIdModel):
    __table__ = "t_chat_message"

    id = fd.IntField(name='id', primary_key=True, auto_increment=True)
    user_id = fd.UserIDField(desc='用户ID')
    session_id = fd.SessionIdField(desc='会话ID')
    role = fd.RoleField(desc='角色')
    content = fd.TextField(name='content', size=4096, desc='消息内容')
    created_at = fd.CreatedAtField()

    @classmethod
    @asyncio.coroutine
    def find_by_session(cls, user_id, session_id, limit=50):
        sql = f"SELECT * FROM {cls.__table__} WHERE user_id=? AND session_id=? ORDER BY created_at ASC LIMIT ?"
        rows = yield from cls.select(sql, (user_id, session_id, limit))
        return [cls.row_mapper(r) for r in rows]

    @classmethod
    @asyncio.coroutine
    def delete_by_session(cls, user_id, session_id):
        sql = f"DELETE FROM {cls.__table__} WHERE user_id=? AND session_id=?"
        yield from cls.execute(sql, (user_id, session_id))
