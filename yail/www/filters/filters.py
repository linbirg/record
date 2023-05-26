#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

import asyncio
from aiohttp import web

import json

# from lib.yeab.config import before_request
from lib.yeab.web import ybfilter
from lib import logger

# COOKIE_NAME = 'yb_hello123www'


@ybfilter
@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logging(request):
        logger.LOG_INFO('1 Request: %s %s' % (request.method, request.path))
        return (yield from handler(request))

    return logging


@ybfilter
@asyncio.coroutine
def auth_factory(app, handler):
    @asyncio.coroutine
    def auth(request):
        logger.LOG_INFO('2 check user: %s %s' % (request.method, request.path))

        # if request.path in [
        #         '/login.action', '/user/submitUser.json', '/user/showUser'
        # ]:
        #     return (yield from handler(request))

        # session = yield from request.get_session()
        # user = session.get('user')
        # # print(user)

        # if user is None:
        #     return web.HTTPFound('/login.action')

        return (yield from handler(request))

    return auth


@ybfilter
@asyncio.coroutine
def data_factory(app, handler):
    @asyncio.coroutine
    def parse_data(request):
        logger.LOG_INFO('3 parse_data')
        if request.method == 'OPTIONS':
            # 处理OPTIONS请求
            return web.Response(status=200)

        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = yield from request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith(
                    'application/x-www-form-urlencoded'):
                request.__data__ = yield from request.post()
                logging.info('request form: %s' % str(request.__data__))

        return (yield from handler(request))

    return parse_data


@asyncio.coroutine
def cors(request, response):
    # print('response', response)
    origin = request.headers.get('Origin', None)
    if origin is not None:
        logging.info('origin:%s', origin)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers[
            "Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE"
        response.headers[
            "Access-Control-Allow-Headers"] = "Origin, No-Cache, X-Requested-With, If-Modified-Since, Pragma, Last-Modified, Cache-Control, Expires, Content-Type, X-E4M-With,userId,token"
        response.headers["Access-Control-Max-Age"] = "0"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["XDomainRequestAllowed"] = "1"

    return response


def debug_request(request):
    print("debug_request:", request)
    print(
        "|request.version:",
        request.version,
        "|request.method:",
        request.method,
        "|request.url:",
        request.url,
        "|request.rel_url:",
        request.rel_url,
        "|request.scheme:",
        request.scheme,
        "|request.secure:",
        request.secure,
        "|request.forwarded:",
        request.forwarded,
        "|request.host:",
        request.host,
        "|request.remote:",
        request.remote,
        "|request.path_qs:",
        request.path_qs,
        "|request.path:",
        request.path,
        "|request.raw_path:",
        request.raw_path,
        "|request.query:",
        request.query,
        "|request.query_string:",
        request.query_string,  #"|request.headers:", request.headers,
        #"|request.raw_headers:",
        #request.raw_headers,
        "|request.keep_alive:",
        request.keep_alive,
        "|request.transport:",
        request.transport,
        "|request.cookies:",
        request.cookies,
        "|request.content:",
        request.content,
        "|request.body_exists:",
        request.body_exists,
        "|request.can_read_body:",
        request.can_read_body,
        "|request.has_body:",
        request.has_body,
        "|request.content_type:",
        request.content_type,
        "|request.charset:",
        request.charset,
        "|request.content_length:",
        request.content_length,
        "|request.config_dict:",
        request.config_dict,
        "|request.match_info",
        request.match_info)


@ybfilter
@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        logger.LOG_INFO('4 Response handler...')
        debug_request(request)
        r = yield from handler(request)
        resp = r

        if isinstance(r, web.StreamResponse):
            return r

        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp

        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp

        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(
                    r, ensure_ascii=False,
                    default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                r['__user__'] = request.__user__
                resp = web.Response(
                    body=app['__templating__'].get_template(template).render(
                        **r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp

        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))

        if isinstance(r, int) and t >= 100 and t < 600:
            return web.Response(t)

        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'

        return resp

    return response
