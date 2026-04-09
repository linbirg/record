# 【万字】拆完 Claude Code 51万行源码后，我才明白什么叫 Harness

> 来源：微信公众号 - 叶小钗
> 原文：https://mp.weixin.qq.com/s/7aXrDQuQ6djodhdZU3Fy4w

## 核心观点

Claude Code 的源码（TypeScript / Bun 运行时，约 1900 个源文件，51w+ 行代码）展示了一个完整的 **Agent Harness** 工程实现。

**Harness 的定义**：把模型能力变成稳定执行能力的那套工程化装置。解决的从来不是"模型会不会答"，而是"模型能不能在真实环境里持续、稳定、可验证地把事做完"。

Claude Code 认真处理了 Agent 落地时最麻烦的那批工程问题：
- 长链路执行
- 工具并发
- 权限分层
- 记忆沉淀
- 压缩恢复
- 子代理协作

---

## 一、按下回车之后发生了什么

### UI 层

整个界面最核心的组件叫 `REPL.tsx`（5000+ 行），底层是 React 应用，用 Ink 框架渲染在终端里。

### onSubmit 流程

1. 检查是否是即时命令（`/clear` 等带 `immediate` 标记的斜杠命令，直接执行不经过模型）
2. 处理边缘情况（中断恢复、上下文恢复）
3. 加入历史记录
4. 调用 `handlePromptSubmit()` → `onQuery()`

### 图片处理管线

入口：`src/utils/imagePaste.ts`

```
剪贴板 → 多级压缩 → base64 封装
```

压缩策略：
- 尺寸和大小都合规直接用
- 文件大了但尺寸没问题 → PNG 调色板压缩
- 尺寸超了 → 等比缩放
- 缩放后太大 → JPEG 各级质量
- 一定要压到 API 能接受的程度

---

## 二、系统提示词

入口：`src/constants/prompts.ts`，核心函数 `getSystemPrompt()`

### 提示词的九大来源

1. 静态 system prompt 主体
2. 动态 system sections
3. userContext（CLAUDE.md / rules / memory / 日期）
4. systemContext（git status / cache breaker）
5. slash command / skills / plugins
6. agents
7. MCP instructions
8. tool instructions
9. compaction 体系

### 缓存友好的设计

**基本不变的内容**（标记 `cache_control: ephemeral`）：
- 身份和角色
- 系统指令（Markdown 渲染规则、权限模式说明、注入攻击防御）
- 编码哲学
- 工具使用指南
- 语气风格

**每轮刷新的内容**：
- 环境信息（当前目录、git 分支、平台信息）
- 用户上下文（CLAUDE.md、MEMORY.md）
- MCP 指令
- 技能列表
- Hook 指令

### 工具列表按字母排序

不是为了美观，而是为了 **prompt cache 稳定性**。每次 API 调用都带完整工具列表，顺序变化会导致缓存失效。

### 环境信息注入

每轮查询时嵌入：
- 当前工作目录的绝对路径
- 当前 git 分支名和最近几条提交
- 操作系统和 shell 类型
- 模型知识截止日期

模型据此推断该从哪些文件开始找。

---

## 三、工具与技能

### 工具（Tool）

模型可以直接调用的函数：
- Read、Bash、Edit、Glob、Grep 等
- 通过 `tool_use` 类型内容块表达调用意图
- 每个工具实现统一接口：参数校验、执行逻辑、权限检查、`isConcurrencySafe`、`isReadOnly`

### 技能（Skill）

能力增强模块，触发方式：
1. 用户显式输入斜杠命令（`/commit`、`/compact`）
2. 模型自动匹配触发（用户说"帮我提交代码"，模型自动调用 commit 技能）

**本质**：预设的 prompt 模板，展开后变成详细指令。

**一句话区分**：工具是 Tools，技能是模型可以主动匹配并加载的提示词模板。

### 工具过滤三步

```
getAllBaseTools() → getTools() → assembleToolPool()
```

1. 收集所有内置工具，根据 Feature Flag 过滤
2. 移除被用户禁用的工具
3. 合并内置工具和 MCP 外部工具，按字母排序，去重

### 工具分类

```
- 文件操作：Read / Edit / Write / NotebookEdit
- 搜索：Glob / Grep
- 执行：Bash
- 代理：AgentTool / TeamCreate / SendMessage
- 任务：TaskCreate / TaskUpdate / TaskList / TaskOutput / TaskStop
- 网络：WebFetch / WebSearch
- 模式：EnterPlanMode / ExitPlanMode / EnterWorktree / ExitWorktree
- 调度：CronCreate / CronDelete / CronList
- 交互：AskUserQuestion
- 集成：Skill / ToolSearch / LSP / MCP
```

---

## 四、查询循环

核心文件：`src/query.ts`，核心是 `while(true)` 的 `queryLoop()`

### 流程

```
1. 压缩检查
2. 组装消息（系统提示词 + 历史消息 + 当前消息）
3. 调用 API（POST /v1/messages，stream: true）
4. 流式接收响应
   - 文本实时渲染
   - tool_use 块交给 StreamingToolExecutor
5. 执行工具
   - 根据 isConcurrencySafe 决定并行/串行
   - 权限检查
6. 判断是否继续（检查 toolUseBlocks 是否为空）
```

### StreamingToolExecutor

- 不等所有 `tool_use` 到齐再执行
- 收到一个 `tool_use` 就开始执行
- Read、Grep 标记 `isConcurrencySafe = true`，可以并行
- Edit 标记 `isConcurrencySafe = false`，必须串行

### 并行调度机制

```typescript
// 队列系统：每个工具完成后重新触发队列处理
promise.finally(() => processQueue())

// 等待结果时用 Promise.race 逐个等
// 如果并行工具中有一个失败，其他并行工具会被取消
```

---

## 五、权限系统

### 权限模式（从严到宽）

```
plan → default → acceptEdits → auto → dontAsk → bypassPermissions
```

- `default`：普通用户最常用，危险操作弹确认框
- `auto`：用分类器自动判断操作是否安全
- `plan`：所有写操作直接拒绝

### 权限检查流水线（五步）

```
1. 看你有没有明确禁止（settings.json deny 规则）
2. 看有没有标记为需要询问
3. 工具自己的权限逻辑（BashTool 用 shell-quote + LLM 语义分析）
4. 根据权限模式做决策
5. Hook 系统一票否决
```

### Bash 命令风险判断

用 `shell-quote` 库做命令结构化解析，再用 **LLM 做语义分析**判断风险等级：
- `ls`、`git status` → LOW
- `npm install`、`docker build` → MEDIUM
- `rm -rf`、`sudo`、`git push --force` → HIGH

---

## 六、记忆系统

### 两条并行加载管线

**管线一**：读取记忆文件实际内容
- `getMemoryFiles()` 发现文件
- `getClaudeMds()` 格式化文本
- 注入到用户上下文

**管线二**：注入行为指令
- 告诉模型"你有一本笔记可以写，规则是这样的"

### 四层记忆

#### 第一层：CLAUDE.md

文件发现优先级（从低到高）：
1. 管理员指令：`/etc/claude-code/CLAUDE.md`（Linux）或 `/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS）
2. 用户全局指令：`~/.claude/CLAUDE.md` 和 `~/.claude/rules/*.md`
3. 项目指令：从 cwd 向上遍历到根，收集沿途所有 `CLAUDE.md`、`.claude/CLAUDE.md`、`.claude/rules/*.md`、`CLAUDE.local.md`

**优先级规则**：越靠近当前位置的文件，加载顺序越靠后，优先级越高。

**CLAUDE.local.md**：加入 `.gitignore`，只在自己本地生效，适合个人偏好。

#### 第二层：MEMORY.md

- 存放在 `~/.claude/projects/<项目路径>/memory/`
- 由**子代理**在后台自动维护
- 子代理继承父对话的 prompt cache（成本极低）

**触发条件**（组合判断）：
- 累计 token > 10000
- 距上次提取新增 token > 5000
- 距上次提取工具调用 > 3 次
- 最近一轮没有工具调用（进入"总结"阶段）

#### 第三层：Session Memory

- 面向当前会话的运行摘要
- 记录当前正在做什么、做到哪一步了
- 保存在磁盘上，新会话启动时会读取

#### 第四层：上下文压缩

**Micro 压缩**（最轻量）：
- 每轮查询前都跑
- 不生成摘要，不调 API
- 把旧工具返回值替换成 `[Old tool result content cleared]`

**完整压缩**（两条路径）：

路径一（优先）：Session Memory 压缩
- 直接拿 Session Memory 文件当摘要
- 保留近期消息（至少 5 条、至少 1w tokens）
- 不调 API

路径二（回退）：标准压缩
- 调 API 让模型现场写摘要
- 所有消息被替换，一条近期消息都不保留

---

## 七、流式响应

### SSE 事件序列

```
message_start           → token 使用量、模型信息
content_block_start     → 开始一个内容块
content_block_delta × N → 文本片段或 tool_use 参数片段
content_block_stop      → 当前内容块结束
message_stop           → 整个响应结束
```

### 错误处理

- 429 限流 → 指数退避重试
- 500/502/503 → 重试
- 401 认证过期 → 自动刷新 OAuth Token
- Prompt Too Long → 触发压缩后重试
- Max Output Tokens → 缩短输出限制后重试

---

## 八、完整链路回顾

场景："帮我修 bug + 截图"

```
1. 按下回车
   → REPL.tsx 的 onSubmit() 触发
   → imagePaste.ts 处理图片
   → 组装成 UserMessage

2. 查询准备
   → 并行：getSystemPrompt() + assembleToolPool() + compact 检查

3. 第一轮 API 调用
   → 模型返回：文本（识别图片错误）+ tool_use（要求 Read 文件）

4. Read 工具执行
   → 权限检查通过 → 读文件 → 返回内容

5. 第二轮 API 调用
   → 模型返回：tool_use（要求 Edit 修改文件）

6. Edit 工具执行
   → 权限检查流水线 → 弹出确认框 → 用户按 Y → 执行

7. 第三轮 API 调用
   → 模型确认修复完成，无新工具请求

8. 循环结束
   → 最终回复渲染到终端
```

---

## 九、关键设计模式总结

### 1. 子代理模式

压缩、记忆提取这些"管理对话"的操作，通过创建子代理完成：
- 子代理共享父对话的 prompt cache，成本极低
- 把"管理对话"和"回答问题"分成独立关注点

### 2. 流式工具执行

- 不等所有 `tool_use` 到齐再执行
- 能并行的并行，必须串行的排队
- 在模型一次请求多个工具的场景下减少等待时间

### 3. 多层权限模型

- 命令解析结合 `shell-quote` 结构化分析和 LLM 语义理解
- YOLO 分类器用 LLM 判断操作安全性
- Hook 系统给用户留一票否决的最终手段

### 4. Prompt Cache 友好设计

- 系统提示词分静态和动态两段
- 工具列表按字母排序
- 缓存命中时成本降约 90%

### 5. 多层记忆协作

| 记忆层 | 职责 | 跨会话 |
|--------|------|--------|
| CLAUDE.md | 手动写的规则 | ✅ |
| MEMORY.md | 自动维护的长期记忆 | ✅ |
| Session Memory | 当前会话运行摘要 | ❌ |
| Compact 摘要 | 压缩后的历史 | ❌ |

---

## 十、结论：Harness

Claude Code 真正展示的是如何把模型能力包进一整套可以持续运行的工程系统。

**Harness 要解决的**：
- 长链路执行
- 工具并发
- 权限分层
- 记忆沉淀
- 压缩恢复
- 子代理协作

**Claude Code 的价值**：
- 全局视角理解 Agent Runtime / Harness
- 适合外围赏析，不适合深度研究
- 学习体验不如 OpenClaw（可调试、链路外露）

---

## 相关链接

- [Claude Code 提示词系统深度拆解](./claude-code-prompt-system.md)
- [万字：Agent概述](https://mp.weixin.qq.com/s?__biz=Mzg2MzcyODQ5MQ==&mid=2247497903&idx=1&sn=fe906b46bf43a88050c22d7a78b701b2)
- [万字：理解LangChain](https://mp.weixin.qq.com/s?__biz=Mzg2MzcyODQ5MQ==&mid=2247498404&idx=1&sn=aa2f76729ea55ad24c408456a5009a47)
