---
title: Claude Code Prompt System
type: concept
tags: [agent, prompt, llm, claude]
created: 2026-04-08
updated: 2026-04-08
sources: [claude-code-prompt-system.md]
summary: Claude Code 的提示词系统是分层、可缓存、可扩展的 prompt pipeline，驱动整个 Agent 运行时
---

# Claude Code Prompt System

Claude Code 的提示词系统不是一条 system prompt，而是一条**分层、可缓存、可扩展的 prompt pipeline**。

## 核心架构

提示词来自九个来源：

1. **静态 system prompt 主体** - 身份、任务规范、工具使用规则
2. **动态 system sections** - section registry 做求值、memoization、缓存区分
3. **`userContext`** - 来自 CLAUDE.md / rules / memory，经 `prependUserContext()` 以 meta user message 注入
4. **`systemContext`** - 来自 git status 与 cache breaker
5. **slash command / skills / plugins** - 扩展为 prompt 或 fork agent
6. **agents** - 子代理有独立的 prompt domain
7. **MCP instructions** - MCP server 自带 instructions
8. **tool instructions** - 每个工具的 `prompt()` 进入 API 请求
9. **compaction 体系** - 长会话治理机制

## 六层提示词体系

| 层次 | 定义 |
|------|------|
| 身份层 | Claude Code 官方 CLI、interactive agent |
| 行为规范层 | 不擅自加功能、先读再改、如实汇报、高风险确认 |
| 工具协议层 | 工具 prompt、schema、权限模式、并行规则 |
| 上下文层 | userContext、systemContext、attachments、memory、MCP |
| 会话治理层 | compact、summarize、microcompact、context collapse |
| 代理化扩展层 | slash command、skills、plugins、agents、MCP |

## 缓存边界设计

`SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 标记将 prompt 分为：
- **静态块**：可全局缓存（`scope: 'global'`）
- **动态块**：用户/会话特异，不应缓存

Claude Code 从 prompt 设计阶段就把缓存命中作为一等公民来规划。

## userContext 的特殊设计

`userContext` 不进 system prompt，而是通过 `prependUserContext()` 作为 **meta user message** 注入。

这是有意为之的设计选择——把长期规则放在 user message 层而非 system prompt 层。

## 关键机制

- **CLAUDE.md / rules / memory 优先级**：Managed memory → User memory → Project memory → Local memory
- **slash command 三层本质**：本地命令 / prompt command / fork agent
- **agent 独立 prompt domain**：自己的 system prompt、工具池、MCP 连接、memory 与权限模式
- **MCP 双重作用**：工具层（tool schema）+ 指令层（instructions）

## 相关链接

- [[claude-code-harness]] - Claude Code 完整源码分析
- [[ai-chat-context-management]] - AI Chat 上下文管理设计
