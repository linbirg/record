---
title: Claude Code Harness Architecture
type: concept
tags: [agent, harness, claude, architecture]
created: 2026-04-08
updated: 2026-04-08
sources: [claude-code-harness-analysis.md]
summary: Claude Code 展示了完整的 Agent Harness 工程实现，解决长链路执行、工具并发、权限分层等问题
---

# Claude Code Harness Architecture

Claude Code 源码（TypeScript / Bun 运行时，约 1900 个源文件，51w+ 行代码）展示了一个完整的 **Agent Harness** 工程实现。

## Harness 的定义

把模型能力变成稳定执行能力的那套工程化装置。解决的从来不是"模型会不会答"，而是"模型能不能在真实环境里持续、稳定、可验证地把事做完"。

## 解决的六大工程问题

1. **长链路执行** - while(true) 查询循环，多轮 API 调用
2. **工具并发** - StreamingToolExecutor 按 isConcurrencySafe 决定并行/串行
3. **权限分层** - 五步权限检查流水线 + Hook 一票否决
4. **记忆沉淀** - CLAUDE.md / MEMORY.md / Session Memory / 上下文压缩四层协作
5. **压缩恢复** - Micro 压缩 / Session Memory 压缩 / 标准压缩三种机制
6. **子代理协作** - 压缩、记忆提取通过子代理完成，共享父 prompt cache

## 消息处理链路

```
用户按下回车 → REPL.tsx onSubmit → 图片处理管线 → 
getSystemPrompt() + assembleToolPool() → 
queryLoop() → POST /v1/messages → 
StreamingToolExecutor → 权限检查 → 工具执行 → 判断是否继续
```

## 查询循环机制

核心是 `while(true)` 的 `queryLoop()`：
1. 压缩检查
2. 组装消息（系统提示词 + 历史消息 + 当前消息）
3. 调用 API（stream: true）
4. 流式接收响应
5. 执行工具（Read/Grep 并行，Edit 串行）
6. 判断是否继续（检查 toolUseBlocks 是否为空）

## 记忆系统四层

| 层级 | 类型 | 跨会话 |
|------|------|--------|
| CLAUDE.md | 手动规则 | ✅ |
| MEMORY.md | 自动长期记忆 | ✅ |
| Session Memory | 当前会话摘要 | ❌ |
| Compact 摘要 | 压缩历史 | ❌ |

## 流式工具执行

- 不等所有 `tool_use` 到齐再执行
- 收到一个 `tool_use` 就开始执行
- Read、Grep 标记 `isConcurrencySafe = true`，可以并行
- Edit 标记 `isConcurrencySafe = false`，必须串行

## 权限检查五步

```
1. 用户明确禁止（settings.json deny 规则）
2. 标记为需要询问
3. 工具自己的权限逻辑（BashTool: shell-quote + LLM 语义分析）
4. 权限模式决策（bypassPermissions / auto / default）
5. Hook 系统一票否决
```

## 相关链接

- [[claude-code-prompt-system]] - Claude Code 提示词系统
- [[ai-chat-context-management]] - AI Chat 上下文管理设计
