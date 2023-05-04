import os
import sys


__abs_file__ = os.path.abspath(__file__)
lib_dir = os.path.dirname(__abs_file__)
test_dir = os.path.dirname(lib_dir)
code_dir = os.path.dirname(test_dir)
sys.path.append(code_dir)


from lib.yom import Model,IntField,CharField,StringField,Pool

import asyncio
import pytest


from conf.db import db_confs



class User(Model):
    __table__ = "user"

    user_id = IntField(name="user_id",primary_key=True, desc="id",)

    user_name = CharField(name="user_name",size=18,desc="username")
    nickname = StringField(name="nickname",desc="nickname")
    password = StringField(name="password",desc="password")
    role_id = IntField(name="role_id")
    group_name = StringField(name="group_name",desc="group name")
    type_id = IntField(name="type_id")
    

# @pytest.fixture
# def event_loop():
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.

@pytest.mark.asyncio
async def test_create_pool(event_loop):
    await Pool.create_pool(loop=event_loop, host='127.0.0.1',port=3306,user="record",password="ww123456",db="record")
    print(Pool.pool())
    conn = await Pool.pool().acquire()
    
    cur = await conn.cursor()
    
    await cur.execute("SELECT * FROM user where user_id=1")
    print(cur.description)
    r = await cur.fetchall()
    print(r)
    await cur.close()

    # Pool.pool().close()

    # await Pool.pool().wait_closed()

    # event_loop.close()


@pytest.mark.asyncio
async def test_find_one(event_loop):
    await Pool.create_pool(loop=event_loop, host='127.0.0.1',port=3306,user="record",password="ww123456",db="record")

    one = await User.find_one(user_id=1)
    print(one)

    assert one.user_name.strip() == 'yzr'

        
        
