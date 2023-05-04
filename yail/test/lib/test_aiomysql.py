import os
import sys


__abs_file__ = os.path.abspath(__file__)
lib_dir = os.path.dirname(__abs_file__)
test_dir = os.path.dirname(lib_dir)
code_dir = os.path.dirname(test_dir)
sys.path.append(code_dir)


import aiomysql


import asyncio
from lib.yom import Pool


loop = asyncio.get_event_loop()

# @asyncio.coroutine
# def test_example():
#     conn = yield from aiomysql.connect(host='127.0.0.1', port=3306,
#                                        user='record', password='ww123456', db='record',
#                                        loop=loop)

#     cur = yield from conn.cursor()
#     yield from cur.execute("SELECT * FROM user")
#     print(cur.description)
#     r = yield from cur.fetchall()
#     print(r)
#     yield from cur.close()
#     conn.close()

# loop.run_until_complete(test_example())

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        yield from Pool.create_pool(loop=loop,host='127.0.0.1', port=3306,
                                       user='record', password='ww123456', db='record')
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

@async_test
@asyncio.coroutine
def test_create_pool():
    # yield from Pool.create_pool(loop=loop,host='127.0.0.1', port=3306,
    #                                    user='record', password='ww123456', db='record')
    
    # print(Pool.pool())

    with (yield from Pool.pool()) as conn:
        assert conn
        print(conn)
        cur = yield from conn.cursor()
        yield from cur.execute("SELECT * FROM user where user_id=1")
        print(cur.description)
        r = yield from cur.fetchall()
        print(r)
        yield from cur.close()



loop.run_until_complete(test_create_pool())
# test_create_pool()