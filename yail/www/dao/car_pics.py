from . import field_desc as fd
from .base import AutoIdModel

# import asyncio

# import datetime


class CarPics(AutoIdModel):
    __table__ = "t_car_pics"

    no = fd.IntField(name='id', primary_key=True, auto_increment=True)

    carID = fd.IntField(name='car_id')

    path = fd.PicPathField()

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()
