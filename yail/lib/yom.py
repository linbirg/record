# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

# yom-采用Row Data Gateway模式实现的简单om框架。

# 1.orm 是什么
#  ORM 即Object Relational Mapping，全称对象关系映射
# 2.orm的好处
#  i.对于大部分的增删改查的表操作，orm实现表行到类和对象的一一映射，从而省区重复的、构造sql的麻烦，从而简单操作只需要调用方法，不需要sql即可完成。
#  ii.屏蔽数据库细节，提高开发效率，便于数据库迁移。
# 3.目前orm框架的缺点
#   现有sqlalchemy,peewee等太重，性能也有问题。
# 4.诉求
#   我只需要简单的om，和简单的crud的封装。raw sql有其便利性，需要保留支持。

# 这里参照了简书上的两种实现，分别为 https://www.jianshu.com/p/042abf8918fc与https://www.jianshu.com/p/ac8a9bb57ec3。
# 这里主要参考后面一种，并改为同步的oracle版本，后续考虑异步版本。
# ver.0.02 将数据库连接独立到dao中，model只记录映射。

# import logging as logger

from . import logger
import asyncio
import aiomysql

import datetime


class Pool(object):

    __pool = None

    @classmethod
    @asyncio.coroutine
    def create_pool(cls, **kw):
        # logger.LOG_INFO('create database connection pool...')
        if cls.__pool is not None:
            return cls.__pool

        cls.__pool = yield from aiomysql.create_pool(
            host=kw.get('host', 'localhost'),
            port=kw.get('port', 3306),
            user=kw['user'],
            password=kw['password'],
            db=kw['db'],
            charset=kw.get('charset', 'utf8'),
            autocommit=kw.get('autocommit', True),
            maxsize=kw.get('maxsize', 10),
            minsize=kw.get('minsize', 1),
            loop=None,  # 默认用asyncio.get_event_loop()
        )

    @classmethod
    def pool(cls):
        return cls.__pool


class Field(object):
    def __init__(self, name, column_type, primary_key, default, desc=""):
        self.name = name  # 字段名
        self.column_type = column_type  # 字段数据类型
        self.primary_key = primary_key  # 是否是主键
        self.default = default  # 有无默认值
        self.description = desc  # 描述

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

        return __ddl__ + ' comment \'' + self.description + '\''

    def __get_defualt__(self):
        if self.default is not None:
            value = self.default() if callable(self.default) else self.default
            return value

        return None


class StringField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 unique=False,
                 default=None,
                 ddl="varchar(255)",
                 desc=""):

        if unique:
            ddl = ddl + " unique "

        super().__init__(name, ddl, primary_key, default, desc)


class CharField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 unique=False,
                 default=None,
                 size=1,
                 desc=""):

        _ddl_ = "CHAR(%d)" % size
        if unique:
            _ddl_ = _ddl_ + " unique "

        super().__init__(name, _ddl_, primary_key, default, desc)
        self.size = size

    def rpad(self, val, padding=b" ", db_internal_encoding="gbk"):
        if val is None:
            val = ""
        return (val.encode(db_internal_encoding).ljust(
            self.size, padding).decode(db_internal_encoding))


class DoubleField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 default=0.0,
                 size=(18, 2),
                 desc=""):
        super().__init__(name, "NUMBER(%d,%d)" % size, primary_key, default,
                         desc)


class IntField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 auto_increment=False,
                 default=0,
                 desc=""):

        _ddl_ = 'INT'

        self.auto_increment = auto_increment

        if self.auto_increment:
            _ddl_ = _ddl_ + ' auto_increment '

        super().__init__(name, _ddl_, primary_key, default, desc)


class TimeStampField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 default=None,
                 column_type="TIMESTAMP(6)",
                 desc=""):
        super().__init__(name, column_type, primary_key, default, desc)


# 其它字段略，一个道理，一个模式


class ModelMetaClass(type):
    # 元类必须实现__new__方法，当一个类指定通过某元类来创建，那么就会调用该元类的__new__方法
    # 该方法接收4个参数
    # cls为当前准备创建的类的对象
    # name为类的名字，创建User类，则name便是User
    # bases类继承的父类集合,创建User类，则base便是Model
    # attrs为类的属性/方法集合，创建User类，则attrs便是一个包含User类属性的dict
    def __new__(cls, name, bases, attrs):
        # 因为Model类是基类，所以排除掉，如果你print(name)的话，会依次打印出Model,User,Blog，即
        # 所有的Model子类，因为这些子类通过Model间接继承元类
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        # 取出表名，默认与类的名字相同
        tableName = attrs.get("__table__", None) or name
        logger.LOG_TRACE("found model: %s (table: %s)" % (name, tableName))
        # 用于存储所有的字段，以及字段值
        mappings = dict()
        # 仅用来存储非主键意外的其它字段，而且只存key
        fields = []
        # 仅保存主键的key
        # primaryKey = None
        pkeys = []
        # 注意这里attrs的key是字段名，value是字段实例，不是字段的具体值
        # 比如User类的id=StringField(...) 这个value就是这个StringField的一个实例，而不是实例化
        # 的时候传进去的具体id值
        for k, v in attrs.items():
            # attrs同时还会拿到一些其它系统提供的类属性，我们只处理自定义的类属性，所以判断一下
            # isinstance 方法用于判断v是否是一个Field
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    pkeys.append(k)
                else:
                    fields.append(k)
        # 不做必须有主键的检查，一方面可以方便定义空的类，另一方面可能确实存在没有主键的表。
        # 保证了必须有一个主键
        # if len(pkeys) == 0:
        #     raise RuntimeError("Primary key not found")
        # 这里的目的是去除类属性，为什么要去除呢，因为我想知道的信息已经记录下来了。
        # 去除之后，就访问不到类属性了
        # 记录到了mappings,fields，pkeys等变量里，而我们实例化的时候，如
        # user=User(id='10001') ，为了防止这个实例变量与类属性冲突，所以将其去掉
        for k in mappings.keys():
            attrs.pop(k)
        # 以下都是要返回的东西了，刚刚记录下的东西，如果不返回给这个类，又谈得上什么动态创建呢？
        # 到此，动态创建便比较清晰了，各个子类根据自己的字段名不同，动态创建了自己
        # 下面通过attrs返回的东西，在子类里都能通过实例拿到，如self
        attrs["__mappings__"] = mappings
        attrs["__table__"] = tableName
        attrs["__pKeys__"] = pkeys
        attrs["__fields__"] = fields

        def __get_sql_cols_list(cols):
            return ",".join(
                map(lambda k: "%s" % (mappings.get(k).name or k), cols))

        def __get_sql_params_list(cols):
            return ",".join(map(lambda k: "?", cols))

        def __get_sql_param_pairs_list(cols):
            return ",".join(
                map(
                    lambda k: "%s=?" % (mappings.get(k).name or k),
                    cols,
                ))

        def __get_sql_where_con_pairs_list(cols):
            return " and ".join(
                map(
                    lambda k: "%s=?" % (mappings.get(k).name or k),
                    cols,
                ))

        # 只是为了Model编写方便，放在元类里和放在Model里都可以
        # attrs["__select__"] = "select %s,%s from %s " % (
        #     __get_sql_cols_list(pkeys),
        #     __get_sql_cols_list(fields),
        #     tableName,
        # )
        # 拟使用format来格式化字符串
        attrs["__select__"] = "select {pkeys},{fields} from {table} ".format(
            pkeys=__get_sql_cols_list(pkeys),
            fields=__get_sql_cols_list(fields),
            table=tableName)

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


# 让Model继承dict,主要是为了具备dict所有的功能，如get方法
# metaclass指定了Model类的元类为ModelMetaClass
class Model(dict, metaclass=ModelMetaClass):
    __db_internal_encoding = "gbk"

    def __init__(self, **kw):
        super().__init__(**kw)

    # 实现__getattr__与__setattr__方法，可以使引用属性像引用普通字段一样  如self['id']
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
            value = field.default() if callable(
                field.default) else field.default

        setattr(self, key, value)
        return value

    def getValue(self, key):
        value = getattr(self, key, None)
        return value

    # 取默认值，上面字段类不是有一个默认值属性嘛，默认值也可以是函数
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        field = self.__mappings__[key]
        if value is None:
            if field.default is not None:
                value = field.default() if callable(
                    field.default) else field.default
                # setattr(self, key, value)  # TODO get函数不写属性,确定是否需要set。

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
        # 将数据库查出的以字段名显示的row（dict），转换为Model的对象
        data = dict()
        for k, f in cls.__mappings__.items():
            data[k] = row[f.name.lower()]  # lower

        return cls(**data)

    @classmethod
    def padding_val_if_neccesary(cls, val, key):
        field = cls.__mappings__[key]
        if not isinstance(field, CharField):
            return val

        return field.rpad(val,
                          padding=b" ",
                          db_internal_encoding=cls.__db_internal_encoding)

    @classmethod
    def __get_key_name__(cls, key):
        if key not in cls.__mappings__:
            raise RuntimeError("key not found")
        key_name = cls.__mappings__.get(key).name or key
        return key_name

    @classmethod
    def __join__(cls, format, cols, spliter=","):
        return spliter.join(
            map(lambda k: format % (cls.__get_key_name__(k)), cols))

    @classmethod
    def get_sql_cols_list(cls, cols, spliter=","):
        return cls.__join__("%s", cols)

    # @classmethod
    # def __get_sql_params_list(cls, cols):
    #     return cls.__join__(":%s", cols)

    @classmethod
    def get_sql_where_con_pairs_list(cls, cols):
        return " and ".join(
            map(lambda k: '{}=?'.format(cls.__get_key_name__(k)), cols))

    @staticmethod
    def __func_create_row__(cursor):
        # 列名全部小写，保持跟书写习惯一致。取列也已小写方式读取。
        cols = [d[0].lower() for d in cursor.description]

        def createrow(*args):
            return dict(zip(cols, args))

        return createrow

    @classmethod
    @asyncio.coroutine
    def get_connection(cls):
        conn = yield from Pool.pool()
        return conn

    @classmethod
    @asyncio.coroutine
    def select(cls, sql, args=None, size=None):
        # global __pool
        # print("to select:", sql)
        logger.LOG_TRACE("to select:%s", sql)
        with (yield from cls.get_connection()) as conn:
            cur = yield from conn.cursor(aiomysql.DictCursor)
            yield from cur.execute(sql.replace('?', '%s'), args or ())
            cur.rowfactory = cls.__func_create_row__(cur)
            if size:
                rs = yield from cur.fetchmany(size)
            else:
                rs = yield from cur.fetchall()
            yield from cur.close()
            logger.LOG_DEBUG('rows returned: %s' % len(rs))
            # print('rows returned: %s' % len(rs))
            return rs

    @classmethod
    @asyncio.coroutine
    def execute(cls, sql, args=None):
        # global __pool
        # print(sql, args)
        logger.LOG_TRACE("to execute:%s", sql)
        with (yield from cls.get_connection()) as conn:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args or ())
            affected = cur.rowcount
            yield from cur.close()
            return affected

    @classmethod
    @asyncio.coroutine
    def find_where(cls, where=None, *args):
        # 此函数不会做padding等补全操作
        sql = [cls.__select__]
        if where:
            sql.append("where")
            sql.append(where)

        rs = yield from cls.select(" ".join(sql), args)

        return [cls.row_mapper(r) for r in rs]  # 返回的是一个实例对象引用

    @classmethod
    @asyncio.coroutine
    def find(cls, **pks):
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

        rows = yield from cls.find_where(where, *args_val)
        return rows

    @classmethod
    @asyncio.coroutine
    def find_one(cls, **pks):
        '''返回一条数据，如果没有则返回None，多条数据会抛异常.'''
        rets = yield from cls.find(**pks)
        if rets is None or len(rets) == 0:
            return None

        if len(rets) > 1:
            raise RuntimeError("find_one：应该返回一条数据，但是返回了多条数据。")

        return rets[0]

    @classmethod
    @asyncio.coroutine
    def find_all(cls):
        rows = yield from cls.find()
        return rows

    @classmethod
    @asyncio.coroutine
    def find_one_with_lock(cls, nowait=False, time_out=5, **pks):
        assert isinstance(time_out, int)

        if len(pks) <= 0:
            raise RuntimeError("find_one_with_lock：参数不能为空.")

        keys = []
        args = {}

        for k, v in pks.items():
            args[cls.__get_key_name__(k)] = cls.padding_val_if_neccesary(v, k)
            keys.append(k)

        where = ""
        if len(keys) > 0:
            where = " where " + cls.get_sql_where_con_pairs_list(keys)
        wait_sql = "nowait" if nowait else "wait {0}".format(time_out)
        for_update_sql = "for update {0}".format(wait_sql)
        _lock_sql = "{0} {1} {2}".format(cls.__select__, where, for_update_sql)

        # TODO 测试with连接的自动提交是否对此有影响
        rs = yield from cls.select(_lock_sql, args)

        if len(rs) > 1:
            raise RuntimeError("find_one_with_lock：应该返回一条数据，但是返回了多条数据。")

        if rs is None or len(rs) == 0:
            return None

        return cls.row_mapper(rs[0])

    @asyncio.coroutine
    def save(self):
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        affected = yield from self.execute(
            self.__insert__, self.__get_args__(self.__mappings__.keys()))

        return affected

    @asyncio.coroutine
    def delete(self):
        affected = yield from self.execute(self.__delete__,
                                           self.__get_args__(self.__pKeys__))

        return affected

    @asyncio.coroutine
    def update(self):
        self.updated_at = datetime.datetime.now()
        affected = yield from self.execute(
            self.__update__,
            self.__get_args__(self.__fields__ + self.__pKeys__))

        return affected
