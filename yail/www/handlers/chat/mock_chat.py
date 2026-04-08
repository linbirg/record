#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Chat Handler - 用于前端开发和调试
不保存数据，纯模拟流式输出
"""

from lib.yeab.web import post, stream
from aiohttp import web
import asyncio
import json
import random


MOCK_RESPONSES = [
    "你好！很高兴为你服务。我是 ALOHA，一个基于 MiniMax 的 AI 助手。有什么问题都可以问我哦！",
    "关于这个问题，让我来帮你分析一下。首先，我们需要明确几个关键点，然后逐步来解决。",
    "这是一个很有趣的观点。从技术角度来看，这涉及到多个层面的知识，包括理论基础和实践应用。",
    "好的，让我来回答你的问题。根据我的理解，这个问题可以从以下几个方面来考虑：\n\n1. 首先了解基本概念\n2. 分析具体情况\n3. 制定解决方案\n4. 实施并优化",
    "谢谢你提问！让我详细解释一下：\n\n第一点：我们需要理解核心原理。\n第二点：实际应用中的注意事项。\n第三点：常见的误区和解决方法。",
    "我理解你的需求了。让我为你提供一个完整的解决方案，包含详细的步骤和说明。",
    "这个话题很有意思。让我分享一些我的看法：\n\n首先，我们需要了解基本概念。其次，分析实际情况。最后，给出具体建议。",
    "好的，让我来帮你处理这个问题。整个过程可以分为以下几个步骤：准备阶段、实施阶段、验证阶段。",
    "让我来帮你解答这个问题。从我的知识库中，我找到了相关的资料，请看下面的说明：\n\n重要内容已准备就绪，请仔细阅读。",
    "你好！很高兴在这里见到你。我可以帮你解答各种问题，包括但不限于技术、生活，学习等方面的话题。",
    "关于你说的这个情况，我有一些建议想要分享：\n\n首先，建议你先梳理一下具体需求。其次，我们可以一步步来实施方案。最后，记得及时总结经验。",
    "让我来给你详细说明一下这个过程。整个流程其实并不复杂，只需要按照以下步骤操作就可以了。",
    "这是一个很常见的问题，很多人都会遇到。让我来帮你分析一下原因，并提供相应的解决方案。",
    "好的，对于你提出的这个问题，我有以下几点看法：\n\n第一点：需要从整体角度来理解。\n第二点：注重细节和关键环节。\n第三点：持续优化和改进。",
    "让我来回答你的问题。我会尽量给出详细且实用的答案，如果有任何不明白的地方，欢迎继续提问。",
    "关于这个话题，我有一些独到的见解想要分享。总的来说，关键在于把握核心要点，并结合实际情况灵活运用。",
    "你好！看来你对这个问题很感兴趣。让我来帮你深入分析一下，从多个维度来理解这个话题。",
    "让我来帮你梳理一下思路。首先明确目标，其次分析现状，最后制定计划。这是一个系统性的思维过程。",
    "好的，让我来回答这个常见问题。整个过程可以分为三个主要阶段，每个阶段都有其重点和注意事项。",
]

MOCK_THINKING = [
    "让我仔细思考一下这个问题...",
    "正在分析你的问题...",
    "我需要考虑一下...",
    "让我整理一下思路...",
    "正在从多个角度分析...",
]


@post("/chat/send")
@stream
async def mock_chat_send(request):
    """Mock 流式聊天，不保存数据"""
    data = await request.json()
    user_id = data.get('userId')
    content = data.get('content', '')
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

    # 1. 先输出思考过程 (reasoning_content)
    thinking_text = random.choice(MOCK_THINKING)
    full_thinking = ""
    for chunk in generate_chunks(thinking_text, chunk_size=2):
        full_thinking += chunk
        event_data = json.dumps({
            'reasoning_content': full_thinking,
            'content': ''
        }, ensure_ascii=False)
        await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
        await asyncio.sleep(0.08)
    
    await asyncio.sleep(0.3)  # 思考停顿
    
    # 2. 再输出正式回复 (content)
    response_text = select_mock_response(content)
    full_content = ""
    for chunk in generate_chunks(response_text, chunk_size=3):
        full_content += chunk
        event_data = json.dumps({
            'reasoning_content': full_thinking,
            'content': full_content
        }, ensure_ascii=False)
        await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
        await asyncio.sleep(0.03)
    
    await resp.write(f"event: done\ndata: \n\n".encode('utf-8'))
    await resp.write_eof()
    return resp


def select_mock_response(user_input: str) -> str:
    """根据用户输入选择预设回复"""
    return random.choice(MOCK_RESPONSES)


def generate_chunks(text: str, chunk_size: int = 5) -> list:
    """将文本分割为小块，模拟流式"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
