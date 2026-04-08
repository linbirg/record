#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yeab.web import post, stream, ResponseBody
from aiohttp import web
import asyncio
import json
import openai

from www.dao.chat_message import ChatMessage
from conf import dev as conf
from www.common.message import Message
from lib import logger


# @post("/chat/send_real")
# @stream
# async def chat_send(request):
#     # TODO: 修复 yield from 与 async def 混用问题
#     # 当前使用 mock_chat.py 作为 Mock
#     pass


@post("/chat/history")
@ResponseBody
@asyncio.coroutine
def chat_history(userId, sessionId):
    messages = yield from ChatMessage.find_by_session(userId, sessionId)
    return {
        'messages': [
            {'role': m.role, 'content': m.content, 'createdAt': str(m.created_at)}
            for m in messages
        ]
    }


@post("/chat/clear")
@ResponseBody
@asyncio.coroutine
def chat_clear(userId, sessionId):
    yield from ChatMessage.delete_by_session(userId, sessionId)
    return Message('success', True)
