#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Summarizer - LLM 摘要器

负责 L5 触发时的深度摘要和记忆提取
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from conf import dev as conf
from lib import logger

from .session_manager import (
    get_session_dir,
    get_session_messages_dir,
    get_global_context_file,
    get_memory_index_file,
    get_session_context_file,
)
from .message_store import create_message_store
from .global_context import global_context_manager
from .memory_store import memory_store
from .memory_types import Memory, MemoryType, MemoryScope


class LLMSummarizer:
    """LLM 摘要器"""

    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id

    def build_prompt(self) -> str:
        """构建 LLM Prompt"""
        msg_store = create_message_store(self.session_id)
        messages = msg_store.load_messages()
        
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        messages_text = self._format_messages(recent_messages)
        
        session_context_file = get_session_context_file(self.session_id)
        history_summary = ""
        if session_context_file.exists():
            content = session_context_file.read_text(encoding='utf-8')
            if '## 历史摘要' in content:
                match = re.search(r'## 历史摘要\n(.*?)(?=\n##|$)', content, re.DOTALL)
                if match:
                    history_summary = match.group(1).strip()
        
        global_ctx = global_context_manager.get_context()
        user_profile = self._format_user_profile(global_ctx)
        
        existing_memories = self._get_existing_memories()
        
        prompt = f"""## 任务指令
分析以下对话，输出 JSON 格式的结果。不要调用任何工具，只返回文本内容。

## 输出格式
```json
{{
  "session_summary": {{
    "topic": "主题关键词",
    "task": "当前任务描述",
    "progress": ["已完成步骤1", "进行中步骤2"]
  }},
  "memory_updates": [
    {{
      "type": "user|feedback|project|reference",
      "action": "create|update",
      "name": "记忆名称",
      "content": "记忆内容",
      "description": "一句话描述"
    }}
  ]
}}
```

## 输入内容
1. 最近消息:
{messages_text}

2. 历史摘要:
{history_summary if history_summary else "无"}

3. 用户画像:
{user_profile}

4. 已有关联记忆:
{existing_memories if existing_memories else "无"}

## 要求
- 主题提取简洁的关键词
- 任务描述当前对话的目标
- 只提取有长期价值的信息作为记忆
- 如果没有需要提取的记忆，memory_updates 返回空数组
- progress 描述对话的进度步骤
"""
        return prompt

    def _format_messages(self, messages: List[Dict]) -> str:
        """格式化消息为文本"""
        lines = []
        for i, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:500]
            lines.append(f"消息{i} [{role}]: {content}")
        return '\n'.join(lines)

    def _format_user_profile(self, global_ctx) -> str:
        """格式化用户画像"""
        lines = [f"- 用户ID: {global_ctx.user_id}"]
        lines.append(f"- 使用语言: {global_ctx.user_language}")
        lines.append(f"- 技术水平: {global_ctx.user_level}")
        if global_ctx.user_preferences:
            lines.append(f"- 用户偏好: {', '.join(global_ctx.user_preferences)}")
        if global_ctx.known_projects:
            lines.append(f"- 已知项目: {', '.join(global_ctx.known_projects)}")
        return '\n'.join(lines)

    def _get_existing_memories(self) -> str:
        """获取已有关联记忆"""
        memories = memory_store.get_all_memories_by_session(self.session_id)
        lines = []
        for mem_type, mem_list in memories.items():
            for mem in mem_list:
                lines.append(f"- [{mem.type.value}] {mem.name}: {mem.description}")
        return '\n'.join(lines) if lines else "无"

    def _get_openai_client(self):
        """获取 OpenAI 客户端"""
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key=conf.OPENAI_API_KEY,
            base_url=conf.OPENAI_BASE_URL,
        )

    def _extract_json(self, content: str) -> Optional[str]:
        """从 LLM 返回内容中提取 JSON"""
        original_content = content
        content = content.strip()
        
        logger.LOG_TRACE(f"[LLMSummarizer] _extract_json input: {content[:200]}")
        
        # 去除思考内容 【行动计划】...【/行动计划】
        import re
        content = re.sub(r'【.*?】', '', content, flags=re.DOTALL)
        
        # 去除 ```json 代码块
        if content.startswith('```'):
            lines = content.split('\n')
            json_lines = []
            in_code_block = False
            for line in lines:
                if line.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    json_lines.append(line)
            content = '\n'.join(json_lines)
            logger.LOG_TRACE(f"[LLMSummarizer] after removing code block: {content[:200]}")
        
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            result = content[json_start:json_end]
            logger.LOG_TRACE(f"[LLMSummarizer] extracted JSON: {result[:200]}")
            return result
        
        logger.LOG_FATAL(f"[LLMSummarizer] no JSON found in content")
        logger.LOG_FATAL(f"[LLMSummarizer] original content: {original_content[:500]}")
        return None

    async def run_summarization(self) -> Tuple[Optional[Dict], List[Memory]]:
        """执行 LLM 摘要"""
        logger.LOG_INFO(f"[LLMSummarizer] ===== START SUMMARIZATION =====")
        logger.LOG_INFO(f"[LLMSummarizer] session_id={self.session_id}, user_id={self.user_id}")
        
        prompt = self.build_prompt()
        logger.LOG_INFO(f"[LLMSummarizer] prompt length={len(prompt)}")
        
        client = self._get_openai_client()
        
        try:
            logger.LOG_INFO(f"[LLMSummarizer] calling LLM API...")
            response = await client.chat.completions.create(
                model=conf.OPENAI_MODEL,
                messages=[
                    {'role': 'system', 'content': '你是一个上下文管理助手，负责分析对话并提取摘要和记忆。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            logger.LOG_INFO(f"[LLMSummarizer] LLM API call completed")
            
            content = response.choices[0].message.content
            
            logger.LOG_INFO(f"[LLMSummarizer] ===== RAW LLM RESPONSE =====")
            logger.LOG_INFO(f"[LLMSummarizer] response length={len(content)}")
            logger.LOG_INFO(f"[LLMSummarizer] response content:\n{content}")
            logger.LOG_INFO(f"[LLMSummarizer] ===== END RAW RESPONSE =====")
            
            json_str = self._extract_json(content)
            if json_str:
                result = json.loads(json_str)
                
                session_summary = result.get('session_summary', {})
                memory_updates = result.get('memory_updates', [])
                
                logger.LOG_INFO(f"[LLMSummarizer] ===== SUMMARIZATION RESULT =====")
                logger.LOG_INFO(f"[LLMSummarizer] session_summary: {session_summary}")
                logger.LOG_INFO(f"[LLMSummarizer] memory_updates count: {len(memory_updates)}")
                for i, mem in enumerate(memory_updates):
                    logger.LOG_INFO(f"[LLMSummarizer] memory[{i}]: type={mem.get('type')}, name={mem.get('name')}, description={mem.get('description')}")
                logger.LOG_INFO(f"[LLMSummarizer] ===== END RESULT =====")
                
                memories = self._process_memory_updates(memory_updates)
                logger.LOG_INFO(f"[LLMSummarizer] processed memories count: {len(memories)}")
                
                logger.LOG_INFO(f"[LLMSummarizer] ===== SUMMARIZATION COMPLETE =====")
                return session_summary, memories
            else:
                logger.LOG_FATAL(f"[LLMSummarizer] failed to extract JSON from response")
                return None, []
                
        except Exception as e:
            logger.LOG_FATAL(f"[LLMSummarizer] ===== SUMMARIZATION FAILED =====")
            logger.LOG_FATAL(f"LLM summarization error: {e}")
            import traceback
            logger.LOG_FATAL(f"Traceback: {traceback.format_exc()}")
            logger.LOG_FATAL(f"[LLMSummarizer] ===== END FAILED =====")
            return None, []

    def _process_memory_updates(self, updates: List[Dict]) -> List[Memory]:
        """处理记忆更新"""
        memories = []
        for update in updates:
            mem_type = update.get('type', 'user')
            action = update.get('action', 'create')
            name = update.get('name', '')
            content = update.get('content', '')
            description = update.get('description', '')
            
            if not name or not content:
                continue
            
            try:
                memory_type = MemoryType(mem_type)
            except ValueError:
                memory_type = MemoryType.USER
            
            memory = Memory(
                name=name,
                description=description,
                type=memory_type,
                scope=MemoryScope.PRIVATE if memory_type in [MemoryType.USER, MemoryType.FEEDBACK] else MemoryScope.TEAM,
                content=content,
                source_sessions=[self.session_id],
            )
            memories.append(memory)
        
        return memories


async def run_llm_summarization(session_id: str, user_id: str) -> None:
    """执行 L5 摘要的主函数"""
    summarizer = LLMSummarizer(session_id, user_id)
    
    session_summary, memories = await summarizer.run_summarization()
    
    if session_summary:
        _update_session_context_with_summary(session_id, session_summary)
    
    for memory in memories:
        existing = memory_store.get_memory(memory.type, memory.name)
        if existing:
            existing.content = memory.content
            existing.description = memory.description
            existing.source_sessions = list(set(existing.source_sessions + memory.source_sessions))
            memory_store.save_memory(existing)
        else:
            memory_store.save_memory(memory)
    
    if memories:
        global_context_manager.update_from_memories(memories)
    
    _compress_history_messages(session_id)


def _update_session_context_with_summary(session_id: str, summary: Dict) -> None:
    """用 LLM 摘要更新会话上下文"""
    context_file = get_session_context_file(session_id)
    if not context_file.exists():
        return
    
    content = context_file.read_text(encoding='utf-8')
    
    topic = summary.get('topic', '待确定')
    task = summary.get('task', '待确定')
    progress = summary.get('progress', [])
    
    progress_md = '\n'.join(f"- [ ] {p}" for p in progress) if progress else "- 无"
    
    lines = content.split('\n')
    new_lines = []
    in_task = False
    in_progress = False
    
    for line in lines:
        if '### 主题' in line:
            new_lines.append(line)
            new_lines.append(f"- {topic}")
            in_task = False
            in_progress = False
        elif '### 当前任务' in line:
            new_lines.append(line)
            new_lines.append(f"- {task}")
            in_task = True
            in_progress = False
        elif in_task and line.startswith('- '):
            continue
        elif '### 对话进度' in line:
            new_lines.append(line)
            new_lines.append(progress_md)
            in_task = False
            in_progress = True
        elif in_progress and line.startswith('- ['):
            continue
        else:
            new_lines.append(line)
    
    context_file.write_text('\n'.join(new_lines), encoding='utf-8')


def _compress_history_messages(session_id: str) -> None:
    """压缩历史消息"""
    msg_store = create_message_store(session_id)
    messages = msg_store.load_messages()
    
    if len(messages) <= conf.SUMMARIZE_KEEP_MESSAGES:
        return
    
    keep_messages = messages[-conf.SUMMARIZE_KEEP_MESSAGES:]
    
    summary_text = "以下是对话的历史摘要:\n"
    for msg in messages[:-conf.SUMMARIZE_KEEP_MESSAGES]:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')[:200]
        summary_text += f"- [{role}]: {content}\n"
    
    summary_file = get_session_messages_dir(session_id) / '_summary.md'
    summary_file.write_text(summary_text, encoding='utf-8')
    
    for f in get_session_messages_dir(session_id).iterdir():
        if f.suffix == '.md' and f.stem[0:3].isdigit():
            num = int(f.stem.split('_')[0])
            if num <= len(messages) - conf.SUMMARIZE_KEEP_MESSAGES:
                f.unlink()