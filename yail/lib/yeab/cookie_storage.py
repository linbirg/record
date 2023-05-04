import base64
import json
from typing import Any, Callable, Optional, Union

from aiohttp import web
from cryptography import fernet
from cryptography.fernet import InvalidToken

from .session import AbstractStorage, Session
import logging

import datetime
import functools

log = logging.getLogger(__package__)


class DateEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")

        return super().default(o)


json.dumps = functools.partial(json.dumps, cls=DateEncoder)


class EncryptedCookieStorage(AbstractStorage):
    """Encrypted JSON storage.
    """
    def __init__(self,
                 secret_key: Union[str, bytes, bytearray],
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

        if isinstance(secret_key, str):
            pass
        elif isinstance(secret_key, (bytes, bytearray)):
            secret_key = base64.urlsafe_b64encode(secret_key)
        # TODO: Typing error fixed in https://github.com/pyca/cryptography/pull/5951
        self._fernet = fernet.Fernet(secret_key)  # type: ignore[arg-type]

    async def load_session(self, request: web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            try:
                data = self._decoder(
                    self._fernet.decrypt(cookie.encode('utf-8'),
                                         ttl=self.max_age).decode('utf-8'))
                return Session(None,
                               data=data,
                               new=False,
                               max_age=self.max_age)
            except InvalidToken:
                log.warning("Cannot decrypt cookie value, "
                            "create a new fresh session")
                return Session(None, data=None, new=True, max_age=self.max_age)

    async def save_session(self, request: web.Request,
                           response: web.StreamResponse,
                           session: Session) -> None:
        if session.empty:
            return self.save_cookie(response, '', max_age=session.max_age)

        cookie_data = self._encoder(
            self._get_session_data(session)).encode('utf-8')
        self.save_cookie(response,
                         self._fernet.encrypt(cookie_data).decode('utf-8'),
                         max_age=session.max_age)


class ExEncryptedCookieStorage(EncryptedCookieStorage):
    def __init__(self,
                 cookie_name: str = "AIOHTTP_SESSION",
                 domain: Optional[str] = None,
                 max_age: Optional[int] = None,
                 path: str = '/',
                 secure: Optional[bool] = None,
                 httponly: bool = True,
                 encoder: Callable[[object], str] = json.dumps,
                 decoder: Callable[[str], Any] = json.loads) -> None:

        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        super().__init__(secret_key,
                         cookie_name=cookie_name,
                         domain=domain,
                         max_age=max_age,
                         path=path,
                         secure=secure,
                         httponly=httponly,
                         encoder=encoder,
                         decoder=decoder)
