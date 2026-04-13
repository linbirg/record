from lib import Model
from .base import AutoIdModel
from . import field_desc as fd
from conf.db import DB_TYPE

import datetime


class User(AutoIdModel):
    __table__ = "user" if DB_TYPE == "mysql" else "t_user"

    user_id = fd.UserIDField(primary_key=True, auto_increment=True)

    username = fd.UserNameField()
    nickname = fd.NickNameField()
    password = fd.PasswdField()
    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()
