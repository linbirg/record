#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

from lib import Model, IntField
from lib import logger

import datetime


class AutoIdModel(Model):
    def __init__(self, **kw):
        super().__init__(**kw)

    def __split_auto_mappings__(self):
        no_auto_mappings = {}
        auto_mappings = {}

        for key in self.__mappings__:
            field = self.__mappings__[key]
            if not isinstance(field, IntField):
                no_auto_mappings[key] = field
                continue

            if isinstance(field, IntField):
                if field.auto_increment:
                    auto_mappings[key] = field
                    continue

                if not field.auto_increment:
                    no_auto_mappings[key] = field

        return auto_mappings, no_auto_mappings

    async def save(self):
        """对于有auto_increament的表，可以实现自动插入，并返回lastrowid，赋值到指定字段"""
        autos, no_autos = self.__split_auto_mappings__()

        assert len(autos) <= 1

        cols, vals, args = [], [], []
        for key in no_autos:
            field = no_autos[key]
            cols += [field.name]
            vals += ["?"]

            if key in ["created_at", "updated_at"]:
                self.created_at = datetime.datetime.now().isoformat()
                self.updated_at = datetime.datetime.now().isoformat()

            args += [self[key]]

        vals_sql = ",".join(vals)
        cols_sql = ",".join(cols)

        sql = "insert into %s (%s) values(%s)" % (self.__table__, cols_sql, vals_sql)

        logger.LOG_TRACE("to execute:%s args:%s", sql, args)
        conn = await self.get_connection()
        with conn:
            cur = conn.cursor()
            cur.execute(sql, args or ())
            affected = cur.rowcount
            last_row_id = cur.lastrowid
            cur.close()

        auto_key = list(autos.keys())[0]
        self[auto_key] = last_row_id
        return affected
