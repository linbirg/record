#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager - 会话管理模块
负责 session_id 生成、目录结构初始化、全局上下文管理、L1/L2/L5 压缩
"""

import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from conf import dev as conf

from .tool_result_budget import truncate_tool_result
from .microcompact import compact_tool_calls


def generate_session_id(user_id: str) -> str:
    """
    生成 session_id
    格式: {date}_{time}_{userId}_{uuid前缀}
    示例: 20260409_143052_user123_a1b2c3d4
    """
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')
    uuid_prefix = str(uuid.uuid4()).replace('-', '')[:8]
    return f"{date_str}_{time_str}_{user_id}_{uuid_prefix}"


def get_chat_sessions_dir() -> Path:
    """获取聊天会话根目录"""
    return conf.CHAT_SESSIONS_DIR


def get_global_dir() -> Path:
    """获取全局目录"""
    return get_chat_sessions_dir() / '_global'


def get_session_dir(session_id: str) -> Path:
    """获取指定 session 的目录"""
    return get_chat_sessions_dir() / session_id


def get_global_memories_dir() -> Path:
    """获取全局记忆目录"""
    return get_global_dir() / 'memories'


def get_global_context_file() -> Path:
    """获取全局上下文文件"""
    return get_global_dir() / '_context.md'


def get_session_messages_dir(session_id: str) -> Path:
    """获取 session 的消息目录"""
    return get_session_dir(session_id) / 'messages'


def get_session_context_file(session_id: str) -> Path:
    """获取 session 的上下文文件"""
    return get_session_dir(session_id) / '_context.md'


def get_memory_index_file(memory_type: str) -> Path:
    """
    获取指定类型记忆的索引文件
    memory_type: user, feedback, project, reference
    """
    return get_global_memories_dir() / memory_type / '_index.md'


def ensure_directory_exists(path: Path) -> None:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def init_global_structure() -> None:
    """初始化全局目录结构"""
    global_dir = get_global_dir()
    memories_dir = get_global_memories_dir()

    ensure_directory_exists(global_dir)
    ensure_directory_exists(memories_dir)

    for memory_type in ['user', 'feedback', 'project', 'reference']:
        ensure_directory_exists(memories_dir / memory_type)

    global_context_file = get_global_context_file()
    if not global_context_file.exists():
        global_context_file.write_text(DEFAULT_GLOBAL_CONTEXT, encoding='utf-8')

    for memory_type in ['user', 'feedback', 'project', 'reference']:
        index_file = get_memory_index_file(memory_type)
        if not index_file.exists():
            index_file.write_text(DEFAULT_MEMORY_INDEX_TEMPLATE.format(memory_type=memory_type), encoding='utf-8')


def init_session_structure(session_id: str) -> None:
    """初始化 session 目录结构"""
    session_dir = get_session_dir(session_id)
    messages_dir = get_session_messages_dir(session_id)

    ensure_directory_exists(session_dir)
    ensure_directory_exists(messages_dir)

    session_context_file = get_session_context_file(session_id)
    if not session_context_file.exists():
        session_context_file.write_text(DEFAULT_SESSION_CONTEXT_TEMPLATE.format(
            session_id=session_id
        ), encoding='utf-8')


def session_exists(session_id: str) -> bool:
    """检查 session 是否存在"""
    return get_session_dir(session_id).exists()


DEFAULT_GLOBAL_CONTEXT = """# 全局上下文

## 元信息
- global_created: {date}
- last_updated: {date}
- total_sessions: 0
- active_session: null

## 用户概览
### 身份
- 用户ID: unknown
- 使用语言: 中文
- 技术水平: unknown

### 偏好
- 待补充

### 已知项目
- 待补充

## 跨会话统计
- 总消息数: 0
- 总工具调用: 0
- 平均会话长度: 0 条消息

## 最近会话
- 无
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

DEFAULT_MEMORY_INDEX_TEMPLATE = """# {memory_type} 记忆索引

## 记忆列表
- 无

## 最近更新
- 无
"""

DEFAULT_SESSION_CONTEXT_TEMPLATE = """# 会话上下文

## 元信息
- session_id: {session_id}
- user_id: unknown
- 创建时间: {time}
- 最后更新: {time}
- 消息总数: 0
- LLM 模型: {model}
- 最后摘要时间: null
- 摘要消息数: 0

## 当前会话信息
### 主题
- 待确定

### 当前任务
- 待确定

### 对话进度
- [ ] 开始对话

## 记忆引用
- 无

## 最近消息
- 无

## 历史摘要
- 无
""".format(
    session_id="{session_id}",
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    model=conf.OPENAI_MODEL
)


class SummarizationState:
    """摘要状态"""
    def __init__(self):
        self.last_summarize_time: Optional[datetime] = None
        self.last_summarize_message_count: int = 0
        self.is_summarizing: bool = False


_summarization_state = SummarizationState()


def check_summarization_needed(
    message_count: int,
    total_tokens: int,
    delta_tokens: int,
    no_tool_call_rounds: int,
) -> bool:
    """
    检查是否需要触发摘要

    触发条件（满足任一即触发）：
    - 消息数量 >= SUMMARIZE_TRIGGER_COUNT
    - Token 数量 >= SUMMARIZE_TRIGGER_TOKENS
    - 距上次摘要后新增 >= SUMMARIZE_TRIGGER_DELTA
    - 连续无工具调用轮次 >= SUMMARIZE_TRIGGER_NO_TOOL_ROUNDS
    """
    if message_count >= conf.SUMMARIZE_TRIGGER_COUNT:
        return True

    if total_tokens >= conf.SUMMARIZE_TRIGGER_TOKENS:
        return True

    if delta_tokens >= conf.SUMMARIZE_TRIGGER_DELTA:
        return True

    if no_tool_call_rounds >= conf.SUMMARIZE_TRIGGER_NO_TOOL_ROUNDS:
        return True

    return False


def check_summarization_debounce() -> bool:
    """
    检查摘要防抖
    如果距上次摘要 < SUMMARIZE_DEBOUNCE_SECONDS，则跳过
    """
    if _summarization_state.last_summarize_time is None:
        return True

    elapsed = (datetime.now() - _summarization_state.last_summarize_time).total_seconds()
    return elapsed >= conf.SUMMARIZE_DEBOUNCE_SECONDS


def acquire_summarization_lock() -> bool:
    """尝试获取摘要锁，防止并发摘要"""
    if _summarization_state.is_summarizing:
        return False
    _summarization_state.is_summarizing = True
    return True


def release_summarization_lock() -> None:
    """释放摘要锁"""
    _summarization_state.is_summarizing = False
    _summarization_state.last_summarize_time = datetime.now()


def update_summarization_state(message_count: int) -> None:
    """更新摘要状态"""
    _summarization_state.last_summarize_message_count = message_count


def process_tool_result_with_budget(result: Any, metadata: Optional[Dict] = None) -> Any:
    """
    使用 L1 Tool Result Budget 处理工具结果
    """
    return truncate_tool_result(result, metadata)


def process_tool_calls_with_microcompact(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    使用 L2 Microcompact 处理工具调用列表
    """
    return compact_tool_calls(tool_calls)


def estimate_tokens(text: str) -> int:
    """
    简单估算 token 数量
    注：使用字符统计，未进行真实 token 计数
    """
    return len(text)


def get_recent_messages_for_context(
    messages: List[Dict[str, Any]],
    keep_count: int = None
) -> List[Dict[str, Any]]:
    """
    获取最近的 N 条消息用于上下文
    """
    if keep_count is None:
        keep_count = conf.SUMMARIZE_KEEP_MESSAGES

    return messages[-keep_count:] if len(messages) > keep_count else messages


async def run_summarization(
    session_id: str,
    messages: List[Dict[str, Any]],
    user_id: str,
) -> Optional[str]:
    """
    运行摘要生成（placeholder，后续集成 LLM）
    返回摘要内容
    """
    if not acquire_summarization_lock():
        return None

    try:
        summary = await generate_summary(messages, user_id)

        release_summarization_lock()
        return summary
    except Exception as e:
        release_summarization_lock()
        raise e


async def generate_summary(messages: List[Dict[str, Any]], user_id: str) -> str:
    """
    生成对话摘要（后续集成 LLM API）
    """
    if not messages:
        return "会话为空，无摘要"

    recent_msgs = get_recent_messages_for_context(messages)
    summary_lines = [f"## 摘要生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    summary_lines.append(f"### 消息统计")
    summary_lines.append(f"- 消息总数: {len(messages)}")
    summary_lines.append(f"- 保留最近消息: {len(recent_msgs)}")

    user_msgs = [m for m in messages if m.get('role') == 'user']
    assistant_msgs = [m for m in messages if m.get('role') == 'assistant']

    summary_lines.append(f"- 用户消息: {len(user_msgs)}")
    summary_lines.append(f"- AI 回复: {len(assistant_msgs)}")

    tool_calls_count = sum(
        len(m.get('tool_calls', []))
        for m in messages
        if m.get('role') == 'assistant'
    )
    summary_lines.append(f"- 工具调用: {tool_calls_count}")

    summary_lines.append("")
    summary_lines.append("### 最近对话")

    for i, msg in enumerate(recent_msgs[-5:], 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')[:100]
        summary_lines.append(f"- [{role}]: {content}...")

    return '\n'.join(summary_lines)
