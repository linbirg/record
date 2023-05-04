#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
原作者： 'Michael Liao'
编辑修改：linbirg
在Michael Liao异步coroweb的基础上，尝试部分修改，尽量使其独立、好用
'''

import asyncio, os, inspect, logging, functools
import json

from urllib import parse

import importlib
# import importlib.util

from aiohttp import web

from .apis import APIError

from lib import logger


class BadRequestError(Exception):
    '''
    diff from web.HTTPBadRequest, when catched a BadRequestError, handler can return a HTTPBadRequest
    '''
    def __init__(self, message=''):
        super().__init__(message)


def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator


def ybfilter(func):
    '''
    Define filter
    '''
    @functools.wraps(func)
    def wrapper(*args, **kw):
        return func(*args, **kw)

    wrapper.__yeap_filter__ = 'yeap_filter'
    return wrapper


class RequestBody():
    '''从request中解析json为参数'''
    # TODO 暂时还不确定，是否是有次注解了之后，不会再有其他参数

    REQUEST_BODY_ATTR = '__request_body_arg__'
    REQUEST_BODY_ATTR_TYPE = '__request_body_type__'

    def __init__(self, name, kls=None):
        self.name = name
        self.kls = kls

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)

            return func(*args, **kwargs)

        print("setattr", self.REQUEST_BODY_ATTR, self.name)
        setattr(wrapped_function, self.REQUEST_BODY_ATTR, self.name)
        wrapped_function.__request_body_arg__ = self.name
        if self.kls is not None:
            setattr(wrapped_function, self.REQUEST_BODY_ATTR_TYPE, self.kls)

        return wrapped_function


def ResponseBody(coro):
    '''以json形式传递数据'''
    @functools.wraps(coro)
    @asyncio.coroutine
    def decorator(*args, **kwargs):
        r = yield from coro(*args, **kwargs)
        # resp = web.json_response(r)
        resp = web.Response(
            body=json.dumps(r, ensure_ascii=False).encode('utf-8'))
        resp.content_type = 'application/json;charset=utf-8'

        return resp

    return decorator


def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY or param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            args.append(name)

    logger.LOG_TRACE('func %s has args %s', fn.__name__, args)
    return tuple(args)


def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        # KEYWORD_ONLY和POSITIONAL_OR_KEYWORD作同一类参数处理
        if param.kind == inspect.Parameter.KEYWORD_ONLY or param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            return True

    return False


def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

    return False


def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        # print(name, param.name, param.default, param.annotation, param.kind)
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL
                      and param.kind != inspect.Parameter.KEYWORD_ONLY
                      and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                'request parameter must be the last named parameter in function: %s%s'
                % (fn.__name__, str(sig)))
    return found


@asyncio.coroutine
def parse_post_param(request):
    if not request.content_type:
        raise BadRequestError('Missing Content-Type.')

    ct = request.content_type.lower()

    if ct.startswith('application/json'):
        params = yield from request.json()
        if not isinstance(params, dict):
            raise BadRequestError('JSON body must be object.')

        return params

    if ct.startswith('application/x-www-form-urlencoded') or ct.startswith(
            'multipart/form-data') or ct.startswith(
                'application/octet-stream'):
        params = yield from request.post()
        return dict(**params)

    raise BadRequestError('Unsupported Content-Type:%s' % ct)


class RequestHandler(object):
    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    @asyncio.coroutine
    def __parse_args(self, request):
        print("fn:", self._func.__name__, "|_has_request_arg:",
              self._has_request_arg, "|_has_var_kw_arg:", self._has_var_kw_arg,
              "|_has_named_kw_args:", self._has_named_kw_args,
              "|_named_kw_args", self._named_kw_args, "|_required_kw_args:",
              self._required_kw_args)

        if not (self._has_var_kw_arg or self._has_named_kw_args
                or self._has_request_arg):
            logger.LOG_INFO('%s has no args' % self._func.__name__)
            return {}

        kw = {}

        # 廖老师这段代码，对于默认的“application/octet-stream”无法解析参数
        # 准备按照以下逻辑查找：
        # 1 request.query 2 request.query_string
        # check all args find if not
        # 3 if post check content type and parse body
        # 4 未找到的参数，给默认

        args = self._named_kw_args + self._required_kw_args

        query_dict = request.query

        if query_dict is None or len(query_dict) == 0:
            qs = request.query_string
            if qs:
                query_dict = dict()
                for k, v in parse.parse_qs(qs, True).items():
                    query_dict[k] = v[0]

        post_params = None

        for name in args:
            if name in query_dict:
                kw[name] = query_dict[name]
                continue

            if name in request.match_info:
                kw[name] = request.match_info[name]
                continue

            if not name in query_dict:
                if post_params is None and request.method == 'POST':
                    post_params = yield from parse_post_param(request)

                if post_params is None:
                    logger.LOG_WARNING('no post parameters.')
                    continue

                if name in post_params:
                    kw[name] = post_params[name]
                    continue

        if self._has_request_arg:
            kw['request'] = request
        # # check required kw:
        if self._has_request_arg:
            for name in self._required_kw_args:
                if not name in kw:
                    raise BadRequestError('Missing argument: %s' % name)

        logger.LOG_INFO('call with args: %s' % str(kw))

        return kw

        #
        # if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
        #     if request.method == 'POST':
        #         if not request.content_type:
        #             raise BadRequestError('Missing Content-Type.')

        #         ct = request.content_type.lower()

        #         if ct.startswith('application/json'):
        #             params = yield from request.json()
        #             if not isinstance(params, dict):
        #                 raise BadRequestError('JSON body must be object.')
        #             kw = params
        #         elif ct.startswith(
        #                 'application/x-www-form-urlencoded') or ct.startswith(
        #                     'multipart/form-data') or ct.startswith(
        #                         'application/octet-stream'):
        #             params = yield from request.post()
        #             kw = dict(**params)
        #         else:
        #             raise BadRequestError('Unsupported Content-Type:%s' % ct)
        #     if request.method == 'GET':
        #         print("debug2")
        #         qs = request.query_string
        #         if qs:
        #             kw = dict()
        #             for k, v in parse.parse_qs(qs, True).items():
        #                 kw[k] = v[0]
        # if kw is None:
        #     print("debug3")
        #     kw = dict(**request.match_info)
        # else:
        #     if not self._has_var_kw_arg and self._named_kw_args:
        #         print("debug4")
        #         print(kw)
        #         # remove all unamed kw:
        #         copy = dict()
        #         for name in self._named_kw_args:
        #             if name in kw:
        #                 copy[name] = kw[name]
        #         kw = copy
        #     # check named arg:
        #     for k, v in request.match_info.items():
        #         print("debug5")
        #         if k in kw:
        #             logging.warning(
        #                 'Duplicate arg name in named arg and kw args: %s' % k)
        #         kw[k] = v
        # if self._has_request_arg:
        #     kw['request'] = request
        # # check required kw:
        # if self._required_kw_args:
        #     print("debug6")
        #     for name in self._required_kw_args:
        #         if not name in kw:
        #             return web.HTTPBadRequest('Missing argument: %s' % name)

    def _make_response(self, r, request):
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
                # r['__user__'] = request.__user__
                resp = web.Response(
                    body=self._app['__templating__'].get_template(
                        template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp

        # TODO 下面代码有问题，待确认
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))

        if isinstance(r, int) and t >= 100 and t < 600:
            return web.Response(t)

        # default:
        # 默认按json传递数据 TODO 确定是否合适，是否有其他选择
        resp = web.Response(
            body=json.dumps(r, ensure_ascii=False).encode('utf-8'))
        resp.content_type = 'application/json;charset=utf-8'
        # resp = web.Response(body=r)
        # resp.content_type = 'text/plain;charset=utf-8'

        return resp

    def get_request_body(self):
        name = getattr(self._func, RequestBody.REQUEST_BODY_ATTR, None)
        kls = getattr(self._func, RequestBody.REQUEST_BODY_ATTR_TYPE, None)

        return name, kls

    def has_request_body(self):
        name, _ = self.get_request_body()
        return not name == None

    @asyncio.coroutine
    def __call__(self, request):

        kw = {}

        if self.has_request_body():
            name, kls = self.get_request_body()
            post_arg = yield from parse_post_param(request)

            if kls:
                post_arg = kls(**post_arg)

            kw[name] = post_arg

        try:
            if self._has_var_kw_arg or self._has_named_kw_args or self._has_request_arg:
                args = yield from self.__parse_args(request)

                if args is not None and len(args) > 0:
                    kw = {**kw, **args}
        except BadRequestError as e:
            return web.HTTPBadRequest(e.message)

        try:
            r = yield from self._func(**kw)
            rsp = self._make_response(r, request)
            return rsp
        except APIError as e:
            error = dict(error=e.error, data=e.data, message=e.message)
            return self._make_response(error, request)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(
            fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' %
                 (method, path, fn.__name__, ', '.join(
                     inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} not found".format(module_name))
        return None
    else:
        print("Module: {} can be imported".format(module_name))
        return module_spec


def import_module_from_spec(module_spec):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    module = importlib.util.module_from_spec(module_spec)

    module_spec.loader.exec_module(module)
    return module


def find_abs_modules_of_pkg(package):
    modules = []
    for path in package.__path__:
        for root, dirname, filename in os.walk(path):
            # print(root,dirname,filename)

            for fn in filename:
                if fn == "__init__.py" or fn == "__init__.pyc":
                    continue

                if not fn.split('.')[1] == "py":
                    # 不是py文件，跳过
                    continue

                name = fn.split('.')[0]

                root_name = root.split(path)[1]

                if root_name != '':
                    root_name = '.'.join(root_name.split(os.path.sep))
                    modname = package.__name__ + root_name + "." + name
                else:
                    modname = package.__name__ + "." + name

                spec = check_module(modname)
                module = import_module_from_spec(spec)
                modules.append(module)

    return modules


def load_all_of_packages(package_or_module):
    '''package: 包或者名字'''
    if type(package_or_module) == str:
        module_spec = check_module(package_or_module)
        package_or_module = import_module_from_spec(module_spec)

    path = getattr(package_or_module, '__path__', None)
    if path is not None:
        modules = find_abs_modules_of_pkg(package_or_module)
        return modules

    return [package_or_module]


def mod_loader(mdl_name):
    module_spec = check_module(mdl_name)
    if module_spec:
        module = import_module_from_spec(module_spec)
        return module
    return None


def _find_mod_fn(mod):
    '''查找模块中所有有注解的方法'''
    fns = []
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                fns.append(fn)

    return fns


def add_routes(app, package_name):
    '''
    package_name:可以是包的名称、模块的名称、包或者模块。一般为包名。
    函数实现扫描功能，会扫描包下面所有的模块、包或者命名空间，将所有有路径注解的方法注册到路由中。
    '''

    mods = load_all_of_packages(package_name)

    if mods is None or len(mods) == 0:
        raise RuntimeError("cannot load mod!")

    for mod in mods:
        fns = _find_mod_fn(mod)

        for fn in fns:
            add_route(app, fn)
