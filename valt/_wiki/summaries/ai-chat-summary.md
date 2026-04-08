---
title: AI Chat 设计摘要
type: summary
tags: [ui, ai, chat]
created: 2026-04-08
updated: 2026-04-08
sources: [sources/record/ai_chat_design.md]
summary: Todo→AI Chat 重构方案，Vue前端+SSE流式后端+MiniMax API
---

## 概述

将现有 Todo List 组件替换为 AI Chat 对话框。

## 核心技术点

1. **SSE 流式输出** - 后端采用 `@stream` 装饰器实现流式响应
2. **Session 管理** - 设备级 UUID，会话持久化
3. **Markdown 渲染** - marked + highlight.js + DOMPurify

## 文件清单

| 类型 | 文件数 | 说明 |
|------|--------|------|
| 前端组件 | 3 | chat.vue, message.vue, rightSide.vue |
| 前端逻辑 | 1 | store/index.js |
| 后端模块 | 4 | chat.py, chat_message.py, field_desc.py, web.py |
| 迁移脚本 | 1 | 7_chat_message.py |

## 状态

- [x] 前端界面完成
- [x] 后端框架完成
- [ ] 数据库迁移待执行
- [ ] 联调测试待完成

---

## 相关链接

[[ai-chat-design]] [[ui]] [[sse]]