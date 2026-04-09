---
title: AI Chat Context Management Summary
type: summary
tags: [ai, chat, context, memory]
created: 2026-04-08
updated: 2026-04-08
sources: [ai_chat_context_management.md]
summary: AI Chat 上下文管理系统，支持 Markdown 文件持久化和智能摘要触发
---

# AI Chat Context Management Summary

AI Chat 对话框的上下文管理系统设计方案。

## 核心要点

1. **目录结构**：`chat_sessions/{session_id}/` 下存储消息文件
2. **摘要触发**：消息数达 20 或 Token 超 3000 时触发摘要
3. **上下文文件**：`_context.md` 包含元信息、关键信息、最近消息、历史摘要
4. **Mock/Real 切换**：`conf/dev.py` 中 `USE_MOCK_CHAT` 开关

## 待实现功能

- 向量数据库集成
- 多模态支持
- 上下文压缩算法优化
- 对话导出

## 相关链接

- [[ai-chat-context-management]] - 完整设计文档
- [[claude-code-harness]] - Claude Code 记忆系统参考
