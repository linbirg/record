# AI Chat 上下文自动更新设计方案

> 版本：v1.0
> 状态：已完成设计
> 创建：2026-04-10

---

## 一、概述

本文档细化上下文管理系统的自动更新机制，包括：
- 会话级别 context 日常更新
- L5 触发时的深度处理
- 记忆提取与存储策略

---

## 二、会话级别 Context 日常更新

### 2.1 触发时机

| 项目 | 内容 |
|-----|------|
| **执行频率** | 每 **5 轮** 对话执行一次 |
| **触发点** | LLM 返回完整响应后，保存消息完成时 |
| **方式** | 简单规则匹配（非 LLM 调用） |

### 2.2 更新内容

| 字段 | 来源 | 说明 |
|-----|------|------|
| **消息总数** | 自动统计 | 累计消息数量 |
| **最后更新时间** | 自动记录 | 时间戳 |
| **主题** | 规则匹配 | 从最近用户消息中提取关键词 |
| **当前任务** | 规则匹配 | 用户意图（如"调试"、"开发"、"咨询"等） |
| **最近消息** | 自动提取 | 最近 5 条消息的摘要 |
| **项目/工程环境** | 规则匹配 | 技术栈、框架、工具（如 Python、Vue、Django） |
| **用户关键信息** | 规则匹配 | 用户明确要求记住的内容（如"记住我叫..."） |

### 2.3 更新目标文件

```
{chat_sessions_dir}/{session_id}/_context.md
```

---

## 三、L5 触发时的深度处理

### 3.1 触发条件

| 条件 | 阈值 | 说明 |
|-----|------|------|
| 消息数量 | ≥20 条 | 当消息总数达到 20 条时触发 |
| Token 数量 | ≥8000 | 当上下文 token 数超过 8000 时触发 |
| 累计新增 Token | ≥3000 | 距上次摘要后新增超过 3000 tokens |
| 无工具调用轮次 | ≥2 轮 | 连续 2 轮无 AI 工具调用 |

### 3.2 执行时机

在 LLM 返回完整响应后，会话消息已保存，此时执行 L5 处理。

### 3.3 处理流程

```
┌─────────────────────────────────┐
│ 检查 L5 触发条件                │
│ (4个条件满足任一即触发)         │
└─────────────────────────────────┘
              ↓
         构建 LLM Prompt
              ↓
         调用 LLM (禁用工具)
              ↓
         解析 LLM 返回 JSON
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
 会话深度摘要       记忆提取
    ↓                   ↓
 更新会话         保存/更新
 _context.md      记忆到
                  _global/memories/
                      ↓
                 更新全局
                 _context.md
                      ↓
                 压缩历史消息
```

---

## 四、L5 时的 LLM Prompt 设计

### 4.1 Prompt 结构

```markdown
## 任务指令
分析以下对话，输出 JSON 格式的结果。不要调用任何工具，只返回文本内容。

## 输出格式
{
  "session_summary": {
    "topic": "主题关键词",
    "task": "当前任务描述",
    "progress": ["已完成步骤1", "进行中步骤2"]
  },
  "memory_updates": [
    {
      "type": "user|feedback|project|reference",
      "action": "create|update",
      "name": "记忆名称",
      "content": "记忆内容",
      "description": "一句话描述"
    }
  ]
}

## 输入内容
1. 最近消息: ...
2. 历史摘要: ...
3. 用户画像: ...
4. 已有关联记忆: ...

## 要求
- 主题提取简洁的关键词
- 任务描述当前对话的目标
- 只提取有长期价值的信息作为记忆
- 如果没有需要提取的记忆，memory_updates 返回空数组
- progress 描述对话的进度步骤
```

### 4.2 输入内容说明

| 输入项 | 来源 | 说明 |
|-------|------|------|
| **最近消息** | messages/ 目录 | 最近 10 条消息的完整内容 |
| **历史摘要** | _context.md | 之前的会话摘要（如果有） |
| **用户画像** | _global/_context.md | 用户ID、语言、技术水平、偏好等 |
| **已有关联记忆** | _global/memories/ | 当前会话相关的已有记忆 |

### 4.3 输出说明

| 输出项 | 用途 | 存储位置 |
|-------|------|---------|
| **session_summary** | 会话深度摘要，覆盖/细化日常摘要 | `{session_id}/_context.md` |
| **memory_updates** | 需要新增/更新的记忆 | `_global/memories/{type}/_index.md` |

---

## 五、记忆提取策略

### 5.1 记忆类型定义

| 类型 | 用途 | 触发时机 |
|-----|------|---------|
| **user** | 用户角色、偏好、知识水平 | 用户介绍自己身份/习惯时 |
| **feedback** | 用户纠正/确认的行为指导 | 用户说"不要这样"、"很好继续"时 |
| **project** | 进行中的工作、目标、bug | 用户描述项目/任务时 |
| **reference** | 外部系统指针 | 用户提供链接/参考时 |

### 5.2 记忆提取流程

```
日常摘要识别
    ↓
标记需要记忆的内容（关键词、用户明确要求等）
    ↓
L5 触发时 LLM 判断
    ↓
决定是否保存为长期记忆
    ↓
保存到 _global/memories/{type}/
    ↓
更新全局 _context.md 中的记忆引用
```

### 5.3 更新全局 Context

L5 执行后，更新 `_global/_context.md`：
- 更新用户画像（如技术栈变化）
- 更新偏好信息
- 更新已知项目
- 追加记忆引用

---

## 六、历史消息压缩

### 6.1 压缩时机

L5 触发时，完成摘要后执行压缩。

### 6.2 压缩策略

| 项目 | 内容 |
|-----|------|
| **保留** | 最近 10 条完整消息 |
| **压缩** | 之前的消息合并为摘要 |
| **摘要长度** | 预留 2000 token |

### 6.3 压缩后的消息存储

```
messages/
├── 001_user.md      (保留)
├── 002_assistant.md (保留)
├── ...
├── 010_user.md      (保留，最后一条)
├── _summary.md      (新增，早期消息摘要)
```

---

## 七、配置项

### 7.1 新增/修改的配置

| 配置项 | 值 | 说明 |
|-------|-----|------|
| `SUMMARIZE_TRIGGER_COUNT` | 20 | 消息数量触发阈值 |
| `SUMMARIZE_TRIGGER_TOKENS` | 8000 | Token 数量触发阈值 |
| `SUMMARIZE_TRIGGER_DELTA` | 3000 | 累计新增 Token 阈值 |
| `SUMMARIZE_TRIGGER_NO_TOOL_ROUNDS` | 2 | 无工具调用轮次阈值 |
| `SUMMARIZE_DEBOUNCE_SECONDS` | 300 | 摘要防抖时间（秒） |
| `SUMMARIZE_KEEP_MESSAGES` | 10 | 保留最近消息数 |
| `SUMMARIZE_SUMMARY_RESERVE` | 2000 | 摘要预留 token 数 |
| `SESSION_SUMMARY_INTERVAL` | 5 | 会话日常摘要执行间隔（轮次） |

---

## 八、实施文件清单

### 8.1 新增文件

| 文件 | 职责 |
|-----|------|
| `session_context_manager.py` | 会话上下文管理（日常摘要） |
| `llm_summarizer.py` | LLM 摘要器（深度摘要+记忆提取） |

### 8.2 修改文件

| 文件 | 修改内容 |
|-----|---------|
| `chat.py` | 集成上下文更新调用 |
| `session_manager.py` | 添加配置项 |
| `global_context.py` | 添加更新方法 |

---

## 九、流程图

```
用户发送消息
    ↓
LLM 返回完整响应
    ↓
保存用户消息 + 保存 AI 消息
    ↓
┌─────────────────────────────────┐
│ 会话级别日常摘要 (每5轮执行)     │
│ - 简单规则匹配                  │
│ - 更新主题、任务、最近消息     │
│ - 项目环境、用户关键信息       │
│ - 更新会话 _context.md          │
└─────────────────────────────────┘
    ↓
检查 L5 触发条件
    ├─ 不满足 → 结束
    └─ 满足 → 执行 L5 处理
              ↓
         构建 LLM Prompt
              ↓
         调用 LLM (禁用工具)
              ↓
         解析 LLM 返回
              ↓
         ┌────┴────┐
         ↓         ↓
    会话深度摘要    记忆提取
         ↓         ↓
    更新会话      保存到
    _context     _global/memories/
                  ↓
             更新全局 _context
                  ↓
             压缩历史消息
```

---

## 十、LLM 摘要 Prompt 重构

### 10.1 设计目标

将 prompt 从 user 消息移到 system 消息，提高 LLM 返回格式的稳定性。

### 10.2 消息结构调整

#### System 消息结构

```system
你是上下文管理助手，负责分析对话并提取摘要和记忆。

## 任务指令
分析以下对话，输出 JSON 格式的结果。不要调用任何工具，只返回文本内容。

## 输出格式
{
  "session_summary": {
    "topic": "主题关键词",
    "task": "当前任务描述",
    "progress": ["已完成步骤1", "进行中步骤2"]
  },
  "memory_updates": [
    {
      "type": "user|feedback|project|reference",
      "action": "create|update",
      "name": "记忆名称",
      "content": "记忆内容",
      "description": "一句话描述"
    }
  ]
}

## 输入内容
1. 最近消息: [最近10条消息内容]
2. 历史摘要: [从_context.md的历史摘要部分提取]
3. 用户画像: [用户ID、使用语言、技术水平、用户偏好、已知项目]
4. 已有关联记忆: [当前会话关联的记忆列表]

## 要求（必须严格遵守）
- 只输出 JSON，不要有任何其他内容
- session_summary 必须包含 topic、task、progress 三个字段
- memory_updates 中每条记忆必须包含 type、name、content、description 四个字段
- type 只允许: user, feedback, project, reference
- action 只允许: create, update
- progress 必须是数组，每个元素是一个步骤描述
```

#### User 消息结构

```user
请按上述格式要求返回 JSON，不要输出任何其他内容。
```

### 10.3 API 调用参数

```python
response = await client.chat.completions.create(
    model=conf.OPENAI_MODEL,
    messages=[
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': '请按上述格式要求返回 JSON，不要输出任何其他内容。'}
    ],
    temperature=0.1,  # 降低随机性
    max_tokens=2000,
)
```

### 10.4 响应解析兼容性处理

#### 10.4.1 JSON 提取
```python
def _extract_json(content: str) -> Optional[str]:
    """从 LLM 返回内容中提取 JSON"""
    # 去除思考内容
    content = re.sub(r'【.*?】', '', content, flags=re.DOTALL)
    # 去除 markdown 代码块
    if content.startswith('```'):
        lines = content.split('\n')
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                json_lines.append(line)
        content = '\n'.join(json_lines)
    
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        return content[json_start:json_end]
    return None
```

#### 10.4.2 格式兼容性处理
```python
def _normalize_result(self, result: Dict) -> Tuple[Dict, List]:
    """兼容 LLM 返回的各种格式"""
    session_summary = result.get('session_summary', {})
    
    # 如果 session_summary 为空，尝试从顶层提取
    if not session_summary:
        session_summary = {
            'topic': result.get('topic', ''),
            'task': result.get('task', ''),
            'progress': result.get('progress', [])
        }
    
    # 兼容 progress 为字符串的情况
    if isinstance(session_summary.get('progress'), str):
        session_summary['progress'] = [session_summary['progress']]
    
    memory_updates = result.get('memory_updates', [])
    
    return session_summary, memory_updates
```

---

## 十一、更新日志

| 日期 | 版本 | 更新内容 |
|-----|------|---------|
| 2026-04-10 | v1.0 | 初始版本，记录上下文自动更新设计方案 |
| 2026-04-10 | v1.1 | 修复 LLM 摘要 JSON 解析问题 |
| 2026-04-10 | v1.2 | 增强日志记录，完整保存 LLM 原始响应 |
| 2026-04-10 | v1.3 | 重构 LLM 摘要 Prompt：分离 system/user 消息，添加格式兼容性处理 |

---

## 十二、已知问题与修复

### 12.1 LLM 摘要 JSON 解析失败

**问题描述**：
- LLM 返回的内容可能包含 markdown 代码块（如 ```json ... ```）
- 直接使用 `json.loads()` 解析会失败：`Expecting ',' delimiter`
- LLM 返回的 JSON 格式不固定（嵌套 vs 顶层、progress 字符串 vs 数组）

**解决方案**：
- 新增 `_extract_json()` 方法处理 markdown 代码块
- 新增 `_normalize_result()` 方法处理格式兼容性
- 使用严格的 system prompt + temperature=0.1 提高格式稳定性

**日志跟踪点**：
| 位置 | 日志级别 | 内容 |
|-----|---------|------|
| `run_summarization` 开始 | INFO | ===== START SUMMARIZATION =====, session_id, user_id, prompt length |
| 调用 LLM API 前 | INFO | calling LLM API... |
| LLM API 调用完成 | INFO | LLM API call completed |
| LLM 返回后 | INFO | ===== RAW LLM RESPONSE =====, response length, 完整响应内容 |
| JSON 解析成功 | INFO | ===== SUMMARIZATION RESULT =====, session_summary, memory_updates 详情 |
| 摘要完成 | INFO | ===== SUMMARIZATION COMPLETE ===== |
| 摘要失败 | FATAL | ===== SUMMARIZATION FAILED =====, 错误详情, 完整堆栈 |

**修复文件**：
- `llm_summarizer.py`: 添加 `_extract_json` 方法、`_normalize_result` 方法、完整日志记录