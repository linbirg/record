#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microcompact - L2 重复工具调用压缩

同类型工具连续调用时，只保留最后一次结果，之前的替换为 stub

适用工具: Read, Bash, Grep, Glob

配置项:
- MICROCOMPACT_ENABLED: 是否启用
- MICROCOMPACT_TOOLS: 适用工具类型
- MICROCOMPACT_STUB: 压缩后替换文本
"""

from typing import Any, Dict, List, Optional

from conf import dev as conf


class MicrocompactProcessor:
    """Microcompact 处理器"""

    def __init__(self):
        self.enabled = conf.MICROCOMPACT_ENABLED
        self.tools = conf.MICROCOMPACT_TOOLS
        self.stub = conf.MICROCOMPACT_STUB
        self._last_tool_calls: Dict[str, Dict[str, Any]] = {}

    def process(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理工具调用列表，压缩重复调用

        Args:
            tool_calls: 工具调用列表，每项包含 tool_name, args, result

        Returns:
            处理后的工具调用列表
        """
        if not self.enabled or not tool_calls:
            return tool_calls

        result = []
        tool_call_key = None

        for i, call in enumerate(tool_calls):
            tool_name = call.get('tool_name') or call.get('name', '')
            
            if tool_name not in self.tools:
                result.append(call)
                continue

            key = self._get_tool_key(call)
            
            is_last_of_type = not self._has_subsequent_same_type(tool_calls[i + 1:], tool_name)
            
            if is_last_of_type:
                self._last_tool_calls[key] = call
                result.append(call)
            else:
                stub_call = self._create_stub_call(call)
                result.append(stub_call)

        return result

    def _get_tool_key(self, call: Dict[str, Any]) -> str:
        """生成工具调用的唯一键"""
        tool_name = call.get('tool_name') or call.get('name', '')
        args = call.get('args', {})
        
        if 'file' in args:
            return f"{tool_name}:{args['file']}"
        elif 'path' in args:
            return f"{tool_name}:{args['path']}"
        else:
            return f"{tool_name}:{str(args)}"

    def _has_subsequent_same_type(self, remaining_calls: List[Dict[str, Any]], tool_name: str) -> bool:
        """检查后续是否有同类型工具调用"""
        for call in remaining_calls:
            call_name = call.get('tool_name') or call.get('name', '')
            if call_name == tool_name:
                return True
        return False

    def _create_stub_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """创建 stub 调用"""
        return {
            'tool_name': call.get('tool_name') or call.get('name', ''),
            'args': call.get('args', {}),
            'result': self.stub,
            'is_stub': True
        }

    def get_compression_stats(self) -> Dict[str, int]:
        """获取压缩统计"""
        return {
            'total_tools_tracked': len(self._last_tool_calls)
        }


def compact_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    便捷函数：对工具调用列表进行 microcompact 压缩
    """
    processor = MicrocompactProcessor()
    return processor.process(tool_calls)


def compact_repeated_reads(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    对消息列表中的重复 Read 调用进行压缩

    用于在发送给 LLM 前压缩消息历史
    """
    if not conf.MICROCOMPACT_ENABLED:
        return messages

    processor = MicrocompactProcessor()
    result = []

    for msg in messages:
        if msg.get('role') == 'assistant' and 'tool_calls' in msg:
            compressed_calls = processor.process(msg['tool_calls'])
            msg = {**msg, 'tool_calls': compressed_calls}
        
        result.append(msg)

    return result
