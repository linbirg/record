from lib.yeab.web import get, post, ResponseBody, RequestBody
from aiohttp import web
import aiohttp
import re
import json
import base64
import time
import os

from lib import logger
from www.common.message import Message
from www.handlers.vo.page import VoPage

from www.handlers.vo.vo_car_info import VoCarInfo
from www.dao.car_info import CarInfo
from www.dao.car_pics import CarPics

from conf.dev import PIC_DIR, PIC_URL
from lib.ocr import create_ocr_engine


def decode_base64_image(img_str):
    """解码 base64 图片，去掉 data:image 前缀"""
    if img_str and img_str.startswith('data:'):
        img_str = img_str.split(',')[1]
    return base64.b64decode(img_str)


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
    
    timestamp = int(time.time())
    
    driving_filename = None
    driver_filename = None
    
    if carInfo.drivingLicense:
        driving_filename = f"{carInfo.name}_{timestamp}_行驶证.jpg"
        driving_path = "/".join([PIC_DIR, driving_filename])
        with open(driving_path, "wb") as f:
            f.write(decode_base64_image(carInfo.drivingLicense))
    
    if carInfo.driverLicense:
        driver_filename = f"{carInfo.name}_{timestamp}_驾驶证.jpg"
        driver_path = "/".join([PIC_DIR, driver_filename])
        with open(driver_path, "wb") as f:
            f.write(decode_base64_image(carInfo.driverLicense))
    
    car = CarInfo()
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr

    await car.save()
    
    if driving_filename:
        pic1 = CarPics(carID=car.no, path=driving_filename)
        await pic1.save()
    if driver_filename:
        pic2 = CarPics(carID=car.no, path=driver_filename)
        await pic2.save()
    
    msg = Message("ok!")
    msg.data = {"no": car.no}
    return msg


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
@RequestBody("request")
async def upload(request):
    logger.LOG_INFO("upload called")
    post_data = await request.post()
    name = post_data.get("filename") or post_data["file"].filename
    no = post_data.get("no")
    fullpath = "/".join([PIC_DIR, name])
    with open(fullpath, "wb") as f:
        data = post_data["file"].file.read()
        f.write(data)
        car = await CarInfo.find_one(no=no)

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
    car = await CarInfo.find_one(no=no)
    if not car:
        return Message("ok!")
    
    pics = await CarPics.find(carID=car.no)
    for p in pics:
        pic_path = "/".join([PIC_DIR, p.path])
        if os.path.exists(pic_path):
            os.remove(pic_path)
        await p.delete()
    
    await car.delete()
    return Message("ok!")


@post("/car/ocr")
@ResponseBody
async def ocr(image: str, type: str = None, engine: str = None):
    logger.LOG_INFO("OCR request: type=%s, engine=%s, image_length=%d", type, engine, len(image) if image else 0)
    
    if not type:
        logger.LOG_WARNING("OCR error: missing type parameter")
        raise web.HTTPBadRequest(text="Missing type parameter")
    
    if type not in ("driving", "driver"):
        logger.LOG_WARNING("OCR error: invalid type=%s", type)
        raise web.HTTPBadRequest(text="Invalid type: " + str(type) + ", must be 'driving' or 'driver'")
    
    if engine and engine not in ("paddleocr", "minimax"):
        logger.LOG_WARNING("OCR error: invalid engine=%s", engine)
        raise web.HTTPBadRequest(text="Invalid engine: " + str(engine) + ", must be 'paddleocr' or 'minimax'")
    
    if not image:
        logger.LOG_WARNING("OCR error: missing image parameter")
        raise web.HTTPBadRequest(text="Image is required")
    
    try:
        ocr_engine = create_ocr_engine(engine)
        engine_name = ocr_engine.__class__.__name__
        logger.LOG_INFO("Using OCR engine: %s", engine_name)
        
        if type == "driving":
            result = await ocr_engine.recognize_driving_license(image)
        else:
            result = await ocr_engine.recognize_driver_license(image)
        
        logger.LOG_INFO("OCR result: %s", str(result))
        return result
    except ValueError as e:
        logger.LOG_WARNING("OCR ValueError: %s", str(e))
        raise web.HTTPBadRequest(text=str(e))
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.LOG_WARNING("OCR failed: %s\n%s", str(e), error_msg)
        raise web.HTTPInternalServerError(text="OCR failed: " + str(e))
