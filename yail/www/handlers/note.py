#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import get, post, RequestBody, ResponseBody

from www.handlers.vo.vo_note_risk import VoNoteRisk
from www.handlers.vo.page import VoPage
from www.common.message import Message
from www.dao.week_note import WeekNote, Detail
from www.dao.user import User
from www.handlers.vo.vo_week_note import VoWeekNote, VoWeekDetail

from utils.date_util import DateHelper

from lib import logger


@post("/noteRisk/selectNoteRiskByPage.action")
@RequestBody("page", kls=VoPage)
@ResponseBody
async def page(page):
    print(page)
    notes = await WeekNote.find(user_id=page.userId)
    return {"page": {"totalItem": 1}, "note": VoNoteRisk.from_notes(notes)}


@post("/note/query")
@ResponseBody
async def query(userId, weekCount, year=None):
    if year is None:
        year = DateHelper.today().year

    notes = await WeekNote.find(user_id=userId, week_count=weekCount, year=year)
    vo_notes = []
    for nt in notes:
        vo_nt = VoWeekNote.from_model(nt)

        details = await Detail.find(note_id=nt.note_id)

        vo_dts = VoWeekDetail.from_models(details)
        vo_nt.details = vo_dts

        vo_notes.append(vo_nt)

    def pad_week_days(vo_notes):
        def init_a_week():
            vo = VoWeekNote(userId=userId, weekCount=weekCount, weekDay=1)

            a_weeks = []
            for day in range(1, 6):
                vo_day = VoWeekNote.from_other(vo)
                vo_day.weekDay = day
                a_weeks.append(vo_day)

            return a_weeks

        a_weeks = init_a_week()

        if len(vo_notes) <= 0:
            return a_weeks

        for vo in vo_notes:
            a_weeks[vo.weekDay - 1] = vo

        return a_weeks

    return {"note": pad_week_days(vo_notes)}


@post("/note/detail/delete")
@ResponseBody
async def delete_detail(id):
    dt = await Detail.find_one(detail_id=id)
    if dt is None:
        logger.LOG_TRACE("can not find detail where id=%d", id)

    if dt:
        await dt.delete()

    return Message("success", True)


@post("/note/detail/add")
@ResponseBody
async def add_detail(userId, weekCount, weekDay, desc, status):
    user = await User.find_one(user_id=userId)

    if user is None:
        logger.LOG_WARNING("can not find user where userID=%d", userId)

        return Message("failed", False)

    year = DateHelper.today().year

    note = await WeekNote.find_one(
        user_id=userId, week_count=weekCount, week_day=weekDay, year=year
    )

    if note is None:
        logger.LOG_WARNING(
            "can not find week note where userID=%s weekCount=%d weekDay=%d. Will insert new one.",
            userId,
            weekCount,
            weekDay,
        )

        note = WeekNote(
            user_id=user.user_id,
            user_name=user.username,
            week_count=weekCount,
            week_day=weekDay,
            year=year,
            rec_date=DateHelper.today(),
        )
        await note.save()

    detail = Detail(
        note_id=note.note_id,
        user_id=userId,
        user_name=user.username,
        rec_date=DateHelper.today(),
        week_day=weekDay,
        status=status,
        desc=desc,
    )

    await detail.save()

    return detail


@post("/note/detail/update")
@ResponseBody
async def update_detail(detailId, desc, status):
    dt = await Detail.find_one(detail_id=detailId)
    if dt is None:
        msg = "not found detail where id={}".format(detailId)
        logger.LOG_TRACE(msg)

        return Message("failed! " + msg, False)

    dt.desc = desc
    dt.status = status

    await dt.update()

    return Message("success", True)
