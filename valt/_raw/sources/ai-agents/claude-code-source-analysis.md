# Claude Code 源码深度技术分析

> 来源：飞书文档
> 基于 Claude Code v2.1.88 泄露源码（51 万行 TypeScript）的完整技术架构分析

---

基于 Claude Code v2.1.88 泄露源码（51 万行 TypeScript）的完整技术架构分析

分析范围：/Users/wille/projects/claude-code/src/源码版本：Claude Code v2.1.88（npm source map 泄露版）

目录

第一章 项目概览与技术栈

第二章 整体架构与模块结构

第三章 核心引擎：Query 循环

第四章 Agent 系统

第五章 Coordinator 多 Agent 编排

第六章 工具系统

第七章 安全系统

第八章 上下文压缩系统

第九章 Prompt Cache 优化策略

第十章 记忆系统

第十一章 推测执行系统

第十二章 API 调用与重试机制

第十三章 权限决策系统

第十四章 状态管理与启动流程

第十五章 MCP 集成

第十六章 Bridge 远程会话

第十七章 Buddy 宠物系统

第十八章 Ink 终端渲染引擎

第十九章 UI 组件系统

第二十章 测试与验证

第二十一章 框架对比分析

第二十二章 总结与启示

第一章 项目概览与技术栈

1.1 基本信息

Claude Code 是 Anthropic 官方发布的 AI 编程助手 CLI，基于 TypeScript/React（Ink）构建，运行在 Node.js/Bun 环境下。2026 年 3 月 31 日，v2.1.88 的 npm 包中意外包含了完整的 source map（59.8 MB），约 1900 个 TypeScript 文件、51 万行代码被泄露到 GitHub，一天内获得 8 万+ Star。

1.2 技术栈

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
| 协议 | MCP SDK + LSP | 工具与语言服务 |

1.3 启动链路

```
Plain Text
entrypoints/cli.tsx     ← 极速路径：--version 直接退出
       ↓
main.tsx               ← 核心入口（4683 行）：参数解析、MCP 初始化、工具加载
       ↓
entrypoints/init.ts    ← 全局初始化：配置、代理、OAuth、遥测、策略限制
       ↓
setup.ts               ← 会话设置：Git 检测、worktree、hooks、插件加载
       ↓
replLauncher.tsx       ← 启动 REPL：App → REPL 组件渲染
```

main.tsx 文件开头的侧效应在模块加载阶段就启动了多个并行任务：startMdmRawRead()（MDM 管理配置读取）和 startKeychainPrefetch()（macOS Keychain 预取），这些操作在 ~135ms 的模块导入时间内并行执行，避免了串行等待。

第二章 整体架构与模块结构

2.1 核心模块

| 目录 | 职责 | 关键文件 |
|------|------|----------|
| query.ts | LLM 查询引擎（1729 行） | queryLoop、while(true) AsyncGenerator |
| Tool.ts | 工具接口定义（794 行） | Tool 类型、buildTool 工厂 |
| coordinator/ | 多 Agent 编排（370 行） | 300 行 system prompt 驱动 |
| tools/ | 40+ 工具定义 | BashTool、FileEditTool、AgentTool 等 |
| services/ | 后端服务层 | api/、mcp/、compact/、analytics/ |
| hooks/ | 87 个 React hooks | useCanUseTool、useMergedTools 等 |
| components/ | 144 个 UI 组件 | 权限对话框、REPL 界面等 |
| state/ | 全局状态管理 | AppState、store、selectors |
| ink/ | 终端渲染引擎 | Yoga 布局、ANSI 渲染、键盘输入 |
| utils/ | 工具函数库（400+ 文件） | permissions/、hooks/、model/ 等 |

2.2 数据流

Plain Text 数据流

```
用户输入 → QueryEngine.submitMessage()
       ↓
queryLoop() [while(true) AsyncGenerator]
       ↓
callModel (streaming) → services/api → Anthropic API
       ↓
StreamingToolExecutor → toolOrchestration (partitionToolCalls)
       ↓
useCanUseTool → hooks/toolPermission → ML Classifier
       ↓
Tool.call() → 60+ 具体工具
       ↓
PostToolUse hooks → handleStopHooks()
       ↓
extractMemories (fork) → memdir/SessionMemory (fork)
PromptSuggestion/speculation (fork)
AgentSummary (fork)
       ↓
AppState → state/store.ts
       ↓
tasks/ → 7 种后台任务类型
       ↓
UI: ink/ → components/ → screens/REPL.tsx
```

2.3 10 条核心设计理念

AsyncGenerator everywhere — query、工具执行、hook 全部用 AsyncGenerator，统一流式处理和中断语义

编译时特性门控 — 89 个 feature() 开关 + Bun DCE，外部构建物理不含内部代码

协调不靠代码靠 prompt — coordinator 模式 ~300 行 system prompt 替代编排引擎

fail-closed 默认 — 工具默认不并发安全、不只读、不安全，需显式声明

五层压缩体系 — snip → microcompact → context collapse → autocompact → reactive compact

Forked Agent 模式 — compact/extractMemories/SessionMemory/AgentSummary/speculation 全部 fork 主对话共享 prompt cache

bootstrap isolation — 全局状态是 import DAG 叶节点，ESLint 规则强制，杜绝循环依赖

Prompt cache 是一等公民 — 系统提示词静态/动态分段、beta header sticky latch、工具 schema 延迟加载、fork agent 共享 cache

性能是一等公民 — 字符串 interning、DECSTBM 硬件滚动、blit 优化、帧时间追踪

React 渲染终端 — 不是"使用 Ink"，而是自定义终端渲染引擎，保留 React reconciler 接口但重写整个管线

第三章 核心引擎：Query 循环

3.1 AsyncGenerator 架构

query() 函数是一个 AsyncGenerator，外层包装器只做命令生命周期通知，核心逻辑在 queryLoop() 里：

```typescript
export async function* query(
  params: QueryParams,
): AsyncGenerator<StreamEvent | Message | TombstoneMessage | ToolUseSummaryMessage, Terminal> {
  const consumedCommandUuids: string[] = []
  const terminal = yield* queryLoop(params, consumedCommandUuids)
  for (const uuid of consumedCommandUuids) {
    notifyCommandLifecycle(uuid, 'completed')
  }
  return terminal
}
```

3.2 七种 Continue 原因

每次迭代代表一次"LLM 请求 + 工具执行"。循环体是一个状态机，有 7 种 continue 原因：

| Continue 原因 | 触发条件 | 处理方式 |
|--------------|----------|----------|
| next_turn | 有工具调用需要执行 | 正常的下一轮 |
| reactive_compact_retry | prompt too long → reactive compact 成功 | 压缩后重试 |
| collapse_drain_retry | context collapse 释放了 staged 内容 | 释放后重试 |
| max_output_tokens_recovery | 输出截断（< 3 次） | 注入恢复消息继续 |
| max_output_tokens_escalate | 输出截断 + cap enabled | 从 8k 升级到 64k 重试 |
| token_budget_continuation | token 预算还够继续干 | 注入 nudge 消息继续 |
| stop_hook_blocking | stop hook 返回 blocking error | 注入错误消息重试 |

3.3 单次迭代流程

```
Plain Text
1. 状态解构
       ↓
2. 记忆预取 (fire-and-forget)
       ↓
3. 压缩管线（5 层顺序执行）
   applyToolResultBudget → snipCompact → microcompact → contextCollapse → autocompact
       ↓
4. API 调用（流式）
   callModel(streaming) → 逐事件处理
       ↓
5. 流式处理
   - assistant 消息 → yield + push
   - tool_use blocks → StreamingToolExecutor.addTool()
   - 完成的工具结果 → yield + push
   - 可恢复错误 → withhold（不 yield）
       ↓
6. 错误恢复
   - prompt too long → collapse drain → reactive compact → surface error
   - max output tokens → escalate 64k → recovery message (3次) → surface error
   - fallback model → switch + retry
       ↓
7. 工具执行
   streamingToolExecutor.getRemainingResults() 或 runTools()
       ↓
8. 后处理
   - 附件注入（记忆、文件变更、队列命令）
   - 工具摘要生成（Haiku 异步）
   - 最大轮次检查
       ↓
9. 构建下一轮 State → continue
```

3.4 State 不可变更新

```typescript
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking: AutoCompactTrackingState | undefined
  maxOutputTokensRecoveryCount: number
  hasAttemptedReactiveCompact: boolean
  maxOutputTokensOverride: number | undefined
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined
}
```

每次 continue 都构建新的 State 对象，避免副作用。

3.5 Withhold 机制

可恢复的错误（prompt too long、max output tokens、media size error）不会立即 yield 给调用者：

TypeScriptlet withheld = falseif (contextCollapse?.isWithheldPromptTooLong(...)) withheld = trueif (reactiveCompact?.isWithheldPromptTooLong(...)) withheld = trueif (reactiveCompact?.isWithheldMediaSizeError(...)) withheld = trueif (isWithheldMaxOutputTokens(...)) withheld = trueif (!withheld) yield yieldMessage

设计理由：SDK 消费者（如 cowork/desktop）看到 error 就终止 session。但 recovery 循环可能还能修复。withhold 给 recovery 一个机会。

3.6 StreamingToolExecutor

在模型流式输出时就开始执行工具，不等流结束：

TypeScriptclass StreamingToolExecutor {  addTool(block, assistantMessage)     // 模型输出 tool_use 时立即加入  getCompletedResults()                // 消费已完成的结果（流式输出期间）  getRemainingResults()                // 流结束后消费剩余结果  discard()                            // 流式回退时丢弃所有待执行工具}

并发控制：并发安全工具最多 10 个并行（CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY=10），非并发工具串行执行。

3.7 Memory Prefetch

TypeScript// 每次迭代开始时 fire-and-forgetusing pendingMemoryPrefetch = startRelevantMemoryPrefetch(  state.messages, toolUseContext)// 在工具执行后、下一轮开始前消费if (pendingMemoryPrefetch.settledAt !== null) {  const memoryAttachments = await pendingMemoryPrefetch.promise}

利用模型流式输出的时间窗口做预加载，不额外增加延迟。使用 TypeScript 的 using 声明自动管理资源生命周期。

第四章 Agent 系统

4.1 总体架构

Agent 系统总代码量约 6072 行，分布在 14 个文件中。核心文件包括 AgentTool.tsx（1397 行，工具定义）、runAgent.ts（973 行，执行引擎）、UI.tsx（871 行，终端渲染）、loadAgentsDir.ts（755 行，Agent 定义加载）。

4.2 三种子 Agent 运行模式

4.2.1 Fork 模式（继承上下文）

Fork 模式是 Claude Code 最核心的创新之一。子 agent 继承父 agent 的完整对话上下文和 system prompt，通过字节级相同的 API 请求前缀实现 prompt cache 命中。

TypeScript// forkSubagent.ts 核心逻辑export function buildForkedMessages(  directive: string,  assistantMessage: AssistantMessage,): MessageType[] {  // 克隆 assistant message（所有 content blocks）  const fullAssistantMessage: AssistantMessage = {    ...assistantMessage,    uuid: randomUUID(),    message: {      ...assistantMessage.message,      content: [...assistantMessage.message.content],    },  }  // 收集所有 tool_use blocks  const toolUseBlocks = assistantMessage.message.content.filter(    (block): block is BetaToolUseBlock => block.type === 'tool_use',  )  // 用相同的占位符文本构建 tool_result blocks  const toolResultBlocks = toolUseBlocks.map(block => ({    type: 'tool_result' as const,    tool_use_id: block.id,    content: [{ type: 'text' as const, text: FORK_PLACEHOLDER_RESULT }],  }))  // 构建单个 user message：所有 placeholder tool_results + 每个子 agent 的指令  const toolResultMessage = createUserMessage({    content: [      ...toolResultBlocks,      { type: 'text' as const, text: buildChildMessage(directive) },    ],  })  return [fullAssistantMessage, toolResultMessage]}

关键设计：

所有 fork 子 agent 的 tool_result 占位符文本完全相同："Fork started — processing in background"

只有每条指令的最后一个 text block 不同，最大化 cache 命中率

子 agent 不重新构建 system prompt，直接用父 agent 的 renderedSystemPrompt（字节级精确）

成本优势：派生 5 个子 agent 并行工作，消耗的 token 成本接近于 1 个 agent 顺序工作，因为 5 个副本都命中了同一份 prompt cache。

4.2.2 Teammate 模式

在独立的终端窗格中运行，通过文件通信。适合跨任务协作。

4.2.3 Worktree 模式

每个 agent 拥有独立的 git worktree，互不干扰。适合并行开发不同功能。

4.3 runAgent 执行流程

TypeScript// 初始化阶段（11 步）1. 解析 agent 模型（getAgentModel）2. 创建 agent ID（createAgentId）3. 处理上下文分叉（forkContextMessages vs promptMessages）4. 克隆文件状态缓存（fork 时共享，否则独立）5. 获取用户/系统上下文（并行 Promise.all）6. 读取 CLAUDE.md 时的优化：   - Explore/Plan agent 不加载 claudeMd（节省 ~5-15 Gtok/周）   - Explore/Plan agent 不加载 gitStatus（节省 ~1-3 Gtok/周）7. 权限模式覆盖（agent 定义的 permissionMode）8. 工具解析（resolveAgentTools 或 useExactTools）9. 构建 system prompt10. 初始化 agent 专属 MCP 服务器11. 预加载 agent frontmatter 中声明的 skills

4.4 清理机制

finally 块做了 10+ 项清理，防止内存泄漏和僵尸进程：

TypeScriptfinally {  // 1. 清理 agent 专属 MCP 服务器  await mcpCleanup()  // 2. 清理 session hooks  clearSessionHooks(rootSetAppState, agentId)  // 3. 清理 prompt cache 追踪状态  cleanupAgentTracking(agentId)  // 4. 释放文件状态缓存内存  agentToolUseContext.readFileState.clear()  // 5. 释放 fork 上下文消息  initialMessages.length = 0  // 6. 注销 perfetto 追踪  unregisterPerfettoAgent(agentId)  // 7. 清理 transcript 子目录映射  clearAgentTranscriptSubdir(agentId)  // 8. 清理 todos 条目（防止内存泄漏）  // 9. 杀死 agent 产生的后台 bash 任务  killShellTasksForAgent(agentId, ...)  // 10. 杀死 agent 产生的 monitor MCP 任务}

4.5 子 Agent 指令模板

Fork 子 agent 的指令非常精炼（10 条规则），强调"直接干活不要废话"：

Plain Text1. 你是 forked worker process，不是主 agent2. 不要对话、不要问问题3. 直接用工具执行，不要在工具调用间输出文字4. 修改文件后先 commit，报告里包含 commit hash5. 回复必须以 "Scope:" 开头6. 报告不超过 500 字

第五章 Coordinator 多 Agent 编排

5.1 核心发现

整个 coordinator 模块只有一个文件 370 行代码，没有状态机、没有 DAG、没有 workflow engine。编排逻辑靠约 300 行 system prompt 驱动。

5.2 工作流

阶段

谁做

目的

Research

Workers（并行）

调研代码库、找文件、理解问题

Synthesis

协调者

读 findings、理解问题、写实现 spec

Implementation

Workers

按 spec 做修改、commit

Verification

Workers

测试修改是否有效

5.3 Continue vs Spawn 决策矩阵

场景

机制

原因

研究探索的文件正好要编辑

Continue

Worker 已有文件上下文 + 现在有清晰计划

研究广泛但实现窄

Spawn fresh

避免探索噪音，聚焦上下文更干净

纠正失败或扩展最近工作

Continue

Worker 有错误上下文

验证另一个 worker 写的代码

Spawn fresh

验证者应该用新鲜视角

完全不同的任务

Spawn fresh

没有有用的上下文复用

5.4 Coordinator 的 system prompt 核心段落

TypeScriptexport function getCoordinatorSystemPrompt(): string {  return `You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers.## 1. Your RoleYou are a **coordinator**. Your job is to:- Help the user achieve their goal- Direct workers to research, implement and verify code changes- Synthesize results and communicate with the user- Answer questions directly when possible — don't delegate work that you can handle without tools## 4. Task Workflow| Phase | Who | Purpose ||-------|-----|---------|| Research | Workers (parallel) | Investigate codebase, find files, understand problem || Synthesis | **You** (coordinator) | Read findings, understand the problem, craft implementation specs || Implementation | Workers | Make targeted changes per spec, commit || Verification | Workers | Test changes work |**Parallelism is your superpower. Workers are async. Launch independent workers concurrently whenever possible.**`}

第六章 工具系统

6.1 Tool 接口定义

每个工具是一个实现了 Tool 接口的对象，核心字段约 35+ 方法：

TypeScriptexport type Tool<Input, Output> = {  name: string  aliases?: string[]  call(args, context, canUseTool, parentMessage): Promise<ToolResult<Output>>  description(input, options): Promise<string>  inputSchema: z.ZodType<Input>  isConcurrencySafe(input): boolean  isEnabled(): boolean  isReadOnly(input): boolean  isDestructive?(input): boolean  prompt(options): Promise<string>  // ... 30+ more methods}

6.2 buildTool 工厂函数

TypeScriptconst TOOL_DEFAULTS = {  isEnabled: () => true,  isConcurrencySafe: () => false,    // 默认不并发安全  isReadOnly: () => false,           // 默认假设会写  isDestructive: () => false,  checkPermissions: (input) => Promise.resolve({ behavior: 'allow' }),  toAutoClassifierInput: () => '',   // 跳过分类器  userFacingName: () => '',}export function buildTool<D>(def: D): BuiltTool<D> {  return { ...TOOL_DEFAULTS, userFacingName: () => def.name, ...def }}

关键设计：buildTool 填充所有可选方法的安全默认值。工具定义者只需提供核心逻辑，安全声明可选但默认 fail-closed。

6.3 60+ 工具清单

类别

工具

文件操作

Read, Edit, Write, Glob, Grep, NotebookEdit

执行

Bash, PowerShell

网络

WebFetch, WebSearch

Agent

AgentTool, SendMessage, TaskCreate/Get/List/Stop/Update/Output

团队

TeamCreate, TeamDelete

MCP

MCPTool, McpAuthTool, ListMcpResources, ReadMcpResource

元工具

ToolSearch, EnterPlanMode, ExitPlanMode, Skill

其他

TodoWrite, Sleep, Config, Brief, SyntheticOutput, REPL, LSP

6.4 工具延迟加载

不常用的工具设置了 shouldDefer: true，初始 prompt 中不放完整 schema。模型通过 ToolSearch 工具按需搜索和加载，减少初始 prompt 长度，保护 prompt cache。

第七章 安全系统

7.1 BashTool 23 项安全检查

BashTool 是 Claude Code 中最危险的工具，因此安全检查也是最密集的。bashCommandIsSafe 函数串联了 23 项安全检查：

早期检查（可短路返回）

Plain Text1. validateEmpty           — 空命令直接放行2. validateIncompleteCommands — 检测不完整命令片段3. validateSafeCommandSubstitution — 放行安全的 heredoc 替换4. validateGitCommit       — 放行简单的 git commit -m "msg"

主检查链

Plain Text5.  validateJqCommand              — jq 的 system() 和危险 flag6.  validateObfuscatedFlags        — ANSI-C 引号、locale 引号、空引号绕过7.  validateShellMetacharacters    — 参数中的 ; | &8.  validateDangerousVariables     — 重定向/管道中的 $VAR9.  validateCommentQuoteDesync     — # 注释中的引号导致引号追踪器错位10. validateQuotedNewline          — 引号内换行 + 下一行以 # 开头11. validateCarriageReturn         — \r 导致 shell-quote/bash 分词差异12. validateNewlines               — 换行分隔多命令13. validateIFSInjection           — IFS 变量绕过正则验证14. validateProcEnvironAccess      — /proc/*/environ 泄露环境变量15. validateDangerousPatterns      — 反引号、<equation>()、</equation>{}、process substitution16. validateRedirections           — < > 重定向17. validateBackslashEscapedWhitespace — echo\ test 变成一个 token18. validateBackslashEscapedOperators  — \; 隐藏命令结构19. validateUnicodeWhitespace      — Unicode 空格导致分词差异20. validateMidWordHash            — 词中 # 在 shell-quote vs bash 解析不同21. validateBraceExpansion         — {a,b} 花括号扩展绕过权限检查22. validateZshDangerousCommands   — zmodload/emulate/fc -e/zpty/ztcp23. validateMalformedTokenInjection — 不完整 token + 命令分隔符

7.2 攻击向量与防御

混淆 Flag 攻击

Bash# 攻击方式""-exec          # 空引号 + flag$'-exec'         # ANSI-C 引号"""-"exec        # 多层空引号 + 引号内 flag""""-exec        # 3+ 连续引号

防御：5 项子检查覆盖 ANSI-C 引号、locale 引号、空引号对、3+ 连续引号。

注释引号错位攻击

Bashecho "safe" # ' " <<'MARKER'rm -rf /MARKER

bash：# 开始注释，rm -rf / 执行

引号追踪器：' 在注释中打开了单引号，吞掉了换行和 rm -rf /

花括号扩展攻击

Bashgit diff {@'{'0},--output=/tmp/pwned}

引号追踪器：'{' 被当成内容 → 去掉后只剩 1 个 { 2 个 }

bash：'{' 是字面量 → 第一个 } 没有逗号 → 跳过 → 找到逗号 → 扩展

Heredoc 安全验证

isSafeHeredoc 函数严格验证 6 项：

定界符必须是引号包裹或转义的

闭合定界符必须在独立行

必须有前缀命令（不能在命令名位置）

剩余文本只允许安全字符

剩余文本必须通过所有安全检查（递归）

拒绝嵌套匹配

Backslash Escaped Operators

Bashcat safe.txt \; echo ~/.ssh/id_rsa

bash：cat 读取 safe.txt 和 ; 和 echo 和 ~/.ssh/id_rsa（都是文件参数）

splitCommand 规范化后：cat safe.txt ; echo ~/.ssh/id_rsa → 两个命令

路径检查只看到 ./safe.txt → 放行 → id_rsa 泄露

7.3 权限四层防御

Plain Text第一层：工具级过滤（filterToolsByDenyRules）  在工具列表发送给模型之前，根据 alwaysDenyRules 预过滤第二层：运行时检查（hasPermissionsToUseTool）  工具调用时触发 useCanUseTool hook第三层：Bash 分类器（bashClassifier.ts）  使用 AI 判断命令是否危险，结果缓存第四层：Bypass 模式  --dangerously-skip-permissions 跳过所有检查，但有 killswitch

7.4 Speculative Classifier

在模型流式输出时就预先启动 Bash 分类器。用户真正输入命令时，分类器可能已经完成：

TypeScript// 在模型流式输出时const speculativePromise = peekSpeculativeClassifierCheck(command)// 用户确认时const raceResult = await Promise.race([  speculativePromise.then(result => ({ type: 'result', result })),  new Promise(resolve => setTimeout(resolve, 2000, { type: 'timeout' })),])if (raceResult.type === 'result' && raceResult.result.matches &&     raceResult.result.confidence === 'high') {  // 高置信度 → 跳过对话框直接放行}

第八章 上下文压缩系统

8.1 五层压缩架构

Plain TextLayer 1: Tool Result Budget    ← 每次查询前，截断工具结果Layer 2: Microcompact          ← 轻量压缩，不调用 LLMLayer 3: Snip Compact          ← 移除中间消息，保留首尾Layer 4: Context Collapse      ← 对已读文件投影压缩Layer 5: Auto Compact          ← 调用 LLM 压缩（最后手段）

8.2 Tool Result Budget

每次查询前，对工具结果进行内容替换/截断，防止单个工具输出占据过多上下文：

TypeScript// 对超过预算的工具结果进行替换// 用 "[Old tool result content cleared]" 替换旧内容// 保留元数据（文件路径、行号等）

8.3 Microcompact

不调用 LLM，直接对特定消息模式进行压缩：

TypeScriptconst COMPACTABLE_TOOLS = new Set([  'FileRead', 'Bash', 'Grep', 'Glob',  'WebSearch', 'WebFetch', 'FileEdit', 'FileWrite'])

压缩策略：重复的文件读取只保留最后一次，旧的工具结果用 stub 替换，超过 2000 token 的图片内容压缩。

8.4 Auto Compact

当 token 数接近上下文窗口限制时，触发 LLM 压缩：

TypeScript// 上下文窗口 - 13,000 token 缓冲AUTOCOMPACT_BUFFER_TOKENS = 13_000// 示例：200K 上下文窗口// 触发点 = 200K - 20K(预留给摘要) - 13K(缓冲) = 167K tokens

Circuit Breaker（熔断机制）：

TypeScript// 连续失败 3 次后停止尝试// 全球每天约 1,279 个会话有 50+ 次连续失败// 浪费约 250K API 调用/天MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

8.5 Post-compact 恢复

压缩后恢复最近读过的 5 个文件（各限 5000 token），加上 Skill 重注入（独立 25000 token 预算）。所以压缩完了模型不会"忘了之前在干嘛"。

8.6 压缩决策流程

TypeScript// queryLoop 每次迭代开始：queryLoop 迭代开始  → applyToolResultBudget()     // Layer 1: 工具结果截断  → snipCompactIfNeeded()       // Layer 3: 剪切压缩  → microcompact()              // Layer 2: 微压缩  → applyCollapsesIfNeeded()    // Layer 4: 折叠  → autocompact()               // Layer 5: 自动压缩（最后手段）

第九章 Prompt Cache 优化策略

Claude Code 的几乎所有架构决策都在围绕"减少 cache bust"展开。源码显示 Anthropic 对 prompt cache 的优化程度远超预期。

9.1 系统提示词分段缓存

系统提示词被分成静态和动态两段，用边界标记分隔。静态部分可以跨组织全局缓存，动态部分包括 memory、env_info、language、output_style、mcp_instructions 等 session-specific 内容。

9.2 Beta Header Sticky-on Latch

TypeScript// 核心设计：一旦触发就保持不变，防止 header 翻转导致 cache bustif (fastModeHeaderLatched && !betas.includes(FAST_MODE_BETA_HEADER)) {  betas.push(FAST_MODE_BETA_HEADER)  // 永远保持}

Beta header 一旦触发就保持不变。例如 fast mode 的 header，第一次触发后就永久保持，防止在 fast mode 开启/关闭之间翻转导致 cache 失效。

9.3 工具 Schema 延迟加载

不常用的工具设置了 shouldDefer: true，初始 prompt 中不放完整 schema。模型通过 ToolSearch 工具按需获取。这减少了初始 prompt 长度，保护 prompt cache。

9.4 Agent Summary 工具数组不清理

TypeScript// Agent Summary 生成进度摘要时，工具全部 deny 但不清空数组// 因为清空会改变 tool schema 字段从而 bust cache

9.5 Fork 子 Agent 共享 Cache

compact/记忆提取/SessionMemory/AgentSummary/推测执行全部通过 fork 主对话共享 prompt cache。这是降低成本的关键设计。

9.6 缓存成本分析

源码注释显示了一些数据：

Explore/Plan agent 不加载 claudeMd → 节省 ~5-15 Gtok/周

Explore/Plan agent 不加载 gitStatus → 节省 ~1-3 Gtok/周

这些优化在全球 34M+ Explore spawns 上累积节省的 token 量巨大

第十章 记忆系统

10.1 四分类法

Claude Code 的记忆不是一锅粥，而是严格的四分类：

类型

用途

何时保存

作用域

user

用户角色、偏好、知识水平

了解用户身份/习惯时

always private

feedback

用户纠正/确认的行为指导

用户说"不要这样"或"很好继续"时

默认 private

project

进行中的工作、目标、bug

了解谁在做什么/为什么/什么时候

强烈倾向 team

reference

外部系统指针

了解外部资源位置时

usually team

10.2 什么不该保存

Markdown- 代码模式、架构、文件路径 → 可以从当前项目推导- Git 历史 → git log 是权威来源- 调试方案 → 修复已经在代码里- CLAUDE.md 已有的内容 → 不重复- 临时任务细节 → 会话级上下文

10.3 记忆文件格式

Markdown---name: 记忆名称description: 一行描述type: user | feedback | project | reference---记忆内容。对于 feedback/project 类型，结构为：规则/事实，然后 **Why:** 和 **How to apply:** 行。

10.4 AutoDream 后台记忆整合

AutoDream 是 Claude Code 的后台记忆整合系统，在用户空闲时自动运行：

三道门控：

时间门控：距上次整合 ≥ 24 小时

会话门控：自上次整合以来积累了 ≥ 5 个会话

锁门控：没有其他进程正在整合

四阶段 Prompt：

Orient — ls 内存目录，了解现有结构

Gather — 收集新信号（日志、已漂移的记忆、transcript 搜索）

Consolidate — 合并新信号到现有主题文件

Prune — 修剪索引，保持入口文件 < 25KB

执行方式：以 fork 子 agent 方式运行，只读权限（Bash 只允许 ls/find/grep/cat 等只读命令）。

10.5 记忆召回时的信任机制

Plain Text记忆中提到具体函数/文件/flag → 这是"写入时存在"的声明，可能已被重命名/删除推荐前要验证：- 记忆提到文件路径 → 检查文件是否存在- 记忆提到函数或 flag → grep 它"记忆说 X 存在" ≠ "X 现在存在"

10.6 Session Memory

Session Memory 后台周期性维护一个 markdown 会话记忆，通过 forked subagent 模式运行。三阈值触发：

token 阈值：上下文增长 ≥ 5000 token

tool calls 阈值：工具调用 ≥ 3 次

自然断点：最后 assistant turn 没有工具调用

第十一章 推测执行系统

11.1 Overlay 文件系统

在用户还没输入下一条指令时，Claude Code 会预测用户的下一步，然后在一个 overlay 文件系统上提前执行：

Plain Text用户真实工作目录: /project/推测执行 overlay: /tmp/.claude/speculation/<pid>/<id>/写操作 → 写到 overlay（copy-on-write，先复制原始文件到 overlay）读操作 → 优先读 overlay，没有则读真实文件系统

11.2 Copy-on-Write 策略

TypeScriptif (isWriteTool) {  // Copy-on-write：复制原始到 overlay 如果还没有  if (!writtenPathsRef.current.has(rel)) {    const overlayFile = join(overlayPath, rel)    await mkdir(dirname(overlayFile), { recursive: true })    try {      await copyFile(join(cwd, rel), overlayFile)    } catch {      // 原始文件可能不存在（新建文件）— 没关系    }    writtenPathsRef.current.add(rel)  }  input = { ...input, [pathKey]: join(overlayPath, rel) }}

11.3 边界条件

边界类型

条件

处理

edit

需要写文件但权限不是 acceptEdits/bypassPermissions

停止，等待用户确认

bash

Bash 命令包含 cd 或写操作

停止

denied_tool

工具被拒绝

停止

complete

模型自然结束（无工具调用）

完成

11.4 资源限制

TypeScriptconst MAX_SPECULATION_TURNS = 20    // 最多 20 轮const MAX_SPECULATION_MESSAGES = 100 // 最多 100 条消息

第十二章 API 调用与重试机制

12.1 流式 API 调用

queryModelWithStreaming 是核心 API 调用函数，逐事件处理 Anthropic 的流式响应：

content_block_start → 初始化内容块

content_block_delta → 累积文本/工具输入/思考/签名

content_block_stop → 完成内容块，yield assistant 消息

message_delta → 更新 usage 和 stop reason

12.2 Thinking 配置

两种模式：

Adaptive thinking（模型自动决定思考深度）：thinking = { type: 'adaptive' }

Budget thinking（固定 token 预算）：thinking = { budget_tokens: thinkingBudget, type: 'enabled' }

12.3 错误分类与重试

错误类型

处理方式

529（过载）

前台重试（最多 3 次），后台直接丢弃

429（限流）

指数退避重试

401（认证）

刷新 OAuth token 后重试

ECONNRESET/EPIPE

禁用 keep-alive，重新连接

prompt too long

调整 max_tokens 后重试

max output tokens

升级到 64k 重试

12.4 前台 vs 后台 529 处理

TypeScriptconst FOREGROUND_529_RETRY_SOURCES = new Set([  'repl_main_thread', 'sdk', 'agent:custom', 'compact', ...])// 前台（用户等待）→ 重试// 后台（摘要、分类等）→ 直接丢弃// 理由：容量级联时每次重试是 3-10x 网关放大

12.5 Fast Mode 冷却

短 retry-after → 等待后重试（保持 prompt cache）。长 retry-after → 进入冷却（切换到标准速度，最小 5 分钟）。

12.6 指数退避

TypeScriptconst BASE_DELAY_MS = 500// delay = min(500 * 2^(attempt-1), 32000) + random(0..25%)

第十三章 权限决策系统

13.1 useCanUseTool 决策流程

Plain Text1. hasPermissionsToUseTool() → 规则匹配（allow/deny/ask）2. if allow → 直接放行3. if deny → 拒绝 + 记录 auto-mode denial4. if ask → 三路 race：   a. handleCoordinatorPermission() → coordinator 模式自动检查   b. handleSwarmWorkerPermission() → swarm worker 转发到 leader   c. handleInteractivePermission() → 弹出权限对话框5. Bash 分类器（speculative）→ 2 秒 race，高置信度直接放行

13.2 PermissionMode 枚举

Plain Textdefault         — 每次都询问acceptEdits     — 自动批准文件编辑bypassPermissions — 完全跳过（需手动确认）dontAsk         — 不询问plan            — 规划模式auto            — ML 分类器自动决定bubble          — 弹到父终端

13.3 Auto Mode 分类器

使用 AI 分类器判断命令是否危险。两阶段：

Stage 1：fast XML 判断（快速）

Stage 2：thinking 模式（慢速，只在 Stage 1 不确定时使用）

分类器的遥测数据包括：input tokens、output tokens、cache read/creation tokens、duration ms、cost USD。这些数据用于分析分类器的开销。

第十四章 状态管理与启动流程

14.1 极简 Store（35 行）

TypeScriptexport function createStore<T>(initialState: T): Store<T> {  let state = initialState  const listeners = new Set<Listener>()  return {    getState: () => state,    setState: (updater) => {      const prev = state      const next = updater(prev)      if (Object.is(next, prev)) return  // 浅比较，相同不通知      state = next      for (const listener of listeners) listener()    },    subscribe: (listener) => { listeners.add(listener); return () => listeners.delete(listener) }  }}

AppState 是一个约 450 行的巨型类型，用 DeepImmutable 包裹，涵盖权限规则、后台任务、MCP 连接、插件状态、推测执行、团队上下文、消息收件箱等。子 agent 的 setAppState 可设为 no-op 防污染，但 setAppStateForTasks 始终连接根 store。

14.2 启动流程（setup.ts, 477 行）

Plain Text1. Node.js 版本检查（>= 18）2. UDS 消息服务器启动（ant-only）3. Teammate 快照4. 终端备份恢复（iTerm2/Terminal.app）5. setCwd()6. Hooks 配置快照7. FileChanged watcher 初始化8. Worktree 创建（如果启用）9. 后台任务注册：   - initSessionMemory()   - initContextCollapse()   - lockCurrentVersion()10. 预取：    - getCommands()（技能/插件/命令）    - loadPluginHooks()    - commit attribution hooks    - team memory watcher11. Analytics sink 初始化12. tengu_started beacon（最早的"进程启动"信号）13. API key helper 预取14. Release notes + recent activity15. Bypass permissions 安全检查（Docker + 无网络）16. 上次会话 tengu_exit 事件日志

14.3 并行预取优化

main.tsx 文件开头的侧效应在模块加载阶段就启动了多个并行任务：

TypeScript// 在 ~135ms 的模块导入时间内并行执行startMdmRawRead();        // MDM 管理配置读取startKeychainPrefetch();   // macOS Keychain 预取（OAuth + API Key）

这些操作避免了串行等待，是"启动时预取"模式的典型应用。

第十五章 MCP 集成

15.1 传输协议

Claude Code 的 MCP 客户端支持 6 种传输协议：

类型

实现

用途

stdio

StdioClientTransport

本地进程通信

sse

SSEClientTransport

服务器推送事件

http

StreamableHTTPClientTransport

HTTP 流式

ws

WebSocketTransport

WebSocket

ws-ide

WebSocketTransport（IDE 专用）

VS Code 集成

sdk

InProcessTransport

进程内通信

15.2 连接管理

TypeScript// 批量连接：本地 3 个并发，远程 20 个并发export function getMcpServerConnectionBatchSize(): number {  return parseInt(process.env.MCP_SERVER_CONNECTION_BATCH_SIZE || '', 10) || 3}// 清理策略// 1. SIGTERM（优雅关闭）// 2. 等 400ms// 3. SIGKILL（强制杀死）// 4. 500ms 总超时

15.3 工具桥接

MCP 工具通过 MCPTool 自动转换为 Claude Code 的 Tool 接口：

TypeScript// MCP 工具命名规则：mcp__<serverName>__<toolName>buildMcpToolName(serverName, toolName)// 工具描述上限：2048 字符const MAX_MCP_DESCRIPTION_LENGTH = 2048// 工具超时：默认 ~27.8 小时const DEFAULT_MCP_TOOL_TIMEOUT_MS = 100_000_000

15.4 配置来源（5 层优先级）

Plain Text1. project settings (.claude/settings.json)2. user settings (~/.claude/settings.json)3. enterprise managed (MDM)4. plugin-provided5. CLI arguments

第十六章 Bridge 远程会话

16.1 两代架构

版本

方式

用途

v1

Environments API poll/dispatch

经典桥接

v2

直连 session-ingress

简化架构

16.2 核心功能

Session 管理：创建、心跳、重连、清理

JWT 自动刷新：5 分钟前主动刷新

Trusted Device Token：可信设备认证

Capacity Wake：容量唤醒

Worker 注册：CCR worker 管理

16.3 心跳机制

TypeScriptasync function heartbeatActiveWorkItems() {  for (const [sessionId] of activeSessions) {    await api.heartbeatWork(environmentId, workId, ingressToken)  }  // JWT 过期 → 调用 bridge/reconnect 触发重新分发  // 401/403 → 认证失败，重排队  // 404/410 → 环境过期，不再重试}

第十七章 Buddy 宠物系统

17.1 设计

18 种物种：duck, goose, blob, cat, dragon, octopus, owl, penguin, turtle, snail, ghost, axolotl, capybara, cactus, robot, rabbit, mushroom, chonk

6 种眼睛：·, ✦, ×, ◉, @, °

8 种帽子：none, crown, tophat, propeller, halo, wizard, beanie, tinyduck

5 种稀有度：common(60%), uncommon(25%), rare(10%), epic(4%), legendary(1%)

5 种属性：DEBUGGING, PATIENCE, CHAOS, WISDOM, SNARK

17.2 生成机制

基于 userId hash 的确定性生成，使用 Mulberry32 伪随机。稀有度加权随机，属性值 = 稀有度下限 + rng * (100 - 下限)。

17.3 Anti-Leak 策略

物种名用 String.fromCharCode 编码——其中一个物种名和内部模型代号碰撞，构建流程会 grep 构建产物检查代号泄露，所以用编码绕过检测。

17.4 持久化

只存储 soul（name + personality）和 hatchedAt。bones（species/eye/hat/rarity/stats）从 hash(userId) 再生，防止用户编辑存档刷稀有度。

第十八章 Ink 终端渲染引擎

18.1 架构

Claude Code 深度 fork 了 Ink（React 终端 UI 库），重写了整个渲染管线：

Plain TextReact 组件树 → Reconciler → 自定义 DOM → Yoga 布局 → 字符级 Screen 缓冲区 → Diff → ANSI 写入

18.2 字符串 Interning 系统

TypeScriptexport class CharPool {  private strings: string[] = [' ', '']  private stringMap = new Map<string, number>()  private ascii: Int32Array  // charCode → index, -1=未 intern  intern(char: string): number {    // ASCII 快速路径：直接数组查找，不走 Map    if (char.length === 1) {      const code = char.charCodeAt(0)      if (code < 128) {        const cached = this.ascii[code]        if (cached !== -1) return cached        // 首次遇到，intern      }    }  }}

目的：diff 时用整数比较代替字符串比较，大幅减少 CPU 开销。

18.3 StylePool

TypeScriptexport class StylePool {  intern(styles: AnsiCode[]): number {    // Bit 0 编码：style 是否对空格字符可见（背景、反转、下划线等）    // 前景色-only → 偶数 ID；可见于空格 → 奇数 ID    // 渲染器可以跳过不可见空格（单次位掩码检查）  }  transition(fromId: number, toId: number): string {    // 预序列化的 ANSI 转换字符串    // 同一对 (fromId, toId) 只计算一次，之后零分配  }}

18.4 关键优化

双缓冲帧系统：前后两个缓冲区交替渲染，目标 60fps（16ms/帧）

DECSTBM 硬件滚动：当只是滚动内容时，不重绘整个屏幕，用一条终端指令替代 O(rows×cols) 的重写

Diff 优化：逐 cell 比较，用整数比较（charId, styleId）代替字符串比较

空格跳过：StylePool 的 bit 0 编码，不可见空格直接跳过渲染

第十九章 UI 组件系统

19.1 组件分类（144 个文件）

核心布局：App.tsx、FullscreenLayout.tsx、VirtualMessageList.tsx（1081 行）、TextInput.tsx

消息渲染：34 个（messages/ 目录），每种消息类型独立组件

权限对话框：PermissionPrompt.tsx、PermissionExplanation.tsx 等

Design System：Dialog、Pane、Tabs、ProgressBar、ThemedBox/ThemedText

子目录：agents/、diff/、mcp/、memory/、skills/、tasks/、teams/

19.2 VirtualMessageList

只渲染可见区域的消息（虚拟滚动）

支持 scrollToIndex、search、jumpToMatch

高度缓存（按列宽失效）

search-text 缓存（WeakMap）

19.3 React Compiler

所有组件经过 React Compiler 编译，自动做细粒度 memoization。代码中的 _c() 调用是编译器生成的缓存桩。

第二十章 测试与验证

20.1 编译验证

Bash$ bun run ./src/bootstrap-entry.ts --version999.0.0-restored (Claude Code)$ bun run ./src/bootstrap-entry.ts --helpUsage: claude [options] [prompt]

20.2 缺失模块检查

dev-entry.ts 会扫描所有文件的 relative imports，如果有缺失会报 missing_relative_imports=N。实际测试结果：0 个缺失。

20.3 API 兼容性验证

使用智谱 Coding Plan API Key 验证 Anthropic SDK 兼容性：

TypeScriptconst client = new Anthropic({  apiKey: process.env.ZHIPU_AUTH_TOKEN,  baseURL: 'https://open.bigmodel.cn/api/anthropic',  defaultHeaders: { 'Authorization': `Bearer ${process.env.ZHIPU_AUTH_TOKEN}` },})// 非流式调用const msg = await client.messages.create({  model: 'glm-5', max_tokens: 30,  messages: [{ role: 'user', content: 'Say hello in one word.' }],})// ✅ SUCCESS: Hello.// 流式调用const stream = client.messages.stream({  model: 'glm-5', max_tokens: 100,  messages: [{ role: 'user', content: 'Write a haiku about coding.' }],})// ✅ 输出: Fingers on the keys,//         Logic flows in silent lines,//         Code brings dreams to life.

20.4 REPL 启动限制

完整 REPL 启动后卡住（8 秒无输出退出）。可能原因：

需要 TTY（Ink 终端渲染需要真实的终端）

UDS 消息服务器启动阻塞

macOS Keychain 预取阻塞

缺少 API Key 环境变量导致初始化卡住

20.5 第三方 Provider 支持

在 client.ts 中添加了第三方 Provider 支持（OpenRouter / 智谱 GLM Coding Plan）：

TypeScriptconst zhipuKey = process.env.ZHIPU_AUTH_TOKENconst openrouterKey = process.env.OPENROUTER_API_KEY// 智谱优先于 OpenRouter// 环境变量自动切换，无需改代码

第二十一章 框架对比分析

21.1 Claude Code vs 其他框架

维度

Claude Code

LangChain

AutoGPT

OpenClaw

Continue.dev

定位

CLI 编程助手

Agent 框架

自主 Agent

个人助手平台

IDE 插件

架构

AsyncGenerator + fork

Chain/Graph

目标驱动循环

多通道多 Agent

IDE 集成

编排

300 行 prompt 驱动

DAG executor

简单循环

Skill 系统

上下文注入

工具

60+ 内置

可扩展

可扩展

Skill 包装

LSP + 自定义

压缩

5 层渐进

无

简单截断

单层 compact

无

缓存

一等公民

无

无

无

无

安全

23 项检查

基本

基本

中等

IDE 沙箱

终端

自研渲染引擎

无

CLI

多通道

IDE 原生

21.2 Claude Code 的 5 大独特设计

AsyncGenerator 查询循环：统一的流式处理和中断语义，query/工具/hook 全部用 AsyncGenerator

工具并发声明：isConcurrencySafe() 是简单但有效的设计，只读工具可以并发执行

5 层上下文压缩：从工具结果截断到自动压缩，比其他框架的单层压缩更精细

Bash AI 分类器：使用 AI 判断命令是否危险，speculative 预执行

启动并行预取：main.tsx 在模块加载阶段就启动预取任务，减少冷启动时间

21.3 性能分析

Claude Code "又快又流畅"的原因：

启动并行化：UDS、keychain、MDM 在模块加载阶段并行执行

工具并发执行：只读工具最多 10 个并发

Prompt Caching：分段缓存 + sticky latch + fork 共享

分层压缩：5 层渐进，每层都比上一层更激进

流式渲染：StreamingToolExecutor 在模型输出时就开始执行工具

Bun 运行时：编译时 dead code elimination + 快速启动

第二十二章 总结与启示

22.1 六大核心设计哲学

能用 prompt 解决的就不用代码 — coordinator 模式用 300 行 system prompt 替代编排引擎，证明在 LLM 能力足够强的前提下，自然语言比代码更灵活、更好维护

Fail-closed 是正确默认值 — 所有工具默认不并发安全、不只读、不安全，需要显式声明。忘记标记的后果是"多问一次权限"而不是"数据损坏"

成本控制融入架构 — prompt cache 的分段缓存、工具 schema 延迟加载、fork agent 共享 cache、compact 的 circuit breaker，每个设计决策都在考虑 API 调用成本

利用时间窗口做推测执行 — 记忆预取（Memory Prefetch）利用模型推理时间窗口、推测分类器（Speculative Classifier）在流式输出时预先启动、推测执行（Speculation）在用户未输入时预执行

AsyncGenerator everywhere — query、工具执行、hook 全部用 AsyncGenerator，统一流式处理和中断语义

状态机比 if-else 链更清晰 — query loop 有 7 种 continue 原因，每种原因对应一种状态转换

22.2 对 Agent 系统开发者的启示

先想 prompt，再想代码 — 设计复杂逻辑时，先想"能不能用自然语言说清楚"

默认不安全 — 我们的工具/配置也应该默认不安全，需要显式声明

不要串行等待 — 找到可以并行的机会，利用时间窗口

用状态机 — 复杂流程用状态机，不用 if-else 嵌套

Prompt cache 是一等公民 — 设计时考虑"这个操作会 bust cache 吗"

22.3 局限性

文件过大：main.tsx 4683 行，query.ts 也是数千行，单文件职责过重

Feature Flag 复杂度：大量 feature() 调用增加了代码分支复杂度

Bun 依赖：深度绑定 Bun 特性（feature()、bundler），限制了跨运行时移植性

内部 API 泄露：通过 source map 暴露了完整的内部实现，存在安全风险

Hook 系统的脆弱性：用户定义的 shell 命令作为 hook，缺乏沙箱隔离

上下文压缩的权衡：多层压缩策略虽然节省 token，但可能丢失重要上下文

22.4 架构选择建议

场景

推荐框架

快速搭建 Agent 应用

LangChain

自主任务执行

AutoGPT

个人 AI 助手平台

OpenClaw

IDE 内编程辅助

Continue.dev

高性能 CLI 工具

Claude Code 的架构思路

分析时间: 2026-04-01 ~ 2026-04-02源码版本: Claude Code v2.1.88分析范围。分析深度: 30+ 个核心模块，约 50,000 行代码参考来源: 源码直接阅读 + APPSO 报道 + 连旭分析 + ccleaks.com

