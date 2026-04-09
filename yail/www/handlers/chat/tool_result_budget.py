#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Result Budget - L1 工具结果裁剪

在工具执行结果发送给 LLM 之前进行裁剪，防止单条输出占过多上下文

配置项:
- TOOL_RESULT_BUDGET_MAX_CHARS: 单个工具结果最大字符数 (默认 2000)
- TOOL_RESULT_BUDGET_MIN_PREVIEW: 保留前 N 字符作为预览 (默认 500)
- TOOL_RESULT_BUDGET_REPLACE_TEXT: 裁剪后替换文本
"""

import json
from typing import Any, Dict, Optional

from conf import dev as conf


def truncate_tool_result(
    result: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> Any:
    """
    对工具结果进行裁剪

    Args:
        result: 工具执行结果（字符串或字典）
        metadata: 额外元数据（如 file 路径、lines 等）

    Returns:
        裁剪后的结果
    """
    if not conf.TOOL_RESULT_BUDGET_ENABLED:
        return result

    if isinstance(result, str):
        return _truncate_string_result(result, metadata)
    elif isinstance(result, dict):
        return _truncate_dict_result(result)
    else:
        return result


def _truncate_string_result(result: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """裁剪字符串类型的结果"""
    if len(result) <= conf.TOOL_RESULT_BUDGET_MAX_CHARS:
        return result

    preview = result[:conf.TOOL_RESULT_BUDGET_MIN_PREVIEW]
    truncated = (
        f"{preview}..."
        f"\n\n{conf.TOOL_RESULT_BUDGET_REPLACE_TEXT}"
    )

    if metadata:
        truncated += f"\n\n```json\n{json.dumps(metadata, ensure_ascii=False, indent=2)}\n```"

    return truncated


def _truncate_dict_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """裁剪字典类型的结果"""
    result_str = json.dumps(result, ensure_ascii=False)
    if len(result_str) <= conf.TOOL_RESULT_BUDGET_MAX_CHARS:
        return result

    truncated = {
        'truncated': True,
        'original_length': len(result_str),
        'preview': json.dumps(result, ensure_ascii=False)[:conf.TOOL_RESULT_BUDGET_MIN_PREVIEW],
        'data': conf.TOOL_RESULT_BUDGET_REPLACE_TEXT
    }

    return truncated


def is_tool_result_truncated(result: Any) -> bool:
    """检查结果是否被裁剪"""
    if isinstance(result, dict):
        return result.get('truncated', False)
    return False


def get_tool_result_metadata(result: Any) -> Optional[Dict[str, Any]]:
    """获取工具结果的元数据"""
    if isinstance(result, dict):
        return result.get('metadata')
    return None
