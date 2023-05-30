from . import field_desc as fd
from .base import AutoIdModel

# import asyncio

# import datetime


class CarPics(AutoIdModel):
    __table__ = "t_car_pic"

    no = fd.IntField(name='id', primary_key=True, auto_increment=True)

    carNo = fd.CarNoField()

    path = fd.PicPathField()

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()
