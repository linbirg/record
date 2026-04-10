# AI Chat 思考过程处理分析

> 版本：v1.0
> 状态：已完成
> 创建：2026-04-10

---

## 一、概述

本文档分析 AI Chat 系统中思考过程（reasoning_content）的完整处理流程，包括后端 API 调用、数据传递、前端展示。

---

## 二、后端处理流程

### 2.1 LLM API 调用

**文件**: `yail/www/handlers/chat/chat.py`

**代码位置**: `call_llm_stream` 函数，约第 240-270 行

```python
client = get_openai_client()
full_reasoning = ""
full_content = ""

response = await client.chat.completions.create(
    model=conf.OPENAI_MODEL,
    messages=openai_messages,
    stream=True,
)

async for chunk in response:
    if not chunk.choices:
        continue

    delta = chunk.choices[0].delta
    
    # 处理思考内容
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        full_reasoning = delta.reasoning_content
        yield {'reasoning_content': full_reasoning, 'content': full_content}
    
    # 处理正文内容
    if hasattr(delta, 'content') and delta.content:
        full_content += delta.content
        yield {'reasoning_content': full_reasoning, 'content': full_content}

# 保存消息
msg_store.save_assistant_message(
    content=full_content,
    reasoning_content=full_reasoning,
)
```

### 2.2 数据流图

```
MiniMax API (streaming)
       ↓
chunk.choices[0].delta
       ↓
   ┌───────┴───────┐
   ↓               ↓
has reasoning_content?  has content?
   ↓               ↓
   ↓         full_content += content
   ↓         yield {reasoning_content, content}
   ↓
full_reasoning = delta.reasoning_content
yield {reasoning_content, content}
       ↓
msg_store.save_assistant_message(
    content=full_content,
    reasoning_content=full_reasoning,
)
```

### 2.3 关键代码逻辑

| 条件 | 触发动作 |
|-----|---------|
| `hasattr(delta, 'reasoning_content')` 且有值 | 更新 full_reasoning，yield |
| `hasattr(delta, 'content')` 且有值 | 更新 full_content，yield |

---

## 三、前端处理流程

### 3.1 消息接收

**文件**: `frontEnd/src/components/ChatList/chat.vue`

**代码位置**: `sendChatMessage` 方法，约第 99-116 行

```javascript
this.$store.dispatch('sendChatMessageStream', {
    content: content,
    onChunk: (data) => {
        const lastMsg = this.messages[this.messages.length - 1]
        
        if (typeof data === 'string') {
            lastMsg.content = data
        } else {
            if (data.reasoning_content !== undefined) {
                lastMsg.reasoning_content = data.reasoning_content
            }
            if (data.content !== undefined) {
                lastMsg.content = data.content
            }
        }
        this.$forceUpdate()
        this.scrollToBottom()
    },
    // ...
})
```

### 3.2 消息展示

**文件**: `frontEnd/src/components/ChatList/message.vue`

**模板结构**:
```vue
<div class="message-bubble" :class="isUser ? 'user' : 'ai'">
    <!-- 思考过程区域 -->
    <div v-if="!isUser && hasReasoning" class="reasoning-wrapper">
        <div class="reasoning-toggle" @click="toggleReasoning">
            <span>{{ isReasoningExpanded ? '▼' : '▶' }}</span>
            <span>{{ isReasoningExpanded ? '收起思考过程' : '展开思考过程' }}</span>
        </div>
        <div v-show="isReasoningExpanded" class="reasoning-content" v-html="renderedReasoning"></div>
    </div>
    <!-- 正文内容 -->
    <div class="bubble" v-html="renderedContent"></div>
</div>
```

### 3.3 计算属性

```javascript
computed: {
    hasReasoning() {
        return this.message.reasoning_content && this.message.reasoning_content.length > 0
    },
    renderedReasoning() {
        if (!this.message.reasoning_content) return ''
        return DOMPurify.sanitize(this.escapeHtml(this.message.reasoning_content))
    },
    renderedContent() {
        if (this.isUser) {
            return DOMPurify.sanitize(this.escapeHtml(this.message.content))
        }
        if (!this.message.content) return ''
        const html = marked.parse(this.message.content)
        return DOMPurify.sanitize(html)
    }
}
```

### 3.4 前端数据流图

```
后端 yield {reasoning_content, content}
       ↓
chat.vue onChunk callback
       ↓
   ┌───────┴───────┐
   ↓               ↓
data.reasoning_content  data.content
   ↓               ↓
lastMsg.reasoning_content = ...  lastMsg.content = ...
       ↓
this.$forceUpdate()
       ↓
message.vue 渲染
       ↓
   hasReasoning = reasoning_content && length > 0
       ↓
   v-if="!isUser && hasReasoning"
       ↓
   显示 "展开思考过程" 按钮
   点击后 v-show="isReasoningExpanded" 显示内容
```

---

## 四、可能问题与排查

### 4.1 前端只显示最终结果

**可能原因**:

1. **MiniMax API 返回的 delta 中没有 `reasoning_content` 属性**
   - 后端用 `hasattr(delta, 'reasoning_content')` 检查
   - 如果没有这个属性，条件不满足，思考内容不会被处理

2. **API 返回的字段名不是 `reasoning_content`**
   - MiniMax 可能使用其他字段名（如 `thinking`、`reasoning` 等）

3. **API 没有返回思考内容**
   - 可能模型配置问题，或者请求参数没开启思考

### 4.2 排查步骤

1. **检查后端日志**
   - 查看 `delta attrs` 显示的实际属性名
   - 位置：`chat.py` 第 254 行 `logger.LOG_TRACE`

2. **检查 MiniMax API 文档**
   - 确认 streaming response 的实际结构
   - 确认 `reasoning_content` 字段名

3. **前端调试**
   - 在 `onChunk` 中添加 `console.log(data)`
   - 观察实际接收到的数据结构

---

## 五、官方 API 修复方案

### 5.1 问题根因

通过日志分析和官方 API 示例对比，发现以下问题：

| 问题 | 当前实现 | 官方示例 |
|-----|---------|---------|
| API 参数 | 无特殊参数 | `extra_body={"reasoning_split": True}` |
| 思考字段 | `delta.reasoning_content` | `delta.reasoning_details` |
| 处理方式 | 直接读取属性 | 遍历列表检查 `"text" in detail` |

### 5.2 官方 API 示例

```python
from openai import OpenAI
client = OpenAI()

stream = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hi, how are you?"},
    ],
    # 设置 reasoning_split=True 将思考内容分离到 reasoning_details 字段
    extra_body={"reasoning_split": True},
    stream=True,
)

reasoning_buffer = ""
text_buffer = ""

for chunk in stream:
    if (
        hasattr(chunk.choices[0].delta, "reasoning_details")
        and chunk.choices[0].delta.reasoning_details
    ):
        for detail in chunk.choices[0].delta.reasoning_details:
            if "text" in detail:
                reasoning_text = detail["text"]
                new_reasoning = reasoning_text[len(reasoning_buffer) :]
                if new_reasoning:
                    print(new_reasoning, end="", flush=True)
                    reasoning_buffer = reasoning_text

    if chunk.choices[0].delta.content:
        content_text = chunk.choices[0].delta.content
        new_text = content_text[len(text_buffer) :] if text_buffer else content_text
        if new_text:
            print(new_text, end="", flush=True)
            text_buffer = content_text
```

### 5.3 修复方案

**文件**: `yail/www/handlers/chat/chat.py`

**修改内容**:

1. API 调用添加 `reasoning_split` 参数：
```python
response = await client.chat.completions.create(
    model=conf.OPENAI_MODEL,
    messages=openai_messages,
    stream=True,
    extra_body={"reasoning_split": True},  # 新增
)
```

2. 处理逻辑改为遍历 `reasoning_details`：
```python
for chunk in response:
    delta = chunk.choices[0].delta
    
    # 处理思考内容
    if (hasattr(delta, 'reasoning_details') 
        and delta.reasoning_details):
        for detail in delta.reasoning_details:
            if "text" in detail:
                reasoning_text = detail["text"]
                full_reasoning += reasoning_text
                yield {'reasoning_content': full_reasoning, 'content': full_content}
    
    # 处理正文内容
    if delta.content:
        full_content += delta.content
        yield {'reasoning_content': full_reasoning, 'content': full_content}
```

---

## 六、相关文件清单

| 文件 | 职责 |
|-----|------|
| `yail/www/handlers/chat/chat.py` | 后端 LLM 调用，处理 streaming 响应 |
| `frontEnd/src/components/ChatList/chat.vue` | 前端消息发送和接收 |
| `frontEnd/src/components/ChatList/message.vue` | 前端消息渲染和展示 |

---

## 七、更新日志

| 日期 | 版本 | 更新内容 |
|-----|------|---------|
| 2026-04-10 | v1.0 | 初始版本，记录思考过程处理分析 |
| 2026-04-10 | v1.1 | 添加官方 API 修复方案，修复 reasoning_details 处理逻辑 |