---
title: Claude Code 12 Agentic Harness 设计模式
type: concept
tags: [agent, claude, harness, architecture, memory, workflow, tool, automation]
created: 2026-04-10
updated: 2026-04-10
sources: [sources/ai-agents/claude-code-12-harness-patterns.md]
summary: Claude Code 源码中提炼的 12 个可复用 Agentic Harness 设计模式，分为记忆与上下文、工作流与编排、工具与权限、自动化四类。
---

## 摘要

Claude Code 源码中提炼出的 12 个可复用 Agentic Harness 设计模式，分为四类：**记忆与上下文、工作流与编排、工具与权限、自动化**。这些模式不是空谈的理论，而是从生产级代码中提炼出来的架构智慧。

---

## 一、记忆与上下文

这五个模式是一条逐步演进的路径：持久化指令文件 → 作用域组装 → 分层记忆 → 记忆整合 → 上下文压缩。

### 1. 持久化指令文件模式 (Persistent Instruction File Pattern)

**做法**：放一个项目级的配置文件，每次会话自动加载。里面写清楚构建命令、测试方式、架构规则、命名约定。

**适用场景**：需要在多个会话里反复处理同一个代码库。

### 2. 作用域上下文组装模式 (Scoped Context Assembly Pattern)

**做法**：把指令拆到不同作用域里（组织级、用户级、项目根目录、父目录、子目录），Agent 根据当前位置动态加载对应规则。

**适用场景**：Monorepo、多语言项目、不同目录有不同规范的代码库。

### 3. 分层记忆模式 (Tiered Memory Pattern)

**做法**：记忆分层。精简索引始终放在上下文，和当前任务相关的内容按需加载，完整历史留在磁盘上。

**适用场景**：需要跨多次会话保留偏好、决策或状态的 Agent。

### 4. 记忆整合模式 (Dream Consolidation Pattern)

**做法**：加一个后台整理机制，在空闲时定期做清理：去重、删旧、重组结构。

**适用场景**：Agent 会长期运行、持续积累记忆，而且不方便靠人工去维护。

### 5. 渐进式上下文压缩模式 (Progressive Context Compaction Pattern)

**做法**：「分层压缩」。新对话尽量保留细节，旧内容做轻量总结，再往前的逐步压缩成很短的摘要。

**适用场景**：对话轮次比较多（比如 20～30 轮以上）的任务。

---

## 二、工作流与编排

核心思路：**分离**。把读取和写入拆开，把「查资料」和「改代码」的上下文拆开，把顺序执行和并行执行也拆开。

### 6. 探索-规划-行动循环模式 (Explore-Plan-Act Loop Pattern)

**做法**：流程拆成三步，权限逐步放开：
- 先探索，只读代码、查信息、摸清结构
- 再规划，和用户对齐思路
- 最后再动手改代码

**适用场景**：不熟悉的代码库，或者涉及多个文件的复杂修改。

### 7. 上下文隔离子智能体模式 (Context-Isolated Subagents Pattern)

**做法**：任务拆给不同的子 Agent，每个都有自己的上下文和权限：
- 做调研的只负责看和分析，不能改代码
- 做规划的只负责设计方案
- 真正执行的才有完整工具权限

**适用场景**：长会话、多阶段流程，或者不同阶段对上下文要求差异很大的任务。

### 8. 分支-合并并行模式 (Fork-Join Parallelism Pattern)

**做法**：任务拆成多个分支并行处理，每个子 Agent 在独立的代码副本里工作（如用 git worktree），互不干扰，等都完成后再合并。

**适用场景**：可以拆成多个互不依赖子任务的场景。

---

## 三、工具与权限

### 9. 渐进式工具扩展模式 (Progressive Tool Expansion Pattern)

**做法**：先给一小部分常用工具，够用就行；其他工具按需再打开。

**适用场景**：工具很多，但大多数任务其实只用到一小部分。

### 10. 命令风险分类模式 (Command Risk Classification Pattern)

**做法**：在执行前做一层「风险判断」。低风险的命令自动放行，高风险的才需要人工确认或直接拦截。

**适用场景**：Agent 能执行 shell 命令，或者会操作外部系统。

### 11. 单用途工具设计模式 (Single-Purpose Tool Design Pattern)

**做法**：把常见操作拆成专门的工具，比如读文件、改文件、搜索、匹配路径，各自都有明确的输入和边界。

**适用场景**：需要频繁做文件操作或搜索的 Agent。

---

## 四、自动化

### 12. 确定性生命周期钩子模式 (Deterministic Lifecycle Hooks Pattern)

**做法**：把这些动作挂到 Agent 生命周期的关键节点上自动执行，完全不依赖提示词。比如工具调用前后、会话开始、工作目录变化时，系统都会触发对应的钩子。

**适用场景**：存在必须严格执行、不能遗漏的步骤。

---

## 核心总结

这些本质上都是架构层面的决策：

- **内存怎么分层**
- **上下文怎么压缩**
- **权限怎么控制**
- **哪些流程必须自动执行**

模型会变，工具也会换，但这些东西不会很快过时。

---

## 相关链接

[[claude-code-harness]] - Claude Code Harness 架构分析
[[claude-code-prompt-system]] - Claude Code Prompt System
[[claude-code-source-analysis]] - Claude Code 源码分析
[[ai-chat-context-management]] - AI Chat 上下文管理