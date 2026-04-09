#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Types - 记忆类型定义

4类记忆:
- user: 用户角色、偏好、知识水平
- feedback: 用户纠正/确认的行为指导
- project: 进行中的工作、目标、bug
- reference: 外部系统指针
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class MemoryType(Enum):
    """记忆类型枚举"""
    USER = "user"
    FEEDBACK = "feedback"
    PROJECT = "project"
    REFERENCE = "reference"

    @classmethod
    def values(cls):
        return [e.value for e in cls]

    @classmethod
    def from_string(cls, s: str):
        for e in cls:
            if e.value == s.lower():
                return e
        raise ValueError(f"Unknown memory type: {s}")


class MemoryScope(Enum):
    """记忆作用域枚举"""
    PRIVATE = "private"  # 仅当前用户
    TEAM = "team"       # 团队共享

    @classmethod
    def values(cls):
        return [e.value for e in cls]


MEMORY_TYPE_DESCRIPTIONS = {
    MemoryType.USER: "用户角色、偏好、知识水平",
    MemoryType.FEEDBACK: "用户纠正/确认的行为指导",
    MemoryType.PROJECT: "进行中的工作、目标、bug",
    MemoryType.REFERENCE: "外部系统指针",
}

MEMORY_TYPE_SCOPES = {
    MemoryType.USER: MemoryScope.PRIVATE,
    MemoryType.FEEDBACK: MemoryScope.PRIVATE,
    MemoryType.PROJECT: MemoryScope.TEAM,
    MemoryType.REFERENCE: MemoryScope.TEAM,
}


@dataclass
class Memory:
    """记忆数据类"""
    name: str
    description: str
    type: MemoryType
    scope: MemoryScope
    content: str
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    source_sessions: List[str] = field(default_factory=list)
    source_messages: List[int] = field(default_factory=list)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        source_sessions_str = ', '.join(self.source_sessions) if self.source_sessions else '无'
        source_msgs_str = ', '.join(f'#{m}' for m in self.source_messages) if self.source_messages else '无'
        
        return f"""### {self.name}
- 更新时间: {self.updated_at}
- 来源会话: {source_sessions_str}
- 摘要: {self.description}

**内容:**
{self.content}

**来源消息:** {source_msgs_str}
"""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'scope': self.scope.value,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'source_sessions': self.source_sessions,
            'source_messages': self.source_messages,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Memory':
        """从字典创建"""
        return cls(
            name=data['name'],
            description=data['description'],
            type=MemoryType.from_string(data['type']),
            scope=MemoryScope(data['scope']),
            content=data['content'],
            created_at=data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            updated_at=data.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            source_sessions=data.get('source_sessions', []),
            source_messages=data.get('source_messages', []),
        )


@dataclass
class MemoryEntry:
    """记忆索引中的单条记录（简化版）"""
    name: str
    description: str
    updated_at: str
    source_sessions: List[str] = field(default_factory=list)
