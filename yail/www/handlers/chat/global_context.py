#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Context Manager - 全局上下文管理

负责管理 _global/_context.md 文件，包含:
- 用户概览
- 跨会话统计
- 最近会话列表
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .memory_store import memory_store
from .memory_types import MemoryType

from .session_manager import get_global_context_file


@dataclass
class GlobalContext:
    """全局上下文数据类"""
    global_created: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    last_updated: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    total_sessions: int = 0
    active_session: Optional[str] = None
    
    user_id: str = "unknown"
    user_language: str = "中文"
    user_level: str = "unknown"
    
    user_preferences: List[str] = field(default_factory=list)
    known_projects: List[str] = field(default_factory=list)
    
    total_messages: int = 0
    total_tool_calls: int = 0
    avg_session_length: float = 0.0
    
    recent_sessions: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        preferences_str = '\n'.join(f"- {p}" for p in self.user_preferences) if self.user_preferences else "- 待补充"
        projects_str = '\n'.join(f"- {p}" for p in self.known_projects) if self.known_projects else "- 待补充"
        recent_str = '\n'.join(f"- {s}" for s in self.recent_sessions) if self.recent_sessions else "- 无"
        
        return f"""# 全局上下文

## 元信息
- global_created: {self.global_created}
- last_updated: {self.last_updated}
- total_sessions: {self.total_sessions}
- active_session: {self.active_session or 'null'}

## 用户概览
### 身份
- 用户ID: {self.user_id}
- 使用语言: {self.user_language}
- 技术水平: {self.user_level}

### 偏好
{preferences_str}

### 已知项目
{projects_str}

## 跨会话统计
- 总消息数: {self.total_messages}
- 总工具调用: {self.total_tool_calls}
- 平均会话长度: {self.avg_session_length:.1f} 条消息

## 最近会话
{recent_str}
"""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'global_created': self.global_created,
            'last_updated': self.last_updated,
            'total_sessions': self.total_sessions,
            'active_session': self.active_session,
            'user_id': self.user_id,
            'user_language': self.user_language,
            'user_level': self.user_level,
            'user_preferences': self.user_preferences,
            'known_projects': self.known_projects,
            'total_messages': self.total_messages,
            'total_tool_calls': self.total_tool_calls,
            'avg_session_length': self.avg_session_length,
            'recent_sessions': self.recent_sessions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GlobalContext':
        """从字典创建"""
        return cls(
            global_created=data.get('global_created', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            last_updated=data.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            total_sessions=data.get('total_sessions', 0),
            active_session=data.get('active_session'),
            user_id=data.get('user_id', 'unknown'),
            user_language=data.get('user_language', '中文'),
            user_level=data.get('user_level', 'unknown'),
            user_preferences=data.get('user_preferences', []),
            known_projects=data.get('known_projects', []),
            total_messages=data.get('total_messages', 0),
            total_tool_calls=data.get('total_tool_calls', 0),
            avg_session_length=data.get('avg_session_length', 0.0),
            recent_sessions=data.get('recent_sessions', []),
        )


class GlobalContextManager:
    """全局上下文管理器"""

    def __init__(self):
        self._context: Optional[GlobalContext] = None

    def get_context(self) -> GlobalContext:
        """获取全局上下文"""
        if self._context is None:
            self._context = self._load_context()
        return self._context

    def _load_context(self) -> GlobalContext:
        """从文件加载全局上下文"""
        context_file = get_global_context_file()
        
        if not context_file.exists():
            return GlobalContext()
        
        content = context_file.read_text(encoding='utf-8')
        return self._parse_context(content)

    def _parse_context(self, content: str) -> GlobalContext:
        """解析上下文内容"""
        data = {}
        
        data['global_created'] = self._extract_field(content, 'global_created')
        data['last_updated'] = self._extract_field(content, 'last_updated')
        data['total_sessions'] = int(self._extract_field(content, 'total_sessions') or '0')
        data['active_session'] = self._extract_field(content, 'active_session')
        
        if data['active_session'] == 'null':
            data['active_session'] = None
        
        data['user_id'] = self._extract_field(content, '用户ID')
        data['user_language'] = self._extract_field(content, '使用语言')
        data['user_level'] = self._extract_field(content, '技术水平')
        
        prefs = self._extract_section(content, '### 偏好')
        data['user_preferences'] = self._extract_list_items(prefs)
        
        projects = self._extract_section(content, '### 已知项目')
        data['known_projects'] = self._extract_list_items(projects)
        
        data['total_messages'] = int(self._extract_field(content, '总消息数') or '0')
        data['total_tool_calls'] = int(self._extract_field(content, '总工具调用') or '0')
        avg_str = self._extract_field(content, '平均会话长度') or '0'
        data['avg_session_length'] = float(avg_str.replace(' 条消息', ''))
        
        recent = self._extract_section(content, '## 最近会话')
        data['recent_sessions'] = self._extract_list_items(recent)
        
        return GlobalContext.from_dict(data)

    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """提取字段值"""
        patterns = [
            rf'- {field_name}:\s*(.+?)(?:\n|$)',
            rf'{field_name}:\s*(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        return None

    def _extract_section(self, content: str, section_name: str) -> str:
        """提取章节内容"""
        pattern = rf'{re.escape(section_name)}\s*\n(.*?)(?=\n## |\n#|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        return ""

    def _extract_list_items(self, section: str) -> List[str]:
        """提取列表项"""
        items = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:])
        return items

    def save_context(self, context: Optional[GlobalContext] = None) -> None:
        """保存全局上下文到文件"""
        if context is None:
            context = self.get_context()
        
        context.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        context_file = get_global_context_file()
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text(context.to_markdown(), encoding='utf-8')
        
        self._context = context

    def update_user_info(
        self,
        user_id: Optional[str] = None,
        language: Optional[str] = None,
        level: Optional[str] = None,
    ) -> None:
        """更新用户信息"""
        context = self.get_context()
        
        if user_id:
            context.user_id = user_id
        if language:
            context.user_language = language
        if level:
            context.user_level = level
        
        self.save_context(context)

    def add_session(self, session_id: str) -> None:
        """添加新会话"""
        context = self.get_context()
        
        context.total_sessions += 1
        
        if session_id not in context.recent_sessions:
            context.recent_sessions.insert(0, session_id)
            context.recent_sessions = context.recent_sessions[:10]
        
        context.active_session = session_id
        
        self.save_context(context)

    def update_stats(
        self,
        messages_delta: int = 0,
        tool_calls_delta: int = 0,
    ) -> None:
        """更新统计"""
        context = self.get_context()
        
        context.total_messages += messages_delta
        context.total_tool_calls += tool_calls_delta
        
        if context.total_sessions > 0:
            context.avg_session_length = context.total_messages / context.total_sessions
        
        self.save_context(context)

    def add_memory_reference(self, memory_type: MemoryType, memory_name: str) -> str:
        """获取记忆引用路径"""
        return f"_global/memories/{memory_type.value}/_index.md#{memory_name}"

    def build_user_profile_prompt(self) -> str:
        """构建用户画像提示"""
        context = self.get_context()
        
        lines = ["## 用户画像"]
        lines.append(f"- 用户ID: {context.user_id}")
        lines.append(f"- 使用语言: {context.user_language}")
        lines.append(f"- 技术水平: {context.user_level}")
        
        if context.user_preferences:
            lines.append("\n### 用户偏好")
            for pref in context.user_preferences:
                lines.append(f"- {pref}")
        
        if context.known_projects:
            lines.append("\n### 已知项目")
            for proj in context.known_projects:
                lines.append(f"- {proj}")
        
        return '\n'.join(lines)


global_context_manager = GlobalContextManager()
