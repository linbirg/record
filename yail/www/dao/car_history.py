#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

from . import field_desc as fd
from .base import AutoIdModel


class CarInfoHistory(AutoIdModel):
    __table__ = "t_car_info_history"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    original_id = fd.IntField(name="original_id")
    user_name = fd.UserNameField()
    dept = fd.DepartmentField()
    carid = fd.CarNoField()
    brand = fd.BrandField()
    car_license = fd.CarLicenseField()
    license = fd.LicenseField()
    abbr = fd.AbbrField()
    deleted_at = fd.CreatedAtField(name="deleted_at")


class CarNoHistory(AutoIdModel):
    __table__ = "t_car_no_history"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    car_id = fd.IntField(name="car_id")
    user_name = fd.UserNameField()
    old_car_no = fd.CarNoField(name="old_car_no")
    new_car_no = fd.CarNoField(name="new_car_no")
    changed_at = fd.CreatedAtField(name="changed_at")


class CarInfoHistoryPics(AutoIdModel):
    __table__ = "t_car_info_history_pics"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    history_id = fd.IntField(name="history_id")
    path = fd.PicPathField()
    created_at = fd.CreatedAtField()
