---
title: SSE Stream
type: tag
tags: [sse, stream]
created: 2026-04-08
updated: 2026-04-08
summary: Server-Sent Events 流式传输相关
---

## SSE 流式传输

Server-Sent Events (SSE) 是一种服务端推送技术，允许服务器通过 HTTP 连接向客户端推送数据。

### 特点

- 单向通信（服务端 → 客户端）
- 基于 HTTP 协议
- 自动重连
- 轻量级替代 WebSocket

### 在 AI Chat 中的应用

```
POST /chat/send → StreamResponse → event: chunk → 前端 Fetch API
```

### 相关页面

- [[ai-chat-design]] - AI Chat 设计
- [[ai-chat-summary]] - 摘要