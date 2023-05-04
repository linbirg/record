#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import datetime
import calendar

class DateHelper:
    @classmethod
    def to_date(cls,one):
        '''
        ### 将日期转换为Date类型。
        ### para:
        - one: 某一天，可以是Date、Datetime或者```%Y-%m-%d```格式的字符串
        '''
        # import datetime
        if isinstance(one,str):
            one_date = datetime.datetime.strptime(one, "%Y-%m-%d")
            return one_date.date()
        
        if isinstance(one,datetime.datetime):
            return one.date()
        
        if isinstance(one,datetime.date):
            return one
        
        raise RuntimeError('不支持的日期格式')

    @classmethod
    def add_ndays(cls,one,ndays):
        # import datetime
        one_date = cls.to_date(one)
        one_date = one_date + datetime.timedelta(ndays)
        return one_date 
    
    @classmethod
    def date_is_after(cls, one, other):
        one_date = cls.to_date(one)
        other_date = cls.to_date(other)
        
        is_after = one_date > other_date
        return is_after

    @classmethod
    def days_between(cls, one,other):
        one_date = cls.to_date(one)
        other_date = cls.to_date(other)
        
        interval = one_date - other_date
        return interval.days

    @classmethod
    def today(cls):
        return cls.to_date(datetime.date.today()) 

    @classmethod
    def month_region(cls,month,year=2021):
        month_start = datetime.datetime(year, month, 1)
        month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1])
        return cls.to_date(month_start), cls.to_date(month_end) 
