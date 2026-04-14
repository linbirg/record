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

from conf.dev import PIC_DIR, PIC_URL, OPENAI_API_KEY


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


VLM_API_HOST = "https://api.minimaxi.com"


async def call_vision(image_base64: str, prompt: str) -> str:
    # 如果已经有 data:image 前缀就直接使用，否则添加
    if image_base64.startswith('data:'):
        image_url = image_base64
    else:
        image_url = f"data:image/jpeg;base64,{image_base64}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{VLM_API_HOST}/v1/coding_plan/vlm",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "MM-API-Source": "Minimax-MCP"
                },
                json={
                    "prompt": prompt,
                    "image_url": image_url
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                data = await resp.json()
                if data.get("base_resp", {}).get("status_code") != 0:
                    logger.LOG_WARNING(f"VLM API error: {data.get('base_resp')}")
                    raise web.HTTPInternalServerError(text=data.get("base_resp", {}).get("status_msg", "VLM API error"))
                return data.get("content", "")
    except web.HTTPInternalServerError:
        raise
    except Exception as e:
        logger.LOG_WARNING(f"VLM API call failed: {e}")
        raise web.HTTPInternalServerError(text=f"VLM API call failed: {str(e)}")


@post("/car/ocr")
@ResponseBody
async def ocr(image: str, type: str):
    prompts = {
        "driving": "从行驶证图片中提取：姓名、车牌号、车辆品牌、型号、注册日期。只返回JSON格式：{\"name\":\"\",\"carNo\":\"\",\"brand\":\"\",\"model\":\"\",\"regDate\":\"\"}",
        "driver": "从驾驶证图片中提取：姓名。只返回JSON格式：{\"name\":\"\"}"
    }
    
    if type not in prompts:
        raise web.HTTPBadRequest(text="Invalid type")
    
    if not image:
        raise web.HTTPBadRequest(text="Image is required")
    
    content = await call_vision(image, prompts[type])
    
    if not content:
        raise web.HTTPInternalServerError(text="Empty response from VLM API")
    
    json_str = re.sub(r'```json\n?|```\n?', '', content).strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.LOG_WARNING(f"JSON parse error: {e}, content: {content}")
        raise web.HTTPInternalServerError(text=f"JSON parse error: {str(e)}")
