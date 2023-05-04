# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr
'''
借鉴aiohttp_session的实现，结合自己思路，略作改动。
借鉴的地方在于，利用app来存储服务级别的数据，并通过aiohttp的midlware来实现加装到request中已方便使用.

希望使用方式：
1 使能:配置或者手动设置的方式
    setup(app,storage)

2 使用:
    eg:
    session = request.get_session()
'''

import abc
import json
import sys
import time
from typing import Any, Callable, Dict, Iterator, Mapping, MutableMapping, Optional, Union, cast

from aiohttp import web
# from aiohttp.web_middlewares import  _Handler, _Middleware

from lib import logger

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

SESSION_KEY = 'aiohttp_yeab_session'
STORAGE_KEY = 'aiohttp__yeab_session_storage'


class _CookieParams(TypedDict, total=False):
    domain: Optional[str]
    max_age: Optional[int]
    path: str
    secure: Optional[bool]
    httponly: bool
    expires: str


class _SessionData(TypedDict, total=False):
    created: int
    session: Dict[str, Any]


class Session(MutableMapping[str, Any]):
    """Session dict-like object."""
    def __init__(self,
                 identity: Optional[Any],
                 *,
                 data: Optional[Mapping[str, Any]],
                 new: bool,
                 max_age: Optional[int] = None) -> None:
        self._changed = False
        self._mapping: Dict[str, Any] = {}
        self._identity = identity if data != {} else None
        self._new = new if data != {} else True
        self._max_age = max_age
        created = data.get('created', None) if data else None
        session_data = data.get('session', None) if data else None
        now = int(time.time())
        age = now - created if created else now
        if max_age is not None and age > max_age:
            session_data = None
        if self._new or created is None:
            self._created = now
        else:
            self._created = created

        if session_data is not None:
            self._mapping.update(session_data)

    def __repr__(self) -> str:
        return '<{} [new:{}, changed:{}, created:{}] {!r}>'.format(
            self.__class__.__name__, self.new, self._changed, self.created,
            self._mapping)

    @property
    def new(self) -> bool:
        return self._new

    @property
    def identity(self) -> Optional[Any]:  # type: ignore[misc]
        return self._identity

    @property
    def created(self) -> int:
        return self._created

    @property
    def empty(self) -> bool:
        return not bool(self._mapping)

    @property
    def max_age(self) -> Optional[int]:
        return self._max_age

    @max_age.setter
    def max_age(self, value: Optional[int]) -> None:
        self._max_age = value

    def changed(self) -> None:
        self._changed = True

    def invalidate(self) -> None:
        self._changed = True
        self._mapping = {}

    def set_new_identity(self, identity: Optional[Any]) -> None:
        if not self._new:
            raise RuntimeError(
                "Can't change identity for a session which is not new")

        self._identity = identity

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping)

    def __contains__(self, key: object) -> bool:
        return key in self._mapping

    def __getitem__(self, key: str) -> Any:
        return self._mapping[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._mapping[key] = value
        self._changed = True

    def __delitem__(self, key: str) -> None:
        del self._mapping[key]
        self._changed = True


class AbstractStorage(metaclass=abc.ABCMeta):
    def __init__(self,
                 *,
                 cookie_name: str = "AIOHTTP_SESSION",
                 domain: Optional[str] = None,
                 max_age: Optional[int] = None,
                 path: str = '/',
                 secure: Optional[bool] = None,
                 httponly: bool = True,
                 encoder: Callable[[object], str] = json.dumps,
                 decoder: Callable[[str], Any] = json.loads) -> None:
        self._cookie_name = cookie_name
        self._cookie_params = _CookieParams(domain=domain,
                                            max_age=max_age,
                                            path=path,
                                            secure=secure,
                                            httponly=httponly)
        self._max_age = max_age
        self._encoder = encoder
        self._decoder = decoder

    @property
    def cookie_name(self) -> str:
        return self._cookie_name

    @property
    def max_age(self) -> Optional[int]:
        return self._max_age

    @property
    def cookie_params(self) -> _CookieParams:
        return self._cookie_params

    def _get_session_data(self, session: Session) -> _SessionData:
        if session.empty:
            return {}

        return {"created": session.created, "session": session._mapping}

    async def new_session(self) -> Session:
        return Session(None, data=None, new=True, max_age=self.max_age)

    @abc.abstractmethod
    async def load_session(self, request: web.Request) -> Session:
        pass

    @abc.abstractmethod
    async def save_session(self, request: web.Request,
                           response: web.StreamResponse,
                           session: Session) -> None:
        pass

    def load_cookie(self, request: web.Request) -> Optional[str]:
        # TODO: Remove explicit type anotation when aiohttp 3.8 is out
        cookie: Optional[str] = request.cookies.get(self._cookie_name)
        return cookie

    def save_cookie(self,
                    response: web.StreamResponse,
                    cookie_data: str,
                    *,
                    max_age: Optional[int] = None) -> None:
        params = self._cookie_params.copy()
        if max_age is not None:
            params['max_age'] = max_age
            t = time.gmtime(time.time() + max_age)
            params["expires"] = time.strftime("%a, %d-%b-%Y %T GMT", t)
        if not cookie_data:
            response.del_cookie(self._cookie_name,
                                domain=params["domain"],
                                path=params["path"])
        else:
            # Ignoring type for params until aiohttp#4238 is released
            response.set_cookie(self._cookie_name, cookie_data,
                                **params)  # type: ignore


class SimpleCookieStorage(AbstractStorage):
    """Simple JSON storage.
    Doesn't any encryption/validation, use it for tests only"""
    def __init__(self,
                 *,
                 cookie_name: str = "AIOHTTP_SESSION",
                 domain: Optional[str] = None,
                 max_age: Optional[int] = None,
                 path: str = '/',
                 secure: Optional[bool] = None,
                 httponly: bool = True,
                 encoder: Callable[[object], str] = json.dumps,
                 decoder: Callable[[str], Any] = json.loads) -> None:
        super().__init__(cookie_name=cookie_name,
                         domain=domain,
                         max_age=max_age,
                         path=path,
                         secure=secure,
                         httponly=httponly,
                         encoder=encoder,
                         decoder=decoder)

    async def load_session(self, request: web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)

        data = self._decoder(cookie)
        return Session(None, data=data, new=False, max_age=self.max_age)

    async def save_session(self, request: web.Request,
                           response: web.StreamResponse,
                           session: Session) -> None:
        cookie_data = self._encoder(self._get_session_data(session))
        self.save_cookie(response, cookie_data, max_age=session.max_age)


def _setup_request_attr(request):
    async def get_session(self):
        '''set request func get_session
        '''
        session = self.get(SESSION_KEY)
        if session is None:
            storage = self.get(STORAGE_KEY)
            if storage is None:
                raise RuntimeError("Install aiohttp_session middleware "
                                   "in your aiohttp.web.Application")

            session = await storage.load_session(self)
            if not isinstance(session, Session):
                raise RuntimeError(
                    "Installed {!r} storage should return session instance "
                    "on .load_session() call, got {!r}.".format(
                        storage, session))
            self[SESSION_KEY] = session
        return session

    if not hasattr(request, 'get_session'):
        # 2种绑定方法的方式,测试下来都ok
        request.get_session = get_session.__get__(request)
        # import types
        # request.get_session = types.MethodType(get_session, request)


def session_middleware(storage: 'AbstractStorage'):
    if not isinstance(storage, AbstractStorage):
        raise RuntimeError("Expected AbstractStorage got {}".format(storage))

    @web.middleware
    async def factory(request,
                      handler) -> web.StreamResponse:
        logger.LOG_INFO('5 session_middleware')
        print("request.cookies:", request.cookies)
        request[STORAGE_KEY] = storage

        _setup_request_attr(request)

        raise_response = False
        # TODO aiohttp 4: Remove Union from response, and drop the raise_response variable
        response: Union[web.StreamResponse, web.HTTPException]
        try:
            # TODO set scoffold
            response = await handler(request)
        except web.HTTPException as exc:
            response = exc
            raise_response = True
        if not isinstance(response, (web.StreamResponse, web.HTTPException)):
            raise RuntimeError("Expect response, not {!r}".format(
                type(response)))
        if not isinstance(response, (web.Response, web.HTTPException)):
            # likely got websocket or streaming
            return response
        if response.prepared:
            raise RuntimeError(
                "Cannot save session data into prepared response")
        session = request.get(SESSION_KEY)
        if session is not None:
            if session._changed:
                await storage.save_session(request, response, session)
        if raise_response:
            raise cast(web.HTTPException, response)
        return response

    return factory


def setup(app: web.Application, storage: 'AbstractStorage') -> None:
    """Setup the library in aiohttp fashion."""
    app.middlewares.append(session_middleware(storage))