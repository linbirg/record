import asyncio

from lib.yeab.web import get, post, ResponseBody, RequestBody
import aiohttp

from lib import logger
from www.common.message import Message
from www.handlers.vo.page import VoPage

from www.handlers.vo.vo_car_info import VoCarInfo
from www.dao.car_info import CarInfo
from www.dao.car_pics import CarPics

from conf.dev import PIC_DIR


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

    return {
        'page': {
            'totalItem': 10,
            'currentPage': 1,
            'pageSize': 10
        },
        'carInfo': cars
    }

    # return {'page': {'totalItem': 1}, 'carInfo': [{'no':1,'dept':'综合','name':'路人甲','carNo':'沪ADN3689','brand':'TESLA','carlicense':'ABCDEF4536','license':'ABCDEF4536','abbr':''},
    #               {'no':3,'dept':'技术运维保障部','name':'路人乙','carNo':'沪ADN3355','brand':'TESLA','carlicense':'ABCDEF4536','license':'ABCDEF4536','abbr':''}]}


@post('/car/search')
@ResponseBody
@RequestBody('page', kls=VoPage)
@asyncio.coroutine
def search(page):
    print(page)
    cars = yield from CarInfo.find_all()

    return {
        'page': {
            'totalItem': 10,
            'currentPage': 1,
            'pageSize': 10
        },
        'carInfo': cars
    }


@get('/car/search/options')
@ResponseBody
@asyncio.coroutine
def search_options():
    return [
        {
            "value": "1",
            "label": "车牌号",
        },
        {
            "value": "2",
            "label": "姓名",
        },
        {
            "value": "3",
            "label": "部门",
        },
        {
            "value": "4",
            "label": "品牌",
        }
    ]


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
        url = '/static/car/' + p.path
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

    pic = yield from CarPics.find(carID=car.no, path=filename)  # 找到car的图片
    if pic is None:
        logger.LOG_WARNING(f"Can not find car {no} pic:{filename}".format(
            no, filename))

        return Message('ok!')

    yield from pic.delete()

    return Message('ok!')

    # imgs_str = car.imgs if car.imgs else ''  # 保留原始图片名称或空字符串
    # del_str = filename
    # if filename + ';' in imgs_str:
    #     del_str = f'{filename};'.format(filename)

    # imgs_str = imgs_str.replace(del_str, '')

    # car.imgs = imgs_str

    # yield from car.update()


@post('/car/delete')
@ResponseBody
@asyncio.coroutine
def delete(no):
    logger.LOG_INFO('test! carInfo.no=%s', no)
    car = yield from CarInfo.find_one(no=no)

    yield from car.delete()
    return Message('ok!')