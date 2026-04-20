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

    @classmethod
    async def add(cls, name: str, carNo: str, dept: str = "", brand: str = "",
                 carLicense: str = "", license: str = "", abbr: str = ""):
        car = cls()
        car.name = name
        car.carNo = carNo
        car.dept = dept
        car.brand = brand
        car.carLicense = carLicense
        car.license = license
        car.abbr = abbr
        await car.save()
        return car

    async def save_to_history(self):
        """保存当前记录到历史表"""
        from www.dao.car_history import CarInfoHistory

        history = CarInfoHistory()
        history.original_id = self.no
        history.user_name = self.name
        history.dept = self.dept
        history.carid = self.carNo
        history.brand = self.brand
        history.car_license = self.carLicense
        history.license = self.license
        history.abbr = self.abbr
        await history.save()
