# AI Chat 上下文自动更新实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现会话级别日常摘要（每5轮）、L5触发时的深度摘要+记忆提取、全局上下文更新

**Architecture:** 
- 新增 session_context_manager.py 处理日常摘要（规则匹配）
- 新增 llm_summarizer.py 处理 L5 深度摘要和记忆提取
- 在 chat.py 的消息保存后调用上下文更新

**Tech Stack:** Python aiohttp, MiniMax API, 文件存储

---

## Task 1: 添加配置项 SESSION_SUMMARY_INTERVAL

**Files:**
- Modify: `yail/conf/dev.py:30-40`

**Step 1: 添加配置项**

在 `conf/dev.py` 的 SUMMARIZE 配置后添加:

```python
# === 会话日常摘要 ===
SESSION_SUMMARY_INTERVAL = 5  # 每5轮对话执行一次日常摘要
```

**Step 2: 验证配置**

```bash
cd /mnt/d/project/linbirg/ww/ww/record/yail
python -c "from conf import dev as conf; print(conf.SESSION_SUMMARY_INTERVAL)"
```
Expected: `5`

---

## Task 2: 创建 session_context_manager.py

**Files:**
- Create: `yail/www/handlers/chat/session_context_manager.py`

会话级日常摘要（简单规则匹配，每5轮执行）：
- 提取主题关键词
- 提取当前任务
- 提取技术栈
- 提取用户关键信息
- 提取最近消息
- 更新会话 _context.md

---

## Task 3: 创建 llm_summarizer.py

**Files:**
- Create: `yail/www/handlers/chat/llm_summarizer.py`

L5 触发时的深度摘要和记忆提取：
- 构建 LLM Prompt（最近消息、历史摘要、用户画像、已有关联记忆）
- 调用 LLM（禁用工具）
- 解析 LLM 返回（会话摘要 + 记忆更新）
- 更新会话 context
- 保存/更新记忆
- 更新全局 context
- 压缩历史消息

---

## Task 4: 修改 global_context.py 添加记忆更新方法

**Files:**
- Modify: `yail/www/handlers/chat/global_context.py:260-287`

添加 `update_from_memories` 方法：
- 根据记忆更新用户偏好
- 更新已知项目

---

## Task 5: 修改 chat.py 集成上下文更新

**Files:**
- Modify: `yail/www/handlers/chat/chat.py:260-280`

在 `call_llm_stream` 的消息保存后：
1. 执行会话级别日常摘要（每5轮）
2. 检查 L5 触发条件并执行深度摘要

---

## Task 6: 测试验证

验证所有导入正常，代码可运行。