#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author:linbirg

from www.common.vo import ViewObj
# from www.dao.field_desc import StatusField


class VoActivity(ViewObj):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_details(cls, details):
        activities = {}
        for dt in details:
            if dt.rec_date not in activities:
                activities[dt.rec_date] = []
            
            activities[dt.rec_date] += [dt.desc]
        
        return [{'timestamp':a,'details':activities[a]} for a in activities]
            
