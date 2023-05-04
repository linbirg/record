
from . import field_desc as fd
from .base import AutoIdModel

# import asyncio

# import datetime


class CarInfo(AutoIdModel):
    __table__ = "t_car_info"

    no = fd.IntField(name='id', primary_key=True, auto_increment=True)
    name = fd.UserNameField()
    dept = fd.DepartmentField()
    carNo = fd.CarNoField()
    brand = fd.BrandField()

    carLicense = fd.CarLicenseField()
    license = fd.LicenseField()
    abbr = fd.AbbrField()
    imgs = fd.ImgsField()

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()


        