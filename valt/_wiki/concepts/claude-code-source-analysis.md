---
title: Claude Code Source Code Deep Analysis
type: concept
tags: [agent, claude, source-code, typescript, architecture]
created: 2026-04-09
updated: 2026-04-09
sources: [claude-code-source-analysis.md]
summary: 基于 Claude Code v2.1.88 泄露源码（51万行TypeScript）的完整技术架构分析
---

# Claude Code Source Code Deep Analysis

基于 Claude Code v2.1.88 泄露源码（51 万行 TypeScript）的完整技术架构分析。

## 核心信息

| 项目 | 说明 |
|------|------|
| 源码版本 | Claude Code v2.1.88（npm source map 泄露版） |
| 代码规模 | 约 1900 个 TypeScript 文件、51 万行代码 |
| 发布日期 | 2026 年 3 月 31 日 |
| GitHub Star | 一天内获得 8 万+ |

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 语言 | TypeScript + TSX | 全类型安全 |
| UI 框架 | React + Ink（深度 fork） | 终端渲染引擎 |
| 运行时 | Bun 1.3.5+ | 编译时 dead code elimination |
| CLI 框架 | Commander.js | 命令行参数解析 |
| Schema 验证 | Zod v4 | 运行时类型检查 |
| AI SDK | @anthropic-ai/sdk v0.80.0 | Anthropic 官方 SDK |
| MCP | @modelcontextprotocol/sdk | 工具协议 |
| 布局引擎 | 自研 Yoga-layout TS 移植 | Flexbox 终端布局 |
| Feature Flag | GrowthBook（89 个编译时开关） | 灰度控制 |
| 认证 | OAuth 2.0 + JWT + macOS Keychain | 多 Provider |
| 遥测 | OpenTelemetry + gRPC + BigQuery | 全链路追踪 |

## 核心模块

| 模块 | 职责 | 关键文件 |
|------|------|----------|
| query.ts | LLM 查询引擎（1729 行） | queryLoop、while(true) AsyncGenerator |
| Tool.ts | 工具接口定义（794 行） | Tool 类型、buildTool 工厂 |
| coordinator/ | 多 Agent 编排（370 行） | 300 行 system prompt 驱动 |
| tools/ | 40+ 工具定义 | BashTool、FileEditTool、AgentTool 等 |
| services/ | 后端服务层 | api/、mcp/、compact/、analytics/ |
| hooks/ | 87 个 React hooks | useCanUseTool、useMergedTools 等 |
| components/ | 144 个 UI 组件 | 权限对话框、REPL 界面等 |

## 文档目录

1. 项目概览与技术栈
2. 整体架构与模块结构
3. 核心引擎：Query 循环
4. Agent 系统
5. Coordinator 多 Agent 编排
6. 工具系统
7. 安全系统
8. 上下文压缩系统
9. Prompt Cache 优化策略
10. 记忆系统
11. 推测执行系统
12. API 调用与重试机制
13. 权限决策系统
14. 状态管理与启动流程
15. MCP 集成
16. Bridge 远程会话
17. Buddy 宠物系统
18. Ink 终端渲染引擎
19. UI 组件系统
20. 测试与验证
21. 框架对比分析
22. 总结与启示

## 相关链接

- [[claude-code-prompt-system]] - Claude Code 提示词系统分析
- [[claude-code-harness]] - Claude Code Harness 架构分析
