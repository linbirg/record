
import asyncio

from lib.yeab.web import get, post, ResponseBody,RequestBody

from lib import logger
from www.common.message import Message
from www.handlers.vo.page import VoPage

from www.handlers.vo.vo_car_info import VoCarInfo
from www.dao.car_info import CarInfo

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
    e = int(page.currentPage)*int(page.pageSize)
    s = e - int(page.pageSize)

    cars = yield from CarInfo.find_all()

    return {'page': {'totalItem': 10,'currentPage':1,'pageSize':10}, 'carInfo': cars}


    # return {'page': {'totalItem': 1}, 'carInfo': [{'no':1,'dept':'综合','name':'路人甲','carNo':'沪ADN3689','brand':'TESLA','carlicense':'ABCDEF4536','license':'ABCDEF4536','abbr':''},
    #               {'no':3,'dept':'技术运维保障部','name':'路人乙','carNo':'沪ADN3355','brand':'TESLA','carlicense':'ABCDEF4536','license':'ABCDEF4536','abbr':''}]}

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
    fullpath = '/'.join([PIC_DIR,name]) 
    with open(fullpath,'wb') as f:
        data = formData.file.file.read()
        f.write(data)
        # add_file
        car = yield from CarInfo.find_one(no=formData.no)
        imgs_str = car.imgs if car.imgs else ''
        car.imgs  = imgs_str + ';' + name if imgs_str else name

        yield from car.update()
    
    return Message('ok!')



@post('/car/pic/filelist')
@ResponseBody
@asyncio.coroutine
def qry_filelist(no):
    car = yield from CarInfo.find_one(no=no)

    imgs = car.imgs

    if imgs is None:
        return []

    img_list = imgs.split(';')

    filelist = []

    for img in img_list:
        url = '/static/car/' + img
        img_resp = {'name':img,'url':url}

        filelist.append(img_resp)

    
    return filelist

@post('/car/delete')
@ResponseBody
@asyncio.coroutine
def delete(no):
    logger.LOG_INFO('test! carInfo.no=%s', no)
    car = yield from CarInfo.find_one(no=no)

    yield from car.delete()
    return Message('ok!')