---
title: AI Chat 对话界面设计
type: concept
tags: [ui, ai, chat, sse, stream, vue, yeab]
created: 2026-04-08
updated: 2026-04-08
sources: [sources/record/ai_chat_design.md]
summary: 将 Todo List 替换为 AI Chat 对话框，采用 SSE 流式输出，支持 Markdown 渲染
---

## 摘要

将前端界面右边的 Todo List 替换为 AI Chat 对话框，采用 Vue 2 + element-ui 前端和 Python aiohttp + yeab 框架后端，通过 SSE (Server-Sent Events) 实现流式输出，支持 Markdown 渲染和设备级 Session 管理。

---

## 技术架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 2 + element-ui | 组件化开发 |
| 后端 | Python aiohttp + yeab | 自研框架 |
| AI | MiniMax API (OpenAI compatible) | 流式输出 |
| 通信 | SSE | 单向流式传输 |

### 流式响应流程

```
前端 → POST /chat/send → 后端 → OpenAI API (stream=True) → SSE chunk → 前端
```

---

## 前端设计

### 组件结构

```
ChatList/
├── chat.vue      # 主聊天组件
└── message.vue   # 消息气泡（含 Markdown）
```

### 核心功能

- 回车发送，Shift+Enter 换行
- 输入框拖动扩展
- 消息列表自动滚动
- Markdown 渲染（marked + highlight.js）
- 设备级 Session 管理（UUID 存储在 localStorage）

---

## 后端设计

### 核心模块

| 模块 | 文件 | 说明 |
|------|------|------|
| Handler | `www/handlers/chat/chat.py` | 流式响应 |
| DAO | `www/dao/chat_message.py` | 消息持久化 |
| 装饰器 | `lib/yeab/web.py` | @stream 装饰器 |

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat/send` | POST (SSE) | 流式发送消息 |
| `/chat/history` | POST | 获取历史 |
| `/chat/clear` | POST | 清空会话 |

---

## 交互设计

- 回车发送，无需按钮
- 输入框支持向上拖动扩大
- AI 思考时显示加载动画
- 清空对话需确认

---

## 相关链接

[[ai-chat-summary]] [[ui]] [[sse]] [[ai-chat]]