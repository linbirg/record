#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .vo import ViewObj


class Message(ViewObj):
    def __init__(self, msg, succeed=True):
        # args = {'msg': msg, 'isSuccess': succeed}
        # super().__init__(**args)
        # self.msg = msg
        # self.isSuccess = succeed

        self.msg = msg
        self.isSuccess = succeed