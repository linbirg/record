from lib.yom import Model
from .base import AutoIdModel
from . import field_desc as fd

import asyncio

import datetime


class User(AutoIdModel):
    __table__ = "user"

    user_id = fd.UserIDField(primary_key=True, auto_increment=True)

    username = fd.UserNameField()
    nickname = fd.NickNameField()
    password = fd.PasswdField()
    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()
    # role_id = fd.RoleIDField()
    # group_name = fd.GroupNameField()
    # type_id = fd.TypeIDField()

    # @asyncio.coroutine
    # def save(self):
    #     sql = "insert into user (user_name,nickname,password,created_at,updated_at) values(%s,%s,%s,%s,%s)"

    #     self.created_at = datetime.datetime.now()
    #     self.updated_at = datetime.datetime.now()

    #     args = (self.username, self.nickname, self.password, self.created_at,
    #             self.updated_at)

    #     affected = yield from self.execute(sql, args)

    #     return affected
