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


@post("/chat/send")
@stream
async def chat_send(request):
    data = await request.json()
    user_id = data.get('userId')
    content = data.get('content')
    session_id = data.get('sessionId', str(user_id))

    resp = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )
    await resp.prepare(request)

    history = await ChatMessage.find_by_session(
        user_id, session_id, conf.OPENAI_MAX_HISTORY
    )
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": content})

    user_msg = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        role='user',
        content=content
    )
    yield from user_msg.save()

    full_content = ""
    try:
        client = openai.OpenAI(
            api_key=conf.OPENAI_API_KEY,
            base_url=conf.OPENAI_BASE_URL
        )
        stream_resp = client.chat.completions.create(
            model=conf.OPENAI_MODEL,
            messages=messages,
            stream=True
        )

        for chunk in stream_resp:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                full_content += delta['content']
                event_data = json.dumps({'content': full_content}, ensure_ascii=False)
                await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))

    except Exception as e:
        logger.LOG_ERROR(f"OpenAI API error: {e}")
        error_data = json.dumps({'error': str(e)}, ensure_ascii=False)
        await resp.write(f"event: error\ndata: {error_data}\n\n".encode('utf-8'))

    if full_content:
        ai_msg = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role='assistant',
            content=full_content
        )
        yield from ai_msg.save()

    await resp.write(f"event: done\ndata: \n\n".encode('utf-8'))
    await resp.write_eof()

    return resp


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
