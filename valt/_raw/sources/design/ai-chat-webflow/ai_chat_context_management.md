# AI Chat 上下文管理系统 - 最终设计方案

> 版本：v2.2
> 状态：待实现
> 创建：2024-01-01
> 更新：2026-04-09

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Chat 消息流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户输入 → L1: Tool Result Budget → L2: Microcompact      │
│                ↓                          ↓                 │
│         裁剪超长工具结果         压缩重复工具调用            │
│                ↓                          ↓                 │
│         L5: Auto Summarization ←── 触发条件检查             │
│                ↓                                           │
│         更新 _context.md                                   │
│                ↓                                           │
│         写入 messages/                                     │
│                ↓                                           │
│         写入 memories/                                     │
│                ↓                                           │
│         提取 → _global/memories/                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、目录结构

### 2.1 整体目录结构

```
chat_sessions/
├── _global/                           # 全局记忆（跨 session 共享）
│   ├── _context.md                   # 全局上下文
│   └── memories/
│       ├── user/_index.md            # 用户偏好
│       ├── feedback/_index.md         # 用户反馈
│       ├── project/_index.md          # 项目信息
│       └── reference/_index.md        # 外部引用
│
└── {session_id}/                     # 各 session 独立
    ├── _context.md                   # 会话上下文
    └── messages/
        ├── 001_user.md
        ├── 002_assistant.md
        ├── 003_user.md
        └── ...
```

### 2.2 session_id 格式

```
{date}_{time}_{userId}_{uuid前缀}
示例：20260409_143052_user123_a1b2c3d4
```

| 字段 | 说明 | 示例 |
|:---|:---|:---|
| date | 日期 | 20260409 |
| time | 时间 | 143052 |
| userId | 用户ID | user123 |
| uuid前缀 | UUID 前 8 位 | a1b2c3d4 |

### 2.3 各文件作用域说明

| 文件/目录 | 作用域 | 说明 |
|:---|:---|:---|
| `_global/_context.md` | 全局 | 全局元信息、用户偏好摘要、跨 session 统计 |
| `_global/memories/` | 全局 | 跨所有 session 共享的记忆 |
| `{session_id}/_context.md` | session | 当前会话的上下文、进度、最近消息 |
| `{session_id}/messages/` | session | 当前会话的所有消息文件 |

### 2.4 记忆存储方式

按类型合并到单一文件：

```
memories/
├── user/_index.md        # 包含所有 user 类型记忆
├── feedback/_index.md    # 包含所有 feedback 类型记忆
├── project/_index.md    # 包含所有 project 类型记忆
└── reference/_index.md  # 包含所有 reference 类型记忆
```

---

## 三、压缩系统详解

### 3.1 Layer 1: Tool Result Budget (L1)

| 配置项 | 值 | 说明 |
|:---|:---:|:---|
| `TOOL_RESULT_BUDGET_MAX_CHARS` | 2000 | 单个工具结果最大字符数 |
| `TOOL_RESULT_BUDGET_REPLACE_TEXT` | `"[工具结果已裁剪]"` | 裁剪后替换文本 |
| `TOOL_RESULT_BUDGET_MIN_PREVIEW` | 500 | 保留前 N 字符作为预览 |

**处理流程**：
```
工具执行结果
    ↓
结果字符数 > 2000?
    ├── 否 → 直接使用
    └── 是 → 保留前500字符 + "..." + "[工具结果已裁剪]"
            → 保留元数据（文件路径、行数）
```

**元数据格式**：
```json
{
  "truncated": true,
  "original_length": 15000,
  "preview": "import asyncio\nfrom typing import...",
  "metadata": {
    "file": "src/main.py",
    "lines": 500
  }
}
```

> ⚠️ **前端注明**：当前使用简单字符统计，未进行真实 token 计数。可能与 API 实际消耗有偏差。

### 3.2 Layer 2: Microcompact (L2)

| 配置项 | 值 | 说明 |
|:---|:---:|:---|
| `MICROCOMPACT_ENABLED` | `True` | 是否启用 |
| `MICROCOMPACT_TOOLS` | `{Read, Bash, Grep, Glob}` | 适用工具类型 |
| `MICROCOMPACT_STUB` | `"[早期工具调用已压缩]"` | 压缩后替换文本 |

**处理流程**：
```
检测连续同类型工具调用（同一 session 内）
    ↓
保留最后一次完整结果
    ↓
之前的替换为 stub
    ↓
记录压缩次数
```

**示例**：
```markdown
# 压缩前
[Read: file1.py] → result1 (100 chars)
[Read: file1.py] → result2 (150 chars)  ← 保留
[Read: file1.py] → result3 (200 chars)  ← 保留

# 压缩后
[Read: file1.py] → "[早期工具调用已压缩]"
[Read: file1.py] → result2
[Read: file1.py] → result3
```

### 3.3 Layer 5: Auto Summarization (L5)

**触发条件**（满足任一即触发）：

| 条件 | 阈值 | 说明 |
|:---|:---:|:---|
| 消息数量 | 20 条 | 当消息总数达到 20 条时触发 |
| Token 数量 | 8000 | 当上下文 token 数超过 8000 时触发 |
| 累计新增 Token | 3000 | 距上次摘要后新增超过 3000 tokens |
| 无工具调用轮次 | 2 轮 | 连续 2 轮无 AI 工具调用 |

**防抖**：距上次摘要 < 5 分钟则跳过

**摘要前置检查**：检查是否有正在进行的摘要生成任务（防止并发）

**摘要后保留**：最近 10 条完整消息，摘要预留 2000 token

---

## 四、记忆分类系统

### 4.1 4类记忆定义

| 类型 | 用途 | 作用域 | 保存时机 |
|:---|:---|:---|:---|
| **user** | 用户角色、偏好、知识水平 | 全局 | 了解用户身份/习惯时 |
| **feedback** | 用户纠正/确认的行为指导 | 全局 | 用户说"不要这样"或"很好继续"时 |
| **project** | 进行中的工作、目标、bug | 全局 | 了解谁在做什么/为什么/什么时候 |
| **reference** | 外部系统指针 | 全局 | 了解外部资源位置时 |

> **注意**：所有记忆存储在 `_global/memories/` 下，跨 session 共享。

### 4.2 记忆文件格式

```markdown
---
name: 记忆名称
description: 一行描述
type: user | feedback | project | reference
scope: private | team
created_at: 2024-01-01 12:00:00
updated_at: 2024-01-01 14:30:00
source_messages: [session_id:5, session_id:12, session_id:18]
---

## 内容
记忆的具体内容...

## 来源
- 会话 session_id:5: "用户自称..."
- 会话 session_id:12: "用户说..."
```

### 4.3 记忆索引格式

#### `_global/memories/user/_index.md`

```markdown
# User 记忆索引

## 记忆列表

### 用户Python水平
- 更新时间: 2024-01-01 14:30
- 来源会话: session_001, session_003
- 摘要: 3年Python经验，喜欢异步编程，用中文交流

### 用户编码偏好
- 更新时间: 2024-01-02 10:00
- 来源会话: session_002
- 摘要: 喜欢详细的代码示例

## 最近更新
- 2024-01-02 10:00: 用户编码偏好 (新建)
- 2024-01-01 14:30: 用户Python水平 (更新)
```

---

## 五、_context.md 结构

### 5.1 全局上下文 `_global/_context.md`

```markdown
# 全局上下文

## 元信息
- global_created: 2024-01-01 12:00:00
- last_updated: 2024-01-02 15:30:00
- total_sessions: 12
- active_session: session_id

## 用户概览
### 身份
- 用户ID: user123
- 使用语言: 中文
- 技术水平: Python 3年+

### 偏好
- 喜欢详细的代码示例
- 使用 asyncio 进行异步编程
- 习惯用中文交流

### 已知项目
- 项目A: Web 服务开发
- 项目B: 数据处理脚本

## 跨会话统计
- 总消息数: 256
- 总工具调用: 89
- 平均会话长度: 21 条消息

## 最近会话
- session_id: 20260409_143052_user123_a1b2c3d4
- session_id: 20260408_100521_user123_e5f6g7h8
```

### 5.2 会话上下文 `{session_id}/_context.md`

```markdown
# 会话上下文

## 元信息
- session_id: 20260409_143052_user123_a1b2c3d4
- user_id: user123
- 创建时间: 2024-04-09 14:30:52
- 最后更新: 2024-04-09 15:30:00
- 消息总数: 25
- LLM 模型: MiniMax-M2.7

## 当前会话信息
### 主题
Python 异步编程、asyncio 性能优化

### 当前任务
帮助用户优化 asyncio 异步代码的性能问题

### 对话进度
- [x] 解释了 async/await 基本概念
- [x] 讨论了协程与生成器的区别
- [ ] 正在讨论性能优化方案

## 记忆引用
- user: 用户Python水平 (_global/memories/user/_index.md#用户Python水平)
- feedback: 避免使用threading (_global/memories/feedback/_index.md#避免threading)
- project: asyncio优化 (_global/memories/project/_index.md#asyncio优化)

## 最近消息
### 消息 15 (user)
asyncio 有哪些常见的性能陷阱？

### 消息 16 (assistant)
asyncio 的性能陷阱包括...

## 历史摘要
### 阶段 1 (消息 1-10)
用户开始学习 Python 异步编程，询问了基础概念。

### 阶段 2 (消息 11-17)
深入了解协程与生成器的区别，讨论了事件循环的原理。
```

---

## 六、Prompt Cache 轻量优化

| 优化项 | 实现 | 说明 |
|:---|:---:|:---|
| 摘要结果缓存 | ✅ | `SUMMARIZE_CACHE_ENABLED = True` |
| 工具 schema 引用 | ✅ | 工具 schema 用引用而非完整内联 |
| 消息去重 | ✅ | 去除连续重复消息 |

---

## 七、实施文件清单

### 7.1 新增文件

| 文件 | 职责 | 优先级 |
|:---|:---|:---:|
| `tool_result_budget.py` | L1 工具结果裁剪 | P0 |
| `microcompact.py` | L2 重复工具压缩 | P0 |
| `memory_store.py` | 4类记忆读写（全局+会话） | P1 |
| `memory_types.py` | 记忆类型定义 | P1 |
| `global_context.py` | 全局上下文管理 | P1 |
| `prompt_cache.py` | L5 摘要缓存 | P2 |

### 7.2 修改文件

| 文件 | 修改内容 | 优先级 |
|:---|:---|:---:|
| `conf/dev.py` | 添加所有配置项 | P0 |
| `session_manager.py` | 集成 L1/L2/L5 压缩、集成全局记忆 | P0 |
| `message_store.py` | 集成 L1/L2 | P0 |
| `chat.py` | 集成记忆分类 | P1 |

### 7.3 目录结构变更

```
chat_sessions/                    # 根目录（由 chat_sessions_dir 配置）
├── _global/                      # 新增：全局级别
│   ├── _context.md
│   └── memories/
│       ├── user/_index.md
│       ├── feedback/_index.md
│       ├── project/_index.md
│       └── reference/_index.md
└── {session_id}/                 # 现有：会话级别
    ├── _context.md
    └── messages/
        └── ...
```

---

## 八、session 切换时的处理流程

```
用户切换到新 session
    ↓
加载 _global/_context.md 获取用户概览
    ↓
加载 _global/memories/{type}/_index.md 获取用户记忆
    ↓
创建新 session 目录和 _context.md
    ↓
将全局记忆引用写入新 session 的 _context.md
    ↓
新 session 可使用历史偏好和项目信息
```

---

## 九、消息加载流程（含全局记忆）

```
1. 加载 _global/_context.md → 用户概览
2. 加载 _global/memories/{type}/_index.md → 用户记忆
3. 组装 system prompt（包含全局信息）
4. 加载当前 session 的 _context.md → 会话上下文
5. 加载当前 session 的最近消息
6. 组装完整上下文 → 发送给 LLM
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|:---|:---:|:---|
| 2024-01-01 | v1.0 | 初始版本 |
| 2026-04-09 | v2.0 | 对标 Claude Code 重构压缩系统和记忆系统 |
| 2026-04-09 | v2.1 | 新增目录结构、待细化问题清单 |
| 2026-04-09 | v2.2 | 确认跨 session 共享结构、session_id 格式 |
