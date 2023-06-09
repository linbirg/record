#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import get, post, ResponseBody

from www.dao.user import User

from lib import logger
import asyncio
import hashlib


@get('/user/')
@asyncio.coroutine
@ResponseBody
def index():
    users = yield from User.find_all()
    return users


@post('/user/submitUser.json')
@asyncio.coroutine
def submit(userName, nickname, password):
    md_str = hashlib.md5(password.encode("utf8")).hexdigest()
    user = User(username=userName, nickname=nickname, password=md_str)
    logger.LOG_INFO('user:%s' % str(user))
    yield from user.save()

    return {'msg': 'success', 'isSuccess': True}


@get('/user/{userId}')
@asyncio.coroutine
@ResponseBody
def show_user(userId):
    if int(userId) == 0:
        users = yield from User.find_all()
        return users

    user = yield from User.find_one(user_id=userId)

    return user


@post('/user/{userId}/reset')
@asyncio.coroutine
def reset_passwd(userId, new_passwd):
    assert userId != 0

    user = yield from User.find_one(user_id=userId)

    md_str = hashlib.md5(new_passwd.encode("utf8")).hexdigest()
    user.password = md_str
    yield from user.update()

    return {'msg': 'success', 'isSuccess': True}
