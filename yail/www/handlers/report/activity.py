#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import get, post, ResponseBody

from www.dao.user import User

from lib import logger
import asyncio
from www.common.message import Message
from www.dao.week_note import WeekNote, Detail
from www.dao.field_desc import StatusField
from www.handlers.vo.vo_activity import VoActivity
from utils.date_util import DateHelper




@asyncio.coroutine
def assert_user(userId):
  user = yield from User.find_one(user_id=userId)
  if user is None:
      logger.LOG_WARNING('can not find user where userID=%d', userId)

      return False,None
  
  return True,user

@asyncio.coroutine
def query_month_details(userId,month,year=2021):
  start,end = DateHelper.month_region(month,year)
  details = yield from Detail.find_between(user_id=userId,start=start,end=end)
  return details

  # for wc in week_counts:
  #   notes = yield from WeekNote.find(user_id=userId, week_count=wc)
  #   for nt in notes:
  #       details = yield from Detail.find(note_id=nt.note_id,status=StatusField.STATUS_DONE)
  #       mn_dtls += details
  


@post('/reports/activity/query')
@ResponseBody
@asyncio.coroutine
def query(userId,month,year=2021):

  is_valided, user = yield from assert_user(userId)

  if not is_valided:
    return Message('failed', False)

  mn_dtls = yield from query_month_details(userId,month,year)

  activities = VoActivity.from_details(mn_dtls)

  return {'activities':activities}

