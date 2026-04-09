#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Store - 记忆存储管理

负责读写 _global/memories/{type}/_index.md 文件

目录结构:
_global/memories/
├── user/_index.md
├── feedback/_index.md
├── project/_index.md
└── reference/_index.md
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

from .memory_types import Memory, MemoryEntry, MemoryScope, MemoryType

from .session_manager import get_memory_index_file


class MemoryStore:
    """记忆存储器"""

    def __init__(self):
        pass

    def save_memory(self, memory: Memory) -> None:
        """
        保存记忆到对应类型的索引文件

        如果记忆已存在（同名），则更新；否则追加
        """
        index_file = get_memory_index_file(memory.type.value)
        memories = self._parse_index_file(index_file)
        
        existing_idx = None
        for i, m in enumerate(memories):
            if m.name == memory.name:
                existing_idx = i
                break
        
        if existing_idx is not None:
            memory.created_at = memories[existing_idx].created_at
            memories[existing_idx] = memory
        else:
            memories.append(memory)
        
        self._write_index_file(index_file, memories)

    def get_memory(self, memory_type: MemoryType, name: str) -> Optional[Memory]:
        """获取指定记忆"""
        index_file = get_memory_index_file(memory_type.value)
        memories = self._parse_index_file(index_file)
        
        for m in memories:
            if m.name == name:
                return m
        return None

    def get_all_memories(self, memory_type: MemoryType) -> List[Memory]:
        """获取指定类型的所有记忆"""
        index_file = get_memory_index_file(memory_type.value)
        return self._parse_index_file(index_file)

    def get_all_memories_by_session(self, session_id: str) -> Dict[MemoryType, List[Memory]]:
        """获取指定 session 产生的所有记忆"""
        result = {mt: [] for mt in MemoryType}
        
        for memory_type in MemoryType:
            memories = self.get_all_memories(memory_type)
            for m in memories:
                if session_id in m.source_sessions:
                    result[memory_type].append(m)
        
        return result

    def delete_memory(self, memory_type: MemoryType, name: str) -> bool:
        """删除指定记忆"""
        index_file = get_memory_index_file(memory_type.value)
        memories = self._parse_index_file(index_file)
        
        new_memories = [m for m in memories if m.name != name]
        
        if len(new_memories) == len(memories):
            return False
        
        self._write_index_file(index_file, new_memories)
        return True

    def _parse_index_file(self, index_file) -> List[Memory]:
        """解析索引文件"""
        if not index_file.exists():
            return []
        
        content = index_file.read_text(encoding='utf-8')
        return self._parse_memory_list(content)

    def _parse_memory_list(self, content: str) -> List[Memory]:
        """解析记忆列表"""
        memories = []
        
        sections = re.split(r'\n### ', content)
        
        if not sections:
            return memories
        
        first_section = sections[0]
        if '## 记忆列表' not in first_section and '## 最近更新' not in first_section:
            return memories
        
        for section in sections[1:]:
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            name = lines[0].strip()
            
            memory = self._parse_memory_section(section, name)
            if memory:
                memories.append(memory)
        
        return memories

    def _parse_memory_section(self, section: str, name: str) -> Optional[Memory]:
        """解析单条记忆的内容"""
        lines = section.strip().split('\n')
        
        description = ""
        updated_at = ""
        source_sessions = []
        source_messages = []
        content_parts = []
        in_content = False
        
        for line in lines[1:]:
            line = line.strip()
            
            if line.startswith('**内容:**'):
                in_content = True
                content_parts.append(line.replace('**内容:**', '').strip())
            elif line.startswith('**来源消息:**'):
                in_content = False
                msg_refs = line.replace('**来源消息:**', '').strip()
                if msg_refs and msg_refs != '无':
                    for ref in msg_refs.split(','):
                        ref = ref.strip().replace('#', '')
                        if ref.isdigit():
                            source_messages.append(int(ref))
                        elif ref:
                            if ref not in source_sessions:
                                source_sessions.append(ref)
            elif in_content:
                if line.startswith('- 更新时间:') or line.startswith('**来源消息:**'):
                    in_content = False
                else:
                    content_parts.append(line)
            
            if line.startswith('- 更新时间:'):
                updated_at = line.replace('- 更新时间:', '').strip()
            elif line.startswith('- 来源会话:'):
                sessions_str = line.replace('- 来源会话:', '').strip()
                if sessions_str and sessions_str != '无':
                    source_sessions = [s.strip() for s in sessions_str.split(',')]
            elif line.startswith('- 摘要:'):
                description = line.replace('- 摘要:', '').strip()
        
        if not name or not content_parts:
            return None
        
        memory_type = self._infer_memory_type(name, description)
        
        return Memory(
            name=name,
            description=description or "无描述",
            type=memory_type,
            scope=MemoryScope.PRIVATE if memory_type in [MemoryType.USER, MemoryType.FEEDBACK] else MemoryScope.TEAM,
            content='\n'.join(content_parts).strip(),
            updated_at=updated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            source_sessions=source_sessions,
            source_messages=source_messages,
        )

    def _infer_memory_type(self, name: str, description: str) -> MemoryType:
        """根据名称和描述推断记忆类型"""
        text = f"{name} {description}".lower()
        
        if '偏好' in text or '喜欢' in text or '习惯' in text or '水平' in text:
            return MemoryType.USER
        elif '不要' in text or '纠正' in text or '反馈' in text:
            return MemoryType.FEEDBACK
        elif '项目' in text or '工作' in text or '任务' in text:
            return MemoryType.PROJECT
        elif '链接' in text or '地址' in text or '参考' in text:
            return MemoryType.REFERENCE
        else:
            return MemoryType.USER

    def _write_index_file(self, index_file, memories: List[Memory]) -> None:
        """写入索引文件"""
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [f"# {index_file.parent.name.capitalize()} 记忆索引\n", "## 记忆列表\n"]
        
        if not memories:
            lines.append("- 无\n")
        else:
            for memory in memories:
                lines.append(memory.to_markdown())
                lines.append("\n")
        
        lines.append("\n## 最近更新\n")
        sorted_memories = sorted(memories, key=lambda m: m.updated_at, reverse=True)
        for memory in sorted_memories[:10]:
            lines.append(f"- {memory.updated_at}: {memory.name}\n")
        
        index_file.write_text(''.join(lines), encoding='utf-8')

    def get_memory_entries(self, memory_type: MemoryType) -> List[MemoryEntry]:
        """获取记忆索引条目（简化版，用于展示）"""
        memories = self.get_all_memories(memory_type)
        return [
            MemoryEntry(
                name=m.name,
                description=m.description,
                updated_at=m.updated_at,
                source_sessions=m.source_sessions,
            )
            for m in memories
        ]


memory_store = MemoryStore()
