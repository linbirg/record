#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

# import os
# import sys

# __abs_file__ = os.path.abspath(__file__)
# base_dir = os.path.dirname(__abs_file__)
# dao_dir = os.path.dirname(base_dir)
# module_dir = os.path.dirname(dao_dir)
# code_dir = os.path.dirname(module_dir)
# sys.path.append(code_dir)

# from lib import dbutil
from lib.yom import CharField, IntField, DoubleField, TimeStampField, StringField
'''
常用的业务字段的定义应该统一放在这里，一是 简化对数据表的定义和使用，减少参数的数量 二是 有利于统一业务中的字段，避免重复和不一致
'''


# common
class UpdatedAtField(TimeStampField):
    def __init__(self, name='updated_at', desc='updated_at'):
        super().__init__(name=name, desc=desc)


class CreatedAtField(TimeStampField):
    def __init__(self, name='created_at', desc='created_at'):
        super().__init__(name=name, desc=desc)


class TextField(StringField):
    def __init__(self, name, size=1024, unique=False, desc=''):
        super().__init__(name=name,
                         unique=unique,
                         primary_key=False,
                         default=None,
                         ddl='varchar(%d)' % size,
                         desc=desc)


# user
class UserIDField(IntField):
    def __init__(self,
                 primary_key=False,
                 auto_increment=False,
                 desc='用户ID(自增)'):
        super().__init__(name='user_id',
                         primary_key=primary_key,
                         auto_increment=auto_increment,
                         default=0,
                         desc=desc)


class UserNameField(StringField):
    def __init__(self, primary_key=False, unique=False, desc='姓名'):
        super().__init__(name='user_name',
                         primary_key=primary_key,
                         unique=unique,
                         default=None,
                         desc=desc)


class NickNameField(StringField):
    def __init__(self, desc='nickname'):
        super().__init__(name='nickname',
                         primary_key=False,
                         default=None,
                         desc=desc)

class DepartmentField(StringField):
    def __init__(self, desc='department'):
        super().__init__(name='dept',
                         primary_key=False,
                         default='',
                         desc=desc)


class PasswdField(StringField):
    def __init__(self, desc='passwd'):
        super().__init__(name='password',
                         primary_key=False,
                         default=None,
                         desc=desc)


class RoleIDField(IntField):
    def __init__(self, primary_key=False, desc='role_id'):
        super().__init__(name='role_id',
                         primary_key=primary_key,
                         default=None,
                         desc=desc)


class TypeIDField(IntField):
    def __init__(self, primary_key=False, desc='type_id'):
        super().__init__(name='type_id',
                         primary_key=primary_key,
                         default=None,
                         desc=desc)


class GroupNameField(StringField):
    def __init__(self, desc='group_name'):
        super().__init__(name='group_name',
                         primary_key=False,
                         default=None,
                         desc=desc)


# note job
class NoteJobField(TextField):
    def __init__(self, name='job'):
        super().__init__(name=name)


class RegDateField(TextField):
    def __init__(self, name='reg_date', desc='reg_date'):
        super().__init__(name=name, size=10, desc=desc)


class NoteRiskField(StringField):
    def __init__(self, desc='risk'):
        super().__init__(name='risk',
                         primary_key=False,
                         default=None,
                         desc=desc)


class NoteRiskSolveTimeField(StringField):
    def __init__(self, desc='risk_solve_time'):
        super().__init__(name='risk_solve_time',
                         primary_key=False,
                         default=None,
                         desc=desc)


class WeekCountField(IntField):
    def __init__(self, name='week_count', desc='week_count'):
        super().__init__(name=name, desc=desc)


class StatusField(CharField):
    '''是否完成 1 完成 0 未完成'''
    STATUS_DONE = '1'
    STATUS_UNDONE = '0'

    def __init__(self, name='status', default=STATUS_DONE, desc='status'):
        super().__init__(name=name, default=default, desc=desc)

# carinfo
class CarNoField(CharField):
    '''传统车7字符，新能源8字符，预留4字符'''
    def __init__(self, name='carid', desc='carid'):
        super().__init__(name=name,size=12,desc=desc)

class BrandField(StringField):
    def __init__(self, desc='brand'):
        super().__init__(name='brand',
                         desc=desc)


class CarLicenseField(StringField):
    def __init__(self, desc='行驶证'):
        super().__init__(name='car_license',
                         desc=desc)

class LicenseField(StringField):
    def __init__(self, desc='驾驶证'):
        super().__init__(name='license',
                         desc=desc)

class AbbrField(StringField):
    def __init__(self, desc='备注'):
        super().__init__(name='abbr',
                         desc=desc)

class ImgsField(StringField):
    def __init__(self, desc='证件照'):
        super().__init__(name='imgs',
                         desc=desc)


class PicPathField(StringField):
    def __init__(self, desc='图片路径'):
        super().__init__(name='path', desc=desc)
