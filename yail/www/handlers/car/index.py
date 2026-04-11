from lib.yeab.web import get, post, ResponseBody, RequestBody
import aiohttp

from lib import logger
from www.common.message import Message
from www.handlers.vo.page import VoPage

from www.handlers.vo.vo_car_info import VoCarInfo
from www.dao.car_info import CarInfo
from www.dao.car_pics import CarPics

from conf.dev import PIC_DIR, PIC_URL


@get("/car/index")
@ResponseBody
async def index():
    return Message("ok!")


@post("/car/page")
@ResponseBody
@RequestBody("page", kls=VoPage)
async def page(page):
    e = int(page.currentPage) * int(page.pageSize)
    s = e - int(page.pageSize)

    cars = await CarInfo.find_all()

    return VoPage(carInfo=cars)


class SearchOptions:
    OP_CAR_NO = 1
    OP_NAME = 2
    OP_DEPT = 3
    OP_BRAND = 4

    options = [
        {
            "value": OP_CAR_NO,
            "label": "车牌号",
        },
        {
            "value": OP_NAME,
            "label": "姓名",
        },
        {
            "value": OP_DEPT,
            "label": "部门",
        },
        {
            "value": OP_BRAND,
            "label": "品牌",
        },
    ]

    @classmethod
    def op_to_column(cls, option):
        op_cols_dic = {1: "carNo", 2: "name", 3: "dept", 4: "brand"}

        return op_cols_dic[option]


@get("/car/search/options")
@ResponseBody
async def search_options():
    return SearchOptions.options


@post("/car/search")
@ResponseBody
@RequestBody("page", kls=VoPage)
async def search(page):
    cars = []
    if not page.query:
        cars = await CarInfo.find_all()
        return VoPage(carInfo=cars)

    option = SearchOptions.OP_CAR_NO
    if page.option:
        option = int(page.option)

    if (
        option == SearchOptions.OP_NAME
        or option == SearchOptions.OP_DEPT
        or option == SearchOptions.OP_BRAND
    ):
        col_name = SearchOptions.op_to_column(option)
        cars = await CarInfo.find(**{col_name: page.query})

    if option == SearchOptions.OP_CAR_NO:
        cars = await CarInfo.find_by_carno(page.query)

    return VoPage(carInfo=cars)


@post("/car/add")
@ResponseBody
@RequestBody("carInfo", kls=VoCarInfo)
async def add(carInfo):
    logger.LOG_INFO("test! carInfo.name=%s", carInfo.name)
    car = CarInfo()
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr

    await car.save()
    return Message("ok!")


@post("/car/update")
@ResponseBody
@RequestBody("carInfo", kls=VoCarInfo)
async def update(carInfo):
    logger.LOG_INFO("test! carInfo.name=%s", carInfo.name)
    car = await CarInfo.find_one(no=carInfo.no)
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr

    await car.update()
    return Message("ok!")


@post("/car/pic/upload")
@RequestBody("formData", kls=VoCarInfo)
async def upload(formData):
    logger.LOG_INFO("test! formData=%s", formData)
    name = formData.file.filename
    fullpath = "/".join([PIC_DIR, name])
    with open(fullpath, "wb") as f:
        data = formData.file.file.read()
        f.write(data)
        car = await CarInfo.find_one(no=formData.no)

        if car is None:
            raise aiohttp.HTTPError(500, "CarInfo not found")

        pic = CarPics(carID=car.no, path=name)
        await pic.save()

    return Message("ok!")


@post("/car/pic/filelist")
@ResponseBody
async def qry_filelist(no):
    pics = await CarPics.find(carID=no)
    if pics is None or len(pics) == 0:
        return []

    filelist = []

    for p in pics:
        url = PIC_URL + "/" + p.path
        img_resp = {"name": p.path, "url": url}

        filelist.append(img_resp)

    return filelist


@post("/car/pic/delete")
@ResponseBody
async def delete_pic(no, filename):
    logger.LOG_INFO("test! carInfo.no=%s", no)
    car = await CarInfo.find_one(no=no)

    if car is None:
        raise aiohttp.HTTPError(500, "CarInfo not found")

    pics = await CarPics.find(carID=car.no, path=filename)
    if pics is None or len(pics) == 0:
        logger.LOG_WARNING(f"Can not find car {no} pic:{filename}".format(no, filename))

        return Message("delete ok but not find pics.")

    for p in pics:
        await p.delete()

    return Message("ok!")


@post("/car/delete")
@ResponseBody
async def delete(no):
    logger.LOG_INFO("test! carInfo.no=%s", no)
    car = await CarInfo.find_one(no=no)

    await car.delete()
    return Message("ok!")
