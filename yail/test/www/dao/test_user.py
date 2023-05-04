#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import os
import sys

__abs_file__ = os.path.abspath(__file__)
dao_dir = os.path.dirname(__abs_file__)
www_dir = os.path.dirname(dao_dir)
test_dir = os.path.dirname(www_dir)
code_dir = os.path.dirname(test_dir)
sys.path.append(code_dir)

import asyncio

from lib.yom import Pool

from www.dao.user import User

loop = asyncio.get_event_loop()


def async_test(coro):
    def wrapper(*args, **kwargs):
        yield from Pool.create_pool(loop=loop,
                                    host='127.0.0.1',
                                    port=3306,
                                    user='record',
                                    password='ww123456',
                                    db='record')
        rel = yield from coro(*args, **kwargs)
        return rel

    return wrapper


@asyncio.coroutine
@async_test
def test_user_save():
    user = User(username='hello',
                nickname='hello',
                password='123',
                role_id=1,
                group_name='test',
                type_id=2)

    yield from user.save()

    print(user.user_id)


@asyncio.coroutine
@async_test
def test_user_delete():
    user = yield from User.find_one(user_id=11)
    print(user)

    assert not user == None

    yield from user.delete()

    user = yield from User.find_one(user_id=11)

    assert user == None


import hashlib


@asyncio.coroutine
@async_test
def test_user_update():
    user = yield from User.find_one(user_id=1)
    print(user)

    assert not user == None

    md_str = hashlib.md5('123456'.encode("utf8")).hexdigest()
    print('md_str:', md_str)
    user.password = md_str
    yield from user.update()

    user = yield from User.find_one(user_id=1)

    print(user.password)


loop.run_until_complete(test_user_update())