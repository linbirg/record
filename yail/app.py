#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'linbirg'
'''
async web application.
在廖老师的web框架基础上修改而来，感谢廖老师。
'''

import logging
logging.basicConfig(level=logging.INFO)

# import asyncio, time
# from datetime import datetime

# from jinja2 import Environment, FileSystemLoader

# from conf import db as dbconf

# from lib.yeab.web import add_routes, add_static

from www.filters.filters import cors

from lib.yeab.yeab import Yeab

# from handlers import cookie2user, COOKIE_NAME

# def init_jinja2(app, **kw):
#     logging.info('init jinja2...')
#     options = dict(
#         autoescape = kw.get('autoescape', True),
#         block_start_string = kw.get('block_start_string', '{%'),
#         block_end_string = kw.get('block_end_string', '%}'),
#         variable_start_string = kw.get('variable_start_string', '{{'),
#         variable_end_string = kw.get('variable_end_string', '}}'),
#         auto_reload = kw.get('auto_reload', True)
#     )
#     path = kw.get('path', None)
#     if path is None:
#         path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
#     logging.info('set jinja2 template path: %s' % path)
#     env = Environment(loader=FileSystemLoader(path), **options)
#     filters = kw.get('filters', None)
#     if filters is not None:
#         for name, f in filters.items():
#             env.filters[name] = f
#     app['__templating__'] = env

# def datetime_filter(t):
#     delta = int(time.time() - t)
#     if delta < 60:
#         return u'1分钟前'
#     if delta < 3600:
#         return u'%s分钟前' % (delta // 60)
#     if delta < 86400:
#         return u'%s小时前' % (delta // 3600)
#     if delta < 604800:
#         return u'%s天前' % (delta // 86400)
#     dt = datetime.fromtimestamp(t)
#     return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

if __name__ == "__main__":
    app = Yeab(filters_pkg='www.filters')
    app.after_request(cors)
    app.run()