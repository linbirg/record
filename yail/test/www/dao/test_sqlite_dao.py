#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
import asyncio
import tempfile

__abs_file__ = os.path.abspath(__file__)
dao_dir = os.path.dirname(__abs_file__)
www_dir = os.path.dirname(dao_dir)
test_dir = os.path.dirname(www_dir)
code_dir = os.path.dirname(test_dir)
sys.path.insert(0, code_dir)

import pytest
from tools.migrate_sqlite.rake_sqlite_migrate import run_migrations
from lib.yom_sqlite import Pool as SqlitePool


@pytest.fixture
def sqlite_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    run_migrations(path)
    asyncio.get_event_loop().run_until_complete(SqlitePool.create_pool(path))
    yield path
    os.unlink(path)


@pytest.mark.asyncio
async def test_user_save_and_find(sqlite_db):
    from www.dao.user import User

    user = User(username="testuser", nickname="test", password="123456")
    await user.save()
    found = await User.find_one(username="testuser")
    assert found is not None
    assert found.nickname == "test"


@pytest.mark.asyncio
async def test_user_update(sqlite_db):
    from www.dao.user import User

    user = User(username="updateuser", nickname="old", password="123456")
    await user.save()
    user.nickname = "new"
    await user.update()
    found = await User.find_one(username="updateuser")
    assert found.nickname == "new"


@pytest.mark.asyncio
async def test_detail_find_between(sqlite_db):
    from www.dao.week_note import WeekNote, Detail

    note = WeekNote(
        user_id=1,
        user_name="tester",
        week_count=1,
        week_day=1,
        year=2026,
        rec_date="2026-04-01",
    )
    await note.save()
    detail = Detail(
        note_id=note.note_id,
        user_id=1,
        user_name="tester",
        rec_date="2026-04-01",
        week_day=1,
        status="1",
        desc="test job",
    )
    await detail.save()
    results = await Detail.find_between(1, "2026-04-01", "2026-04-30")
    assert len(results) > 0


@pytest.mark.asyncio
async def test_car_info_find_by_carno(sqlite_db):
    from www.dao.car_info import CarInfo

    car = CarInfo(name="tester", dept="test dept", carNo="ABC123", brand="test brand")
    await car.save()
    results = await CarInfo.find_by_carno("ABC")
    assert len(results) >= 1
    assert results[0].carNo == "ABC123"


@pytest.mark.asyncio
async def test_chat_message_raw_sql(sqlite_db):
    from www.dao.chat_message import ChatMessage

    msg = ChatMessage(user_id=1, session_id="sess_001", role="user", content="hello")
    await msg.save()
    results = await ChatMessage.find_by_session(1, "sess_001", limit=10)
    assert len(results) == 1
    assert results[0].content == "hello"
