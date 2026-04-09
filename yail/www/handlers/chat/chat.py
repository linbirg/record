#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Handler - 聊天处理器

集成:
- L1 Tool Result Budget 压缩
- L2 Microcompact 压缩
- L5 Auto Summarization
- 4类记忆系统
- 全局上下文管理
"""

from lib.yeab.web import post, stream, ResponseBody
from aiohttp import web
import asyncio
import json
import openai

from www.dao.chat_message import ChatMessage
from conf import dev as conf
from www.common.message import Message
from lib import logger

from .session_manager import (
    generate_session_id,
    init_global_structure,
    init_session_structure,
    session_exists,
    check_summarization_needed,
    check_summarization_debounce,
    run_summarization,
    estimate_tokens,
)
from .message_store import create_message_store
from .global_context import global_context_manager
from .memory_store import memory_store
from .memory_types import Memory, MemoryType, MemoryScope


_session_initialized = False


def ensure_sessions_initialized():
    """确保会话目录结构已初始化"""
    global _session_initialized
    if not _session_initialized:
        init_global_structure()
        _session_initialized = True


def ensure_session_exists(session_id: str, user_id: str):
    """确保 session 存在，不存在则创建"""
    if not session_exists(session_id):
        init_session_structure(session_id)
        global_context_manager.add_session(session_id)


@post("/chat/send_real")
@stream
async def chat_send_real(request):
    """
    真实的 AI 聊天处理器（带完整上下文管理）

    支持:
    - L1/L2/L5 压缩
    - 记忆提取和保存
    - 全局上下文更新
    """
    ensure_sessions_initialized()

    data = await request.json()
    user_id = str(data.get('userId', 'anonymous'))
    content = data.get('content', '')
    session_id = data.get('sessionId')

    if not session_id:
        session_id = generate_session_id(user_id)

    ensure_session_exists(session_id, user_id)

    msg_store = create_message_store(session_id)
    msg_store.save_user_message(content, {'user_id': user_id})

    messages = msg_store.load_messages()

    total_tokens = msg_store.get_total_tokens()
    delta_tokens = estimate_tokens(content)
    no_tool_rounds = msg_store.get_recent_tool_call_count()

    if check_summarization_needed(
        message_count=msg_store.get_message_count(),
        total_tokens=total_tokens,
        delta_tokens=delta_tokens,
        no_tool_call_rounds=no_tool_rounds,
    ):
        if check_summarization_debounce():
            asyncio.create_task(
                run_summarization(session_id, messages, user_id)
            )

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

    context = {
        'session_id': session_id,
        'user_id': user_id,
        'messages': messages,
        'global_context': global_context_manager.build_user_profile_prompt(),
    }

    try:
        async for chunk in call_llm_stream(context):
            event_data = json.dumps(chunk, ensure_ascii=False)
            await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))

        await resp.write(f"event: done\ndata: \n\n".encode('utf-8'))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_data = json.dumps({'error': str(e)}, ensure_ascii=False)
        await resp.write(f"event: error\ndata: {error_data}\n\n".encode('utf-8'))

    await resp.write_eof()
    return resp


async def call_llm_stream(context: dict) -> dict:
    """
    调用 LLM 流式 API（placeholder）
    后续需要集成真实的 MiniMax API
    """
    messages = context.get('messages', [])
    user_content = messages[-1]['content'] if messages else ''

    reasoning_content = "让我思考一下这个问题..."
    full_reasoning = ""
    for chunk in generate_chunks(reasoning_content, chunk_size=5):
        full_reasoning += chunk
        yield {'reasoning_content': full_reasoning, 'content': ''}
        await asyncio.sleep(0.05)

    await asyncio.sleep(0.2)

    response = f"你已经说了: {user_content}\n\n这是一个模拟回复。后续将集成真实的 MiniMax API。"
    full_content = ""
    for chunk in generate_chunks(response, chunk_size=10):
        full_content += chunk
        yield {'reasoning_content': full_reasoning, 'content': full_content}
        await asyncio.sleep(0.03)

    msg_store = create_message_store(context['session_id'])
    msg_store.save_assistant_message(
        content=full_content,
        reasoning_content=full_reasoning,
    )


def generate_chunks(text: str, chunk_size: int = 5) -> list:
    """将文本分割为小块"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


@post("/chat/send")
@stream
async def chat_send(request):
    """
    聊天发送入口（Mock/Real 切换）
    目前默认使用 mock_chat.py
    """
    ensure_sessions_initialized()

    from . import mock_chat
    return await mock_chat.mock_chat_send(request)


@post("/chat/history")
@ResponseBody
@asyncio.coroutine
def chat_history(userId, sessionId):
    """获取聊天历史"""
    ensure_sessions_initialized()

    if sessionId:
        msg_store = create_message_store(sessionId)
        messages = msg_store.load_messages()
        return {
            'messages': [
                {
                    'role': m['role'],
                    'content': m['content'],
                    'reasoning_content': m.get('reasoning_content'),
                    'timestamp': m.get('timestamp'),
                }
                for m in messages
            ],
            'sessionId': sessionId,
        }
    else:
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
    """清空聊天历史"""
    yield from ChatMessage.delete_by_session(userId, sessionId)
    return Message('success', True)


@post("/chat/memory/save")
@ResponseBody
async def chat_memory_save(request):
    """
    保存记忆

    Request:
    {
        "userId": "user123",
        "sessionId": "session_xxx",
        "type": "user|feedback|project|reference",
        "name": "记忆名称",
        "description": "记忆描述",
        "content": "记忆内容"
    }
    """
    ensure_sessions_initialized()

    data = await request.json()
    user_id = str(data.get('userId', 'anonymous'))
    session_id = data.get('sessionId')
    memory_type_str = data.get('type', 'user')
    name = data.get('name', '')
    description = data.get('description', '')
    content = data.get('content', '')

    try:
        memory_type = MemoryType.from_string(memory_type_str)
    except ValueError:
        return Message('error', f'Invalid memory type: {memory_type_str}')

    memory = Memory(
        name=name,
        description=description,
        type=memory_type,
        scope=MemoryScope.PRIVATE if memory_type in [MemoryType.USER, MemoryType.FEEDBACK] else MemoryScope.TEAM,
        content=content,
        source_sessions=[session_id] if session_id else [],
    )

    memory_store.save_memory(memory)

    return Message('success', True, {'memory_name': name})


@post("/chat/memory/list")
@ResponseBody
async def chat_memory_list(request):
    """
    获取记忆列表

    Request:
    {
        "userId": "user123",
        "type": "user|feedback|project|reference"
    }
    """
    ensure_sessions_initialized()

    data = await request.json()
    memory_type_str = data.get('type', 'user')

    try:
        memory_type = MemoryType.from_string(memory_type_str)
    except ValueError:
        return Message('error', f'Invalid memory type: {memory_type_str}')

    memories = memory_store.get_all_memories(memory_type)

    return Message('success', True, {
        'memories': [
            {
                'name': m.name,
                'description': m.description,
                'type': m.type.value,
                'scope': m.scope.value,
                'updated_at': m.updated_at,
            }
            for m in memories
        ]
    })


@post("/chat/context/global")
@ResponseBody
async def chat_context_global(request):
    """获取全局上下文"""
    ensure_sessions_initialized()

    ctx = global_context_manager.get_context()

    return Message('success', True, ctx.to_dict())


@post("/chat/session/init")
@ResponseBody
async def chat_session_init(request):
    """
    初始化新会话

    Request:
    {
        "userId": "user123"
    }
    """
    ensure_sessions_initialized()

    data = await request.json()
    user_id = str(data.get('userId', 'anonymous'))

    session_id = generate_session_id(user_id)
    init_session_structure(session_id)
    global_context_manager.add_session(session_id)

    return Message('success', True, {'sessionId': session_id})
