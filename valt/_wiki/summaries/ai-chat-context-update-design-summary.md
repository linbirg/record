---
title: AI Chat 上下文自动更新设计
type: summary
tags: [ai-chat, context-management, llm, memory]
created: 2026-04-10
updated: 2026-04-10
sources: [sources/design/ai-chat-webflow/ai_chat_context_update_design.md]
summary: AI Chat 上下文自动更新设计方案，包括会话级日常摘要（每5轮）和 L5 深度摘要（触发条件），以及记忆提取策略。
---

## 摘要

本文档设计 AI Chat 系统的上下文自动更新机制，包括两个层次：

1. **会话级日常摘要** - 每5轮对话执行一次，使用简单规则匹配（非 LLM），更新会话 context
2. **L5 深度摘要** - 当满足触发条件时（消息数≥20/token≥8000/累计新增≥3000/无工具调用≥2轮），调用 LLM 进行深度摘要和记忆提取

## 核心流程

```
用户发送消息 → LLM 返回 → 保存消息 → 日常摘要(每5轮) → 检查L5条件 → 深度摘要+记忆提取
```

## LLM 摘要 Prompt 设计

将 prompt 从 user 消息移到 system 消息，添加格式兼容性处理（`_normalize_result`），temperature=0.1 提高格式稳定性。

## 相关链接

[[ai-chat-context-management]] - AI Chat 上下文管理实体页
[[ai-chat-design]] - AI Chat 设计实体页
[[ai-chat-webflow]] - AI Chat Webflow 概念页