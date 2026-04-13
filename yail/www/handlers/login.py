#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author:linbirg

from lib.yeab.web import post, ResponseBody
from www.dao.user import User
import hashlib
from lib import logger


@post("/login.action")
@ResponseBody
async def login(userName, password, request):
    md_str = hashlib.md5(password.encode("utf8")).hexdigest()
    one = await User.find_one(username=userName)
    assert one

    if md_str == one.password:
        session = await request.get_session()
        session["user"] = one
        return {"userId": one.user_id, "username": one.username, "typeid": 1}

    return None
