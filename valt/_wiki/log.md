# Wiki Log

## 2026-04-23

### ingest

- [ingest] sources/ai-agents/kimi-agent-task-platform-2026-04-23.md (from Kimi)

---

## 2026-04-10

### ingest

- [ingest] sources/design/ai-chat-webflow/ai_chat_context_update_design.md
- [ingest] sources/ai-agents/claude-code-12-harness-patterns.md (从微信公众号)

### compile

- [compile] sources/design/ai-chat-webflow/ai_chat_context_update_design.md → summaries/ai-chat-context-update-design-summary.md
- [compile] sources/ai-agents/claude-code-12-harness-patterns.md → concepts/claude-code-12-harness-patterns.md
- [create] tags/agent.md
- [update] _wiki/index.md
- [update] _raw/registry.md

### lint

- [check] 12 wiki links verified, 0 broken links
- [update] tags/ai-chat.md (add new summary reference)

---

## 2026-04-09

### ingest

- [ingest] sources/ai-agents/Claude Code 源码深度技术分析.docx → claude-code-source-analysis.md
- [convert] docx to markdown using Python zipfile + XML parsing

### compile

- [compile] sources/ai-agents/claude-code-source-analysis.md → concepts/claude-code-source-analysis.md
- [update] _wiki/index.md
- [update] _raw/registry.md

---

## 2026-04-08

### compile

- [compile] sources/ai-agents/claude-code-prompt-system.md → concepts/claude-code-prompt-system.md
- [compile] sources/ai-agents/claude-code-harness-analysis.md → concepts/claude-code-harness.md
- [compile] sources/design/ai-chat-webflow/ai_chat_context_management.md → entities/ai-chat-context-management.md
- [compile] sources/design/ai-chat-webflow/ai_chat_design.md → entities/ai-chat-design.md
- [update] _wiki/index.md
- [update] _raw/registry.md

### 内容更新

- [create] Claude Code Prompt System 概念页
- [create] Claude Code Harness Architecture 概念页
- [create] AI Chat Context Management 实体页
- [create] AI Chat Context Management Summary 摘要页
- [delete] sources/design/ai-chat-webflow/SKILL.md (已合并)

### 设计文档

- [create] sources/design/ai-chat-webflow/ai_chat_context_management.md (AI Chat 上下文管理系统设计)
- [create] sources/ai-agents/claude-code-prompt-system.md (Claude Code 提示词系统)
- [create] sources/ai-agents/claude-code-harness-analysis.md (Claude Code Harness 分析)

### 设计方案完善

- [update] ai_chat_context_management.md - 增加工具调用追踪字段
- [update] ai_chat_context_management.md - 细粒度摘要触发条件
- [update] ai_chat_context_management.md - 增加 Claude Code 对比章节
- [update] ai_chat_context_management.md - 完善摘要 Prompt

---

## 历史记录

### 2026-04-08 (早期)

- [compile] sources/record/ai_chat_design.md
- [move] record, design → sources/
- [recompile] 重组 wiki 结构
- [create] sources/design/ai-chat-webflow/SKILL.md
- [compile] ai-chat-webflow.md
- [implement] chat.vue, message.vue Webflow 风格升级
