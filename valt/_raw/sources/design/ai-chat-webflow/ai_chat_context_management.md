# AI Chat 上下文管理系统设计方案

> 创建时间：2024-01-01
> 更新版本：v2.0
> 状态：**待实现**

---

## 一、需求概述

将前端界面右边的 Todo List 替换为 AI Chat 对话框，实现：
- 流式输出展示
- 思考过程展示
- 消息持久化（Markdown 文件）
- 智能上下文管理
- Mock/Real 切换

**技术栈**：
- 前端：Vue 2 + element-ui + webpack 3
- 后端：Python aiohttp + 自研 yeab 框架
- AI：MiniMax API（支持 reasoning_content 思考过程）

---

## 二、设计系统：Webflow Style

### 2.1 设计原则

| 原则 | 说明 |
|------|------|
| 白色画布 | `#ffffff` 背景，近黑文字 `#080808` |
| Webflow Blue | `#146ef5` 作为主品牌色和交互色 |
| 锐利圆角 | 4px-8px，不超过 8px |
| 5层阴影 | 级联阴影系统保留 |
| translate(6px) | 按钮悬停动效 |
| Uppercase 标签 | 12px-15px, weight 500-600 |

### 2.2 配色方案

```scss
$near-black: #080808;        // 主文字
$webflow-blue: #146ef5;      // 主品牌色
$blue-400: #3b89ff;          // 浅蓝交互
$blue-hover: #0055d4;        // 按钮悬停蓝
$gray-800: #222222;          // 次要文字
$gray-300: #ababab;          // 占位符/禁用
$border-gray: #d8d8d8;       // 边框
$white: #ffffff;
$gray-50: #f5f5f5;            // 输入框背景
```

### 2.3 5层阴影系统

```scss
$shadow-5layer: 
  0px 84px 24px rgba(0,0,0,0),
  0px 54px 22px rgba(0,0,0,0.01),
  0px 30px 18px rgba(0,0,0,0.04),
  0px 13px 13px rgba(0,0,0,0.08),
  0px 3px 7px rgba(0,0,0,0.09);
```

---

## 三、系统架构

### 3.1 目录结构

```
/mnt/d/project/linbirg/ww/ww/record/chat_sessions/
└── {session_id}/
    ├── _context.md          # 上下文管理器
    ├── 001_20240101_120000_user.md
    ├── 002_20240101_120005_assistant.md
    ├── 003_20240101_120010_reasoning.md
    └── ...
```

### 3.2 文件格式

#### 消息文件

**用户消息** (`{序号}_{时间}_{角色}.md`)：
```markdown
---
role: user
timestamp: 2024-01-01 12:00:00
session_id: abc-123-uuid
---

用户消息内容
```

**AI 回复文件**：
```markdown
---
role: assistant
timestamp: 2024-01-01 12:00:05
session_id: abc-123-uuid
model: MiniMax-M2.7
reasoning: |
  思考过程内容...
tool_calls:
  - tool: Read
    args: {file: "src/main.py"}
  - tool: Edit
    args: {old: "xxx", new: "yyy"}
---

AI 正式回复内容
```

---

## 四、上下文管理 `_context.md`

### 4.1 文件内容格式

```markdown
# 对话上下文

## 元信息
- session_id: abc-123-uuid
- 创建时间: 2024-01-01 12:00:00
- 消息总数: 25
- 最后更新: 2024-01-01 12:30:00
- LLM 模型: MiniMax-M2.7

## 关键信息

### 主题
Python 异步编程、asyncio 性能优化

### 用户信息
- 使用 Python 3.10+
- 喜欢详细的代码示例
- 使用中文交流

### 当前任务
帮助用户优化 asyncio 异步代码的性能问题

### 重要实体
- async/await
- asyncio
- 协程 (Coroutine)
- 事件循环 (Event Loop)

### 对话进度
- [x] 解释了 async/await 基本概念
- [x] 讨论了协程与生成器的区别
- [ ] 正在讨论性能优化方案
- [ ] 待完成：给出具体优化建议

## 最近对话（完整）

### 消息 15 (user)
asyncio 有哪些常见的性能陷阱？

### 消息 16 (assistant)
asyncio 的性能陷阱包括...

### 消息 17 (user)
如何避免这些陷阱？

（保留最近 10 条完整消息）

## 历史摘要

### 阶段 1 (消息 1-10)
用户开始学习 Python 异步编程，询问了基础概念。AI 解释了协程、async/await 的基本用法。

### 阶段 2 (消息 11-17)
用户深入了解协程与生成器的区别，讨论了事件循环的原理。开始涉及性能优化话题。
```

### 4.2 摘要触发机制（细粒度混合策略）

**触发条件**（满足任一即触发）：
| 条件 | 阈值 | 说明 |
|------|------|------|
| 消息数量 | 20 条 | 当消息总数达到 20 条时触发 |
| Token 数量 | 3000 tokens | 当上下文 token 数超过 3000 时触发 |
| 累计新增 Token | 2000 tokens | 距上次摘要后新增超过 2000 tokens |
| 无工具调用轮次 | 2 轮 | 连续 2 轮无 AI 工具调用（进入"总结"阶段） |

**摘要前置检查**：
- 检查距上次摘要是否小于 5 分钟（防止频繁触发）
- 检查是否有正在进行的摘要生成任务（防止并发）

### 4.3 工具调用追踪

每条 AI 消息记录工具调用情况：

```markdown
---
role: assistant
timestamp: 2024-01-01 12:00:05
session_id: abc-123-uuid
model: MiniMax-M2.7
reasoning: |
  思考过程内容...
tool_calls:
  - tool: Read
    args: {file: "src/main.py"}
    result: {lines: 50, content: "..."}
  - tool: Edit
    args: {file: "src/main.py", old: "xxx", new: "yyy"}
    result: {success: true}
has_tool_call: true
tool_call_count: 2
---

AI 正式回复内容
```

**会话统计字段**（在 _context.md 中）：
```markdown
## 会话统计
- 消息总数: 25
- 总 Token 数: 4500
- 距上次摘要: 15 分钟
- 上次摘要 Token 数: 2500
- 新增 Token 数: 2000
- 工具调用总次数: 12
- 无工具调用轮次: 0
- 最后工具调用: 消息 18
```

### 4.4 摘要生成流程

```
1. 检测触发条件（消息数量/Token/新增Token/无工具调用轮次）
2. 检查防抖（距上次 < 5 分钟则跳过）
3. 锁定会话（防止并发摘要）
4. 读取所有消息文件，统计工具调用
5. 调用 MiniMax API 生成摘要
6. 更新 _context.md
7. 解锁会话
```

### 4.5 消息加载流程

```
1. 读取 _context.md
2. 提取「关键信息」和「历史摘要」作为系统提示
3. 提取「最近 10 条完整消息」追加
4. 组装完整上下文
5. 发送给 MiniMax API
```

### 4.6 摘要生成 Prompt

```
你是一个对话摘要助手。请分析以下对话历史，提取关键信息并生成摘要。

## 对话上下文
[从 _context.md 读取的元信息]

## 历史消息
[历史消息列表，包含工具调用记录]

## 最近消息（完整）
[最近 10 条消息]

## 工具调用统计
[工具调用次数、类型分布、最近工具调用等]

## 要求
1. 提取关键实体和技术术语
2. 识别用户的需求和目标
3. 标记对话进度（用 [x]/[ ] checkbox）
4. 分析工具调用模式（是否有文件操作、搜索等）
5. 生成简洁的阶段性摘要
6. 输出纯 Markdown 格式

## 输出格式
按照 _context.md 结构输出，包含：
- 更新后的元信息
- 关键信息（主题、用户信息、当前任务、重要实体、对话进度）
- 最近 10 条完整消息
- 历史摘要（分阶段，每阶段 1-3 句话）
```

---

## 五、Mock/Real 切换机制

### 5.1 配置文件

**`yail/conf/dev.py`**：
```python
# AI Chat 配置
USE_MOCK_CHAT = True   # True=Mock, False=真实AI
OPENAI_API_KEY = 'your-api-key'
OPENAI_BASE_URL = 'https://api.minimax.chat/v1'
OPENAI_MODEL = 'MiniMax-M2.7'
OPENAI_MAX_HISTORY = 20

# 消息持久化配置
CHAT_SESSIONS_DIR = '/mnt/d/project/linbirg/ww/ww/record/chat_sessions'

# 摘要触发条件
CONTEXT_TRIGGER_COUNT = 20           # 消息数量阈值
CONTEXT_TRIGGER_TOKENS = 3000        # Token 数量阈值
CONTEXT_TRIGGER_DELTA = 2000          # 距上次摘要后新增 Token 阈值
CONTEXT_TRIGGER_NO_TOOL_ROUNDS = 2   # 连续无工具调用轮次阈值
CONTEXT_TRIGGER_DEBOUNCE = 300        # 防抖间隔（秒）
CONTEXT_KEEP_MESSAGES = 10           # 保留最近消息数量
```

### 5.2 路由分发

```python
# www/handlers/chat/chat.py

@post("/chat/send")
async def chat_send(request):
    if conf.USE_MOCK_CHAT:
        return await mock_chat_send(request)  # 转发到 Mock
    else:
        return await real_chat_send(request)   # 真实 AI
```

---

## 六、重试机制

### 6.1 消息状态

```javascript
{
  id: 123,
  role: 'user' | 'assistant',
  content: '...',
  reasoning_content: '...',
  status: 'idle' | 'sending' | 'streaming' | 'done' | 'error',
  retryCount: 0,
  createdAt: '...'
}
```

### 6.2 状态流转

```
idle → sending → streaming → done
                ↓
              error (可重试, max 3次)
```

### 6.3 重试 UI

- 失败消息显示红色边框和错误提示
- 显示「重新发送」按钮
- 最多重试 3 次

---

## 七、思考过程行为

| 场景 | 行为 |
|------|------|
| 默认状态 | 展开 |
| 流式输出过程中 | 保持展开 |
| 用户手动折叠 | 保持折叠 |
| 新消息到达 | 自动展开 |

---

## 八、会话摘要系统（对比 Claude Code 改进版）

### 8.1 与 Claude Code 的对比

| 特性 | Claude Code | 我们的设计 |
|------|-------------|-----------|
| 摘要触发 | token>10k + 新增>5k + 无工具调用 | 消息20条 或 token>3k 或 新增>2k 或 连续2轮无工具调用 |
| 工具调用追踪 | 有 | 有（完整记录 tool_calls） |
| Micro 压缩 | 有（每轮清理旧工具返回值） | 暂不做，但记录完整工具调用 |
| Session Memory | 独立文件 | 合并在 _context.md |
| 摘要方式 | 子代理（继承 prompt cache） | 直接调用 API |
| 防抖机制 | 无 | 有（5 分钟间隔） |
| 并发控制 | 无 | 摘要锁定机制 |

### 8.2 Claude Code 四层记忆参考

```
第一层：CLAUDE.md        → 手动规则，跨会话持久化
第二层：MEMORY.md        → 子代理自动维护，跨会话
第三层：Session Memory   → 当前会话摘要，新会话可读
第四层：上下文压缩       → Micro/Session/标准压缩
```

### 8.3 我们采用的设计

```
消息文件 → _context.md（混合摘要）
         ├── 元信息 + 会话统计
         ├── 关键信息（主题/用户/任务/实体/进度）
         ├── 最近 10 条完整消息
         ├── 历史摘要（分阶段）
         └── 工具调用统计
```

### 8.4 工具调用追踪优势

相比 Claude Code，我们记录更完整的工具调用信息：

```markdown
tool_calls:
  - tool: Read
    args: {file: "src/main.py"}
    result: {lines: 50, preview: "import..."}
  - tool: Edit
    args: {file: "src/main.py", old: "xxx", new: "yyy"}
    result: {success: true, lines_changed: 3}
```

**可用于**：
- 分析用户操作模式
- 优化工具调用策略
- 生成更准确的摘要
- 审计和回溯

### 8.5 改进的摘要 Prompt

```
你是一个对话摘要助手。请分析以下对话历史，提取关键信息并生成摘要。

## 输入信息
1. 元信息（session_id、创建时间、消息总数）
2. 会话统计（Token 数、工具调用次数、最近摘要时间）
3. 历史消息（包含完整工具调用记录）
4. 最近 10 条消息

## 分析要点
1. 对话主题是什么？
2. 用户的目标/任务是什么？
3. 讨论了哪些技术实体/概念？
4. 工具调用模式（Read/Edit/搜索等）
5. 对话进度（已完成/进行中/待完成）

## 输出要求
1. 关键信息：主题、用户信息、当前任务、重要实体、对话进度（checkbox）
2. 最近 10 条完整消息（保持原始内容）
3. 历史摘要（分阶段，每阶段 1-3 句话）
4. 工具调用统计（总次数、类型分布）

## 注意事项
- 对话进度用 [x]（已完成）和 [ ]（待完成）标记
- 历史摘要要连贯，衔接各阶段
- 工具调用统计反映整体操作模式
```

---

## 九、API 接口

### 9.1 发送消息

```
POST /chat/send
Content-Type: application/json

Request:
{
  "userId": 1,
  "content": "你好",
  "sessionId": "abc-123-uuid"
}

Response: SSE 流
event: chunk
data: {"reasoning_content": "...", "content": ""}

event: chunk
data: {"content": "你好呀"}

event: done
```

### 9.2 获取历史

```
POST /chat/history

Request:
{
  "userId": 1,
  "sessionId": "abc-123-uuid"
}

Response:
{
  "messages": [
    {"role": "user", "content": "你好", "createdAt": "..."},
    {"role": "assistant", "content": "你好呀", "createdAt": "..."}
  ],
  "context": {...}  // _context.md 内容
}
```

### 9.3 清空会话

```
POST /chat/clear

Request:
{
  "userId": 1,
  "sessionId": "abc-123-uuid"
}

Response:
{
  "success": true
}
```

---

## 十、文件清单

### 9.1 后端文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `conf/dev.py` | 待更新 | 添加 `USE_MOCK_CHAT`, `CHAT_SESSIONS_DIR`, `CONTEXT_TRIGGER_*` |
| `www/handlers/chat/chat.py` | 待更新 | 路由分发 + 真实 Handler + 消息保存 |
| `www/handlers/chat/mock_chat.py` | ✅ 已有 | 保持不变 |
| `www/handlers/chat/session_manager.py` | **新建** | Session 创建、上下文管理 |
| `www/handlers/chat/message_store.py` | **新建** | Markdown 文件读写 |

### 10.2 前端文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `chat.vue` | 待更新 | 重试逻辑 + 思考过程状态管理 |
| `message.vue` | ✅ 已有 | 思考过程默认展开 |
| `store/index.js` | 待更新 | 适配状态机 |

---

## 十一、实施步骤

| 顺序 | 任务 | 状态 | 文件 |
|------|------|------|------|
| 1 | 更新 conf/dev.py 配置 | ⏳ | `conf/dev.py` |
| 2 | 创建 message_store.py | ⏳ | `www/handlers/chat/message_store.py` |
| 3 | 创建 session_manager.py | ⏳ | `www/handlers/chat/session_manager.py` |
| 4 | 更新 chat.py 路由分发 | ⏳ | `www/handlers/chat/chat.py` |
| 5 | 实现真实 AI Handler | ⏳ | `www/handlers/chat/chat.py` |
| 6 | 实现上下文摘要功能 | ⏳ | `session_manager.py` |
| 7 | 更新 chat.vue 重试逻辑 | ⏳ | `frontEnd/src/components/ChatList/chat.vue` |
| 8 | 更新 store/index.js | ⏳ | `frontEnd/src/store/index.js` |
| 9 | 集成测试 | ⏳ | - |

---

## 十二、待实现功能（后续）

1. **向量数据库集成**：用于语义检索历史消息
2. **多模态支持**：支持图片、文件上传
3. **上下文压缩**：更智能的摘要算法
4. **对话导出**：导出为 PDF/HTML/Markdown
