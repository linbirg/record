#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import get, post, ResponseBody

from www.dao.user import User

from lib import logger
from www.common.message import Message
from www.dao.week_note import WeekNote, Detail
from www.dao.field_desc import StatusField
from www.handlers.vo.vo_activity import VoActivity
from utils.date_util import DateHelper


async def assert_user(userId):
    user = await User.find_one(user_id=userId)
    if user is None:
        logger.LOG_WARNING("can not find user where userID=%d", userId)

        return False, None

    return True, user


async def query_month_details(userId, month, year=2021):
    start, end = DateHelper.month_region(month, year)
    details = await Detail.find_between(user_id=userId, start=start, end=end)
    return details


@post("/reports/activity/query")
@ResponseBody
async def query(userId, month, year=2021):

    is_valided, user = await assert_user(userId)

    if not is_valided:
        return Message("failed", False)

    mn_dtls = await query_month_details(userId, month, year)

    activities = VoActivity.from_details(mn_dtls)

    return {"activities": activities}
