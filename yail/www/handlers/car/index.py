import asyncio

from lib.yeab.web import get, post, ResponseBody, RequestBody
import aiohttp

from lib import logger
from www.common.message import Message
from www.handlers.vo.page import VoPage

from www.handlers.vo.vo_car_info import VoCarInfo
from www.dao.car_info import CarInfo
from www.dao.car_pics import CarPics

from conf.dev import PIC_DIR, PIC_URL


@get('/car/index')
@ResponseBody
@asyncio.coroutine
def index():
    return Message('ok!')


@post('/car/page')
@ResponseBody
@RequestBody('page', kls=VoPage)
@asyncio.coroutine
def page(page):
    e = int(page.currentPage) * int(page.pageSize)
    s = e - int(page.pageSize)

    cars = yield from CarInfo.find_all()

    return VoPage(carInfo=cars)


class SearchOptions:
    OP_CAR_NO = 1
    OP_NAME = 2
    OP_DEPT = 3
    OP_BRAND = 4

    options = [{
        "value": OP_CAR_NO,
        "label": "车牌号",
    }, {
        "value": OP_NAME,
        "label": "姓名",
    }, {
        "value": OP_DEPT,
        "label": "部门",
    }, {
        "value": OP_BRAND,
        "label": "品牌",
    }]

    @classmethod
    def op_to_column(cls, option):
        op_cols_dic = {1: 'carNo', 2: 'name', 3: 'dept', 4: 'brand'}

        return op_cols_dic[option]


@get('/car/search/options')
@ResponseBody
@asyncio.coroutine
def search_options():
    return SearchOptions.options


@post('/car/search')
@ResponseBody
@RequestBody('page', kls=VoPage)
@asyncio.coroutine
def search(page):
    # print(page.option, page.query, True if page.query else False)
    cars = []
    if not page.query:
        cars = yield from CarInfo.find_all()
        return VoPage(carInfo=cars)

    option = SearchOptions.OP_CAR_NO  # default search by car number.
    if page.option:
        option = int(page.option)

    if option == SearchOptions.OP_NAME or option == SearchOptions.OP_DEPT or option == SearchOptions.OP_BRAND:
        col_name = SearchOptions.op_to_column(option)
        cars = yield from CarInfo.find(**{col_name: page.query})

    if option == SearchOptions.OP_CAR_NO:
        cars = yield from CarInfo.find_by_carno(page.query)
        # print('carNo', page.query, len(cars))

    return VoPage(carInfo=cars)


@post('/car/add')
@ResponseBody
@RequestBody('carInfo', kls=VoCarInfo)
@asyncio.coroutine
def add(carInfo):
    logger.LOG_INFO('test! carInfo.name=%s', carInfo.name)
    car = CarInfo()
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr

    yield from car.save()
    return Message('ok!')


@post('/car/update')
@ResponseBody
@RequestBody('carInfo', kls=VoCarInfo)
@asyncio.coroutine
def update(carInfo):
    logger.LOG_INFO('test! carInfo.name=%s', carInfo.name)
    car = yield from CarInfo.find_one(no=carInfo.no)
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr

    yield from car.update()
    return Message('ok!')


@post('/car/pic/upload')
# @ResponseBody
@RequestBody('formData', kls=VoCarInfo)
@asyncio.coroutine
def upload(formData):
    logger.LOG_INFO('test! formData=%s', formData)
    name = formData.file.filename
    fullpath = '/'.join([PIC_DIR, name])
    with open(fullpath, 'wb') as f:
        data = formData.file.file.read()
        f.write(data)
        # add_file
        car = yield from CarInfo.find_one(no=formData.no)

        if car is None:
            raise aiohttp.HTTPError(500, 'CarInfo not found')

        pic = CarPics(carID=car.no, path=name)
        yield from pic.save()

        # imgs_str = car.imgs if car.imgs else ''
        # car.imgs = imgs_str + ';' + name if imgs_str else name

        # yield from car.update()

    return Message('ok!')


@post('/car/pic/filelist')
@ResponseBody
@asyncio.coroutine
def qry_filelist(no):
    # car = yield from CarInfo.find_one(no=no)

    # imgs = car.imgs

    # if imgs is None:
    # return []

    pics = yield from CarPics.find(carID=no)
    if pics is None or len(pics) == 0:
        return []

    # img_list = imgs.split(';')

    filelist = []

    for p in pics:
        # url = '/static/car/' + p.path
        url = PIC_URL + '/' + p.path
        img_resp = {'name': p.path, 'url': url}

        filelist.append(img_resp)

    return filelist


@post('/car/pic/delete')
@ResponseBody
@asyncio.coroutine
def delete_pic(no, filename):
    logger.LOG_INFO('test! carInfo.no=%s', no)
    car = yield from CarInfo.find_one(no=no)

    if car is None:
        raise aiohttp.HTTPError(500, 'CarInfo not found')

    pics = yield from CarPics.find(carID=car.no, path=filename)  # 找到car的图片
    if pics is None or len(pics) == 0:
        logger.LOG_WARNING(f"Can not find car {no} pic:{filename}".format(
            no, filename))

        return Message('delete ok but not find pics.')

    for p in pics:
        yield from p.delete()

    return Message('ok!')

    


@post('/car/delete')
@ResponseBody
@asyncio.coroutine
def delete(no):
    logger.LOG_INFO('test! carInfo.no=%s', no)
    car = yield from CarInfo.find_one(no=no)

    yield from car.delete()
    return Message('ok!')