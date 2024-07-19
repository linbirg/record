#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from conf import db as dbconf


from lib.yeab.web import add_routes, add_static, load_all_of_packages

from lib import yom as orm

import logging
logging.basicConfig(level=logging.INFO)

from aiohttp import web
from .session import setup
from .cookie_storage import ExEncryptedCookieStorage


class Yeab():
    def __init__(self,
                 host='127.0.0.1',
                 port=9000,
                 handlers='www.handlers',
                 filters_pkg=None):
        self.__loop = None
        self.__host = host
        self.__port = port
        self.__handlers = handlers
        self.__filters_pkg = filters_pkg
        self.__filters = []

        self.__server = None
        self.__app = None

        self.__after_request = []

    def _append_after_request(self):
        assert self.__app
        for fn in self.__after_request:
            self.__app.on_response_prepare.append(fn)

    @asyncio.coroutine
    def _start(self, loop):
        yield from orm.Pool.create_pool(loop=loop, **dbconf.rec_db)

        self.add_filters(self.__filters_pkg)
        self.__app = web.Application(loop=loop,client_max_size=1024**2*10)
        
        add_routes(self.__app, self.__handlers)

        setup(self.__app, ExEncryptedCookieStorage())

        for f in self.__filters:
            self.__app.middlewares.append(f)

        self._append_after_request()

        # add_static(self.__app)
        self.__server = yield from loop.create_server(
            self.__app.make_handler(), self.__host, self.__port)
        logging.info('server started at http://%s:%d...' %
                     (self.__host, self.__port))
        return self.__server

    def run(self):
        self.__loop = asyncio.get_event_loop()
        self.__loop.run_until_complete(self._start(self.__loop))
        self.__loop.run_forever()

    def _find_mod_filter(self, mod):
        fns = []
        for attr in dir(mod):
            if attr.startswith('_'):
                continue

            fn = getattr(mod, attr)
            if callable(fn):
                method = getattr(fn, '__yeap_filter__', None)
                if method:
                    fns.append(fn)

        return fns

    def add_filters(self, filters_pkg=None):
        if filters_pkg is None:
            return

        mods = load_all_of_packages(filters_pkg)

        if mods is None or len(mods) == 0:
            raise RuntimeError("cannot load mod!")

        for mod in mods:
            fns = self._find_mod_filter(mod)

            for fn in fns:
                self.add_filter(fn)

    def add_filter(self, fn):
        '''register a filter(middlware) '''
        self.__filters.append(fn)

    def after_request(self, fn):
        self.__after_request.append(fn)