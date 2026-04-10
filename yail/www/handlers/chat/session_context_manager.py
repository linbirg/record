#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Context Manager - 会话上下文管理器

负责会话级别的日常摘要（简单规则匹配，每5轮执行）
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from conf import dev as conf
from lib import logger

from .session_manager import get_session_context_file, get_session_dir
from .message_store import create_message_store


class SessionContextManager:
    """会话上下文管理器"""

    TASK_KEYWORDS = {
        '调试': '调试问题',
        'debug': '调试问题',
        'bug': '调试问题',
        '错误': '调试问题',
        '开发': '开发功能',
        '写': '开发功能',
        '实现': '开发功能',
        '问': '咨询问题',
        '什么是': '咨询问题',
        '如何': '咨询问题',
        '怎么': '咨询问题',
        '优化': '性能优化',
        '重构': '代码重构',
        'review': '代码审查',
        '审查': '代码审查',
    }

    TECH_KEYWORDS = {
        'python': 'Python',
        'java': 'Java',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'typescript': 'TypeScript',
        'ts': 'TypeScript',
        'vue': 'Vue',
        'react': 'React',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'node': 'Node.js',
        'golang': 'Go',
        'rust': 'Rust',
        'mysql': 'MySQL',
        'redis': 'Redis',
        'mongodb': 'MongoDB',
        'docker': 'Docker',
        'k8s': 'Kubernetes',
    }

    def __init__(self, session_id: str):
        self.session_id = session_id

    def should_update(self) -> bool:
        """检查是否应该执行日常摘要"""
        msg_store = create_message_store(self.session_id)
        count = msg_store.get_message_count()
        return count > 0 and count % conf.SESSION_SUMMARY_INTERVAL == 0

    def extract_topic(self, messages: List[Dict]) -> str:
        """从最近消息中提取主题关键词"""
        user_messages = [m.get('content', '') for m in messages if m.get('role') == 'user']
        if not user_messages:
            return "待确定"
        
        last_user_msg = user_messages[-1].lower()
        
        for keyword, topic in self.TECH_KEYWORDS.items():
            if keyword in last_user_msg:
                return topic
        
        return "对话讨论"

    def extract_task(self, messages: List[Dict]) -> str:
        """从最近消息中提取当前任务"""
        user_messages = [m.get('content', '') for m in messages if m.get('role') == 'user']
        if not user_messages:
            return "待确定"
        
        last_user_msg = user_messages[-1].lower()
        
        for keyword, task in self.TASK_KEYWORDS.items():
            if keyword in last_user_msg:
                return task
        
        return "一般对话"

    def extract_tech_stack(self, messages: List[Dict]) -> List[str]:
        """从消息中提取技术栈"""
        all_content = ' '.join(m.get('content', '').lower() for m in messages)
        techs = set()
        
        for keyword, tech in self.TECH_KEYWORDS.items():
            if keyword in all_content:
                techs.add(tech)
        
        return list(techs) if techs else ["待确定"]

    def extract_user_key_info(self, messages: List[Dict]) -> List[str]:
        """提取用户明确要求记住的关键信息"""
        patterns = [
            r'记住.*?[叫|是|名叫](.+)',
            r'我叫(.+)',
            r'我是(.+?)(?:程序|工程|开发)',
            r'(?:不要|别).*?记住(.+)',
        ]
        
        user_messages = [m.get('content', '') for m in messages if m.get('role') == 'user']
        key_info = []
        
        for msg in user_messages:
            for pattern in patterns:
                match = re.search(pattern, msg, re.IGNORECASE)
                if match:
                    key_info.append(match.group(0))
        
        return key_info[:5]

    def extract_recent_messages(self, messages: List[Dict], count: int = 5) -> List[str]:
        """提取最近消息摘要"""
        recent = messages[-count:] if len(messages) > count else messages
        result = []
        
        for i, msg in enumerate(recent, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]
            result.append(f"### 消息 {i} ({role})\n{content}")
        
        return result

    def update_session_context(self) -> None:
        """更新会话上下文"""
        if not self.should_update():
            return
        
        logger.LOG_INFO(f"[SessionContextManager] updating context for session {self.session_id}")
        
        msg_store = create_message_store(self.session_id)
        messages = msg_store.load_messages()
        
        context_file = get_session_context_file(self.session_id)
        
        topic = self.extract_topic(messages)
        task = self.extract_task(messages)
        tech_stack = self.extract_tech_stack(messages)
        user_key_info = self.extract_user_key_info(messages)
        recent_msgs = self.extract_recent_messages(messages)
        
        content = f"""# 会话上下文

## 元信息
- session_id: {self.session_id}
- user_id: unknown
- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 消息总数: {len(messages)}
- LLM 模型: {conf.OPENAI_MODEL}
- 最后摘要时间: null
- 摘要消息数: 0

## 当前会话信息
### 主题
- {topic}

### 当前任务
- {task}

### 技术栈
{chr(10).join(f'- {t}' for t in tech_stack) if tech_stack else '- 待确定'}

### 用户关键信息
{chr(10).join(f'- {info}' for info in user_key_info) if user_key_info else '- 无'}

## 最近消息
{chr(10).join(recent_msgs) if recent_msgs else '- 无'}

## 历史摘要
- 无
"""
        
        context_file.write_text(content, encoding='utf-8')


def create_session_context_manager(session_id: str) -> SessionContextManager:
    """创建会话上下文管理器实例"""
    return SessionContextManager(session_id)