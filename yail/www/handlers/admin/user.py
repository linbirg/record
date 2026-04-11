#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import get, post, ResponseBody

from www.dao.user import User

from lib import logger
import hashlib


@get("/user/")
@ResponseBody
async def index():
    users = await User.find_all()
    return users


@post("/user/submitUser.json")
async def submit(userName, nickname, password):
    md_str = hashlib.md5(password.encode("utf8")).hexdigest()
    user = User(username=userName, nickname=nickname, password=md_str)
    logger.LOG_INFO("user:%s" % str(user))
    await user.save()

    return {"msg": "success", "isSuccess": True}


@get("/user/{userId}")
@ResponseBody
async def show_user(userId):
    if int(userId) == 0:
        users = await User.find_all()
        return users

    user = await User.find_one(user_id=userId)

    return user


@post("/user/{userId}/reset")
async def reset_passwd(userId, new_passwd):
    assert userId != 0

    user = await User.find_one(user_id=userId)

    md_str = hashlib.md5(new_passwd.encode("utf8")).hexdigest()
    user.password = md_str
    await user.update()

    return {"msg": "success", "isSuccess": True}
