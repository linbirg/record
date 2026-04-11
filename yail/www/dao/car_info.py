from . import field_desc as fd
from .base import AutoIdModel


class CarInfo(AutoIdModel):
    __table__ = "t_car_info"

    no = fd.IntField(name="id", primary_key=True, auto_increment=True)
    name = fd.UserNameField()
    dept = fd.DepartmentField()
    carNo = fd.CarNoField()
    brand = fd.BrandField()

    carLicense = fd.CarLicenseField()
    license = fd.LicenseField()
    abbr = fd.AbbrField()

    created_at = fd.CreatedAtField()
    updated_at = fd.UpdatedAtField()

    @classmethod
    async def find_by_carno(cls, val):
        args_val = (f"%{val}%".format(val),)

        where = "carid LIKE ?"

        rows = await cls.find_where(where, *args_val)
        return rows
