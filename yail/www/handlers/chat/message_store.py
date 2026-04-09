#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Message Store - 消息存储管理

负责管理 session 的消息文件读写，支持 L1/L2 压缩

目录结构:
{session_id}/
└── messages/
    ├── 001_user.md
    ├── 002_assistant.md
    └── ...
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from conf import dev as conf

from .session_manager import (
    get_session_messages_dir,
    get_session_context_file,
    process_tool_result_with_budget,
    process_tool_calls_with_microcompact,
    estimate_tokens,
)
from .tool_result_budget import is_tool_result_truncated


class MessageStore:
    """消息存储器"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages_dir = get_session_messages_dir(session_id)
        self._message_counter = 0
        self._load_message_list()

    def _load_message_list(self) -> None:
        """加载现有消息列表，确定消息序号"""
        if not self.messages_dir.exists():
            return

        pattern = re.compile(r'^(\d+)_')
        max_num = 0

        for f in self.messages_dir.iterdir():
            if f.is_file() and f.suffix == '.md':
                match = pattern.match(f.stem)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)

        self._message_counter = max_num

    def _get_next_message_num(self) -> int:
        """获取下一条消息的序号"""
        self._message_counter += 1
        return self._message_counter

    def _get_message_file(self, num: int, role: str) -> Path:
        """获取消息文件路径"""
        filename = f"{num:03d}_{role}.md"
        return self.messages_dir / filename

    def save_user_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """保存用户消息"""
        num = self._get_next_message_num()
        msg_file = self._get_message_file(num, 'user')

        self.messages_dir.mkdir(parents=True, exist_ok=True)

        metadata_str = self._format_metadata({
            'num': num,
            'role': 'user',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **(metadata or {}),
        })

        content = f"""---
{metadata_str}
---

{content}
"""

        msg_file.write_text(content, encoding='utf-8')
        return f"消息 {num}"

    def save_assistant_message(
        self,
        content: str,
        reasoning_content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """保存助手消息（支持 L1/L2 压缩）"""
        num = self._get_next_message_num()
        msg_file = self._get_message_file(num, 'assistant')

        self.messages_dir.mkdir(parents=True, exist_ok=True)

        compact_reason = None
        if tool_calls:
            original_calls = len(tool_calls)
            tool_calls = process_tool_calls_with_microcompact(tool_calls)
            if len(tool_calls) < original_calls:
                compact_reason = 'microcompact'

        processed_tool_calls = []
        for call in tool_calls or []:
            if 'result' in call:
                result = call['result']
                was_truncated = is_tool_result_truncated(result)
                if was_truncated:
                    if not compact_reason:
                        compact_reason = 'tool_result_budget'
                call['result'] = process_tool_result_with_budget(result)
            processed_tool_calls.append(call)

        metadata_str = self._format_metadata({
            'num': num,
            'role': 'assistant',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'compact_reason': compact_reason,
            'tool_call_count': len(processed_tool_calls),
            **(metadata or {}),
        })

        lines = [f"""---
{metadata_str}
---"""]

        if reasoning_content:
            lines.append(f"\n## 思考过程\n{reasoning_content}\n")

        if processed_tool_calls:
            lines.append("\n## 工具调用\n")
            for call in processed_tool_calls:
                tool_name = call.get('tool_name', call.get('name', 'unknown'))
                args = call.get('args', {})
                result = call.get('result', '')
                is_stub = call.get('is_stub', False)

                lines.append(f"### {tool_name}\n")
                if is_stub:
                    lines.append(f"> {result}\n")
                else:
                    lines.append(f"**参数**: `{json.dumps(args, ensure_ascii=False)}`\n")
                    lines.append(f"\n**结果**:\n```\n{result}\n```\n")

        lines.append(f"\n## 正式回复\n{content}\n")

        msg_file.write_text(''.join(lines), encoding='utf-8')
        return f"消息 {num}"

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """格式化 metadata 为 YAML 前导块"""
        lines = []
        for key, value in metadata.items():
            if value is None:
                continue
            if isinstance(value, dict):
                lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            elif isinstance(value, list):
                lines.append(f"{key}: [{', '.join(str(v) for v in value)}]")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)

    def load_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """加载消息列表"""
        if not self.messages_dir.exists():
            return []

        messages = []
        for f in sorted(self.messages_dir.iterdir()):
            if f.is_file() and f.suffix == '.md':
                msg = self._parse_message_file(f)
                if msg:
                    messages.append(msg)

        if limit:
            messages = messages[-limit:]

        return messages

    def _parse_message_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """解析单条消息文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            parts = content.split('\n---\n', 1)
            if len(parts) != 2:
                return None

            metadata_str, body = parts

            metadata = self._parse_metadata(metadata_str)

            body = body.strip()

            reasoning = None
            tool_calls = []
            main_content = body

            if '\n## 思考过程\n' in body:
                body_parts = body.split('\n## 思考过程\n', 1)
                main_content = body_parts[0]
                thinking_and_rest = body_parts[1]

                if '\n## 工具调用\n' in thinking_and_rest:
                    thinking_parts, tool_calls_str = thinking_and_rest.split('\n## 工具调用\n', 1)
                    reasoning = thinking_parts.strip()
                    tool_calls = self._parse_tool_calls(tool_calls_str)
                else:
                    reasoning = thinking_and_rest.strip()
            elif '\n## 工具调用\n' in body:
                body_parts = body.split('\n## 工具调用\n', 1)
                main_content = body_parts[0]
                tool_calls = self._parse_tool_calls(body_parts[1])

            if '\n## 正式回复\n' in main_content:
                main_content = main_content.split('\n## 正式回复\n', 1)[1]

            return {
                'num': metadata.get('num'),
                'role': metadata.get('role', 'unknown'),
                'timestamp': metadata.get('timestamp'),
                'content': main_content.strip(),
                'reasoning_content': reasoning,
                'tool_calls': tool_calls,
                'tool_call_count': metadata.get('tool_call_count', len(tool_calls)),
                'compact_reason': metadata.get('compact_reason'),
            }

        except Exception as e:
            return None

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """解析 metadata 字符串"""
        metadata = {}
        for line in metadata_str.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        return metadata

    def _parse_tool_calls(self, tool_calls_str: str) -> List[Dict[str, Any]]:
        """解析工具调用字符串"""
        tool_calls = []

        sections = tool_calls_str.split('\n### ')
        for section in sections[1:]:
            lines = section.strip().split('\n')
            if not lines:
                continue

            tool_name = lines[0].strip()
            call = {'tool_name': tool_name, 'args': {}, 'result': ''}

            args_pattern = re.compile(r'\*\*参数\*\*:\s*`(.+?)`', re.DOTALL)
            result_pattern = re.compile(r'\*\*结果\*\*:\s*```\n(.+?)\n```', re.DOTALL)
            stub_pattern = re.compile(r'^>\s*(.+?)$', re.MULTILINE)

            args_match = args_pattern.search(section)
            if args_match:
                try:
                    call['args'] = json.loads(args_match.group(1))
                except json.JSONDecodeError:
                    pass

            if '> ' in section and not args_match:
                stub_match = stub_pattern.search(section)
                if stub_match:
                    call['result'] = stub_match.group(1).strip()
                    call['is_stub'] = True
            else:
                result_match = result_pattern.search(section)
                if result_match:
                    call['result'] = result_match.group(1).strip()

            tool_calls.append(call)

        return tool_calls

    def get_message_count(self) -> int:
        """获取消息总数"""
        return self._message_counter

    def get_total_tokens(self) -> int:
        """估算总 token 数"""
        messages = self.load_messages()
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            total += estimate_tokens(content)
            if msg.get('reasoning_content'):
                total += estimate_tokens(msg['reasoning_content'])
        return total

    def get_recent_tool_call_count(self) -> int:
        """获取最近无工具调用的轮次"""
        messages = self.load_messages()
        no_tool_rounds = 0

        for msg in reversed(messages):
            if msg.get('role') == 'assistant':
                if msg.get('tool_call_count', 0) == 0:
                    no_tool_rounds += 1
                else:
                    break

        return no_tool_rounds


def create_message_store(session_id: str) -> MessageStore:
    """创建消息存储器"""
    return MessageStore(session_id)
