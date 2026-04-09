---
title: AI Chat Context Management
type: entity
tags: [ai, chat, context, memory, vue, yeab, tool-call]
created: 2026-04-08
updated: 2026-04-08
sources: [ai_chat_context_management.md]
summary: AI Chat 对话框的上下文管理系统，支持 Markdown 文件持久化和智能摘要
---

# AI Chat Context Management

AI Chat 对话框的上下文管理系统设计方案，支持流式输出、思考过程展示、消息持久化和智能上下文管理。

## 核心功能

- 流式输出展示（SSE）
- 思考过程展示（reasoning_content）
- 消息持久化（Markdown 文件）
- 工具调用追踪
- 智能上下文摘要管理
- Mock/Real 切换

## 技术栈

- 前端：Vue 2 + element-ui + webpack 3
- 后端：Python aiohttp + 自研 yeab 框架
- AI：MiniMax API（支持 reasoning_content 思考过程）

## 目录结构

```
chat_sessions/{session_id}/
├── _context.md          # 上下文管理器
├── 001_user.md          # 用户消息
├── 002_assistant.md     # AI 回复（含 reasoning + tool_calls）
└── ...
```

## 上下文管理设计

### 摘要触发条件（细粒度混合策略）

| 条件 | 阈值 |
|------|------|
| 消息数量 | 20 条 |
| Token 数量 | 3000 tokens |
| 累计新增 Token | 2000 tokens |
| 无工具调用轮次 | 2 轮 |
| 防抖间隔 | 5 分钟 |

### 工具调用追踪

相比 Claude Code，我们记录更完整的工具调用信息：

```markdown
tool_calls:
  - tool: Read
    args: {file: "src/main.py"}
    result: {lines: 50, preview: "import..."}
  - tool: Edit
    args: {file: "src/main.py", old: "xxx", new: "yyy"}
    result: {success: true, lines_changed: 3}
has_tool_call: true
tool_call_count: 2
```

### _context.md 内容结构

```markdown
## 元信息
- session_id, 创建时间, 消息总数

## 会话统计
- 总 Token 数, 距上次摘要, 新增 Token, 工具调用次数

## 关键信息
- 主题、用户信息、当前任务、重要实体、对话进度

## 最近对话（完整）
保留最近 10 条消息

## 历史摘要
分阶段摘要
```

## Mock/Real 切换

配置文件 `conf/dev.py`：
```python
USE_MOCK_CHAT = True   # True=Mock, False=真实AI
```

## 与 Claude Code 对比

| 特性 | Claude Code | 我们的设计 |
|------|-------------|-----------|
| 摘要触发 | token>10k + 新增>5k + 无工具调用 | 消息20条 或 token>3k 或 新增>2k 或 连续2轮无工具调用 |
| 工具调用追踪 | 有 | 有（完整记录） |
| 防抖机制 | 无 | 有（5 分钟） |
| 并发控制 | 无 | 摘要锁定机制 |

## 相关链接

- [[ai-chat-design]] - AI Chat 设计方案
- [[claude-code-harness]] - Claude Code 架构参考
