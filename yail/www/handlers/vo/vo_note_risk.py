#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author:linbirg

from www.common.vo import ViewObj

# from www.dao.risk_note import NoteRisk


class VoNoteRisk(ViewObj):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_model(cls, model):
        vo = cls()
        vo.id = model.id

        vo.userId = model.user_id
        vo.userName = model.username

        vo.regDate = model.reg_date
        vo.weekCount = model.week_count
        vo.job = model.job
        vo.newJob = model.new_job
        vo.risk = model.risk
        vo.riskSolveTime = model.risk_solve_time

        return vo

    @classmethod
    def from_notes(cls, notes):
        return [cls.from_model(note) for note in notes]
