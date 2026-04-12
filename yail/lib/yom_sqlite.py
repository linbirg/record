# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

# yom-sqlite: 采用Row Data Gateway模式实现的SQLite版om框架。
# 基于 yom.py 改写，使用同步 sqlite3 + asyncio.to_thread 模拟异步。

from . import logger
import sqlite3
import asyncio

import datetime


class Pool(object):
    __db_path = None

    @classmethod
    async def create_pool(cls, db_path):
        cls.__db_path = db_path

    @classmethod
    def pool(cls):
        return cls.__db_path


class Field(object):
    def __init__(self, name, column_type, primary_key, default, desc=""):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.description = desc

    def __str__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.name)

    def get_ddl(self):
        __ddl__ = "%s %s %s" % (
            self.name,
            self.column_type,
            "not null" if self.primary_key else " ",
        )

        val = self.__get_defualt__()

        if val:
            __ddl__ = "%s %s" % (__ddl__, "default " + str(val))

        return __ddl__

    def __get_defualt__(self):
        if self.default is not None:
            value = self.default() if callable(self.default) else self.default
            return value

        return None


class StringField(Field):
    def __init__(
        self,
        name=None,
        primary_key=False,
        unique=False,
        default=None,
        ddl="TEXT",
        desc="",
    ):
        if unique:
            ddl = ddl + " unique "

        super().__init__(name, ddl, primary_key, default, desc)


class CharField(Field):
    def __init__(
        self, name=None, primary_key=False, unique=False, default=None, size=1, desc=""
    ):
        _ddl_ = "TEXT"
        if unique:
            _ddl_ = _ddl_ + " unique "

        super().__init__(name, _ddl_, primary_key, default, desc)
        self.size = size

    def rpad(self, val, padding=b" ", db_internal_encoding="gbk"):
        if val is None:
            val = ""
        return (
            val.encode(db_internal_encoding)
            .ljust(self.size, padding)
            .decode(db_internal_encoding)
        )


class DoubleField(Field):
    def __init__(
        self, name=None, primary_key=False, default=0.0, size=(18, 2), desc=""
    ):
        super().__init__(name, "REAL", primary_key, default, desc)


class IntField(Field):
    def __init__(
        self, name=None, primary_key=False, auto_increment=False, default=0, desc=""
    ):
        _ddl_ = "INTEGER"

        self.auto_increment = auto_increment

        if self.auto_increment and primary_key:
            _ddl_ = "INTEGER PRIMARY KEY AUTOINCREMENT"

        super().__init__(name, _ddl_, primary_key, default, desc)


class TimeStampField(Field):
    def __init__(
        self,
        name=None,
        primary_key=False,
        default=None,
        column_type="TEXT",
        desc="",
    ):
        super().__init__(name, column_type, primary_key, default, desc)


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get("__table__", None) or name
        logger.LOG_TRACE("found model: %s (table: %s)" % (name, tableName))

        mappings = dict()
        fields = []
        pkeys = []

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    pkeys.append(k)
                else:
                    fields.append(k)

        for k in mappings.keys():
            attrs.pop(k)

        attrs["__mappings__"] = mappings
        attrs["__table__"] = tableName
        attrs["__pKeys__"] = pkeys
        attrs["__fields__"] = fields

        def __get_sql_cols_list(cols):
            return ",".join(map(lambda k: "%s" % (mappings.get(k).name or k), cols))

        def __get_sql_params_list(cols):
            return ",".join(map(lambda k: "?", cols))

        def __get_sql_param_pairs_list(cols):
            return ",".join(
                map(
                    lambda k: "%s=?" % (mappings.get(k).name or k),
                    cols,
                )
            )

        def __get_sql_where_con_pairs_list(cols):
            return " and ".join(
                map(
                    lambda k: "%s=?" % (mappings.get(k).name or k),
                    cols,
                )
            )

        attrs["__select__"] = "select {pkeys},{fields} from {table} ".format(
            pkeys=__get_sql_cols_list(pkeys),
            fields=__get_sql_cols_list(fields),
            table=tableName,
        )

        attrs["__update__"] = "update %s set %s where %s" % (
            tableName,
            __get_sql_param_pairs_list(fields),
            __get_sql_where_con_pairs_list(pkeys),
        )
        attrs["__insert__"] = "insert into %s (%s,%s) values (%s,%s)" % (
            tableName,
            __get_sql_cols_list(pkeys),
            __get_sql_cols_list(fields),
            __get_sql_params_list(pkeys),
            __get_sql_params_list(fields),
        )
        attrs["__delete__"] = "delete from %s where %s " % (
            tableName,
            __get_sql_where_con_pairs_list(pkeys),
        )
        attrs["__count__"] = "select count(1) from %s " % tableName

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):
    __db_internal_encoding = "gbk"

    def __init__(self, **kw):
        super().__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def __missing__(self, key):
        field = self.__mappings__[key]
        value = None
        if field.default is not None:
            value = field.default() if callable(field.default) else field.default

        setattr(self, key, value)
        return value

    def getValue(self, key):
        value = getattr(self, key, None)
        return value

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        field = self.__mappings__[key]
        if value is None:
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default

        return self.padding_val_if_neccesary(value, key)

    def __get_args__(self, keys):
        args = []
        for key in keys:
            if key not in self.__mappings__:
                raise RuntimeError("field not found")
        for key in keys:
            args.append(self.getValueOrDefault(key))

        return args

    @classmethod
    def row_mapper(cls, row):
        data = dict()
        for k, f in cls.__mappings__.items():
            data[k] = row[f.name]

        return cls(**data)

    @classmethod
    def padding_val_if_neccesary(cls, val, key):
        field = cls.__mappings__[key]
        if not isinstance(field, CharField):
            return val

        return field.rpad(
            val, padding=b" ", db_internal_encoding=cls.__db_internal_encoding
        )

    @classmethod
    def __get_key_name__(cls, key):
        if key not in cls.__mappings__:
            raise RuntimeError("key not found")
        key_name = cls.__mappings__.get(key).name or key
        return key_name

    @classmethod
    def __join__(cls, format, cols, spliter=","):
        return spliter.join(map(lambda k: format % (cls.__get_key_name__(k)), cols))

    @classmethod
    def get_sql_cols_list(cls, cols, spliter=","):
        return cls.__join__("%s", cols)

    @classmethod
    def get_sql_where_con_pairs_list(cls, cols):
        return " and ".join(map(lambda k: "{}=?".format(cls.__get_key_name__(k)), cols))

    @staticmethod
    def __func_create_row__(cursor):
        cols = [d[0].lower() for d in cursor.description]

        def createrow(*args):
            return dict(zip(cols, args))

        return createrow

    @classmethod
    async def get_connection(cls):
        db_path = Pool.pool()
        conn = sqlite3.connect(db_path)
        return conn

    @classmethod
    async def select(cls, sql, args=None, size=None):
        logger.LOG_TRACE("to select:%s", sql)
        conn = await cls.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, args or ())
            if size:
                rs = cur.fetchmany(size)
            else:
                rs = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            result = [dict(zip(cols, row)) for row in rs]
            cur.close()
            logger.LOG_DEBUG("rows returned: %s" % len(result))
            return result
        finally:
            conn.close()

    @classmethod
    async def execute(cls, sql, args=None):
        logger.LOG_TRACE("to execute:%s", sql)
        conn = await cls.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, args or ())
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected
        finally:
            conn.close()

    @classmethod
    async def find_where(cls, where=None, *args):
        sql = [cls.__select__]
        if where:
            sql.append("where")
            sql.append(where)

        rs = await cls.select(" ".join(sql), args)

        return [cls.row_mapper(r) for r in rs]

    @classmethod
    async def count_where(cls, where=None, *args):
        sql = [cls.__count__]
        if where:
            sql.append("where")
            sql.append(where)

        rs = await cls.select(" ".join(sql), args)

        return rs[0]["count(1)"]

    @classmethod
    async def find(cls, **pks):
        keys = []
        fields = []
        args = {}

        if pks is not None and len(pks) > 0:
            for k, v in pks.items():
                filed_name = cls.__get_key_name__(k)
                args[filed_name] = cls.padding_val_if_neccesary(v, k)
                keys.append(k)
                fields.append(filed_name)

        where = None
        if len(pks) > 0:
            where = cls.get_sql_where_con_pairs_list(keys)

        args_val = []

        for k in fields:
            args_val.append(args[k])

        rows = await cls.find_where(where, *args_val)
        return rows

    @classmethod
    async def find_one(cls, **pks):
        """返回一条数据，如果没有则返回None，多条数据会抛异常."""
        rets = await cls.find(**pks)
        if rets is None or len(rets) == 0:
            return None

        if len(rets) > 1:
            raise RuntimeError("find_one：应该返回一条数据，但是返回了多条数据。")

        return rets[0]

    @classmethod
    async def find_all(cls):
        rows = await cls.find()
        return rows

    async def save(self):
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()
        affected = await self.execute(
            self.__insert__, self.__get_args__(self.__mappings__.keys())
        )

        return affected

    async def delete(self):
        affected = await self.execute(
            self.__delete__, self.__get_args__(self.__pKeys__)
        )

        return affected

    async def update(self):
        self.updated_at = datetime.datetime.now().isoformat()
        affected = await self.execute(
            self.__update__, self.__get_args__(self.__fields__ + self.__pKeys__)
        )

        return affected
