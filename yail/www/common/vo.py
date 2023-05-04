#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
与前端交互的数据对象基类，基础dict，主要为了方便使用
'''
from lib import logger


class ViewObj(dict):
    def __init__(self, **kw):
        super().__init__(**kw)

    # 实现__getattr__与__setattr__方法，可以使引用属性像引用普通字段一样  如self['id']
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            logger.LOG_WARNING(r"'ViewObj' object has no attribute '%s'" % key)
            # raise AttributeError()
            return None

    def __setattr__(self, key, value):
        self[key] = value

    @classmethod
    def from_model(cls, model):
        pass

    @classmethod
    def from_models(cls, modeles):
        return [cls.from_model(m) for m in modeles]