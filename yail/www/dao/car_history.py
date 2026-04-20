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
    deleted_at = fd.CreatedAtField()


class CarNoHistory(AutoIdModel):
    __table__ = "t_car_no_history"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    car_id = fd.IntField(name="car_id")
    old_car_no = fd.CarNoField()
    new_car_no = fd.CarNoField()
    changed_at = fd.CreatedAtField()
