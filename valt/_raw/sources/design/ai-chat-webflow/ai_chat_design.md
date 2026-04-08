# AI Chat 对话界面设计方案

## 一、需求概述

将前端界面右边的 Todo List 替换为 AI Chat 对话框。

**技术栈**：
- 前端：Vue 2 + element-ui + webpack 3
- 后端：Python aiohttp + 自研 yeab 框架
- AI：MiniMax API（支持 reasoning_content 思考过程）

---

## 二、设计系统：Webflow Style

基于 Webflow 设计系统的 AI Chat 对话界面视觉规范。

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

#### Primary
```scss
$near-black: #080808;        // 主文字
$webflow-blue: #146ef5;      // 主品牌色
$blue-400: #3b89ff;          // 浅蓝交互
$blue-hover: #0055d4;        // 按钮悬停蓝
```

#### Neutral
```scss
$gray-800: #222222;          // 次要文字
$gray-300: #ababab;          // 占位符/禁用
$border-gray: #d8d8d8;       // 边框
$border-hover: #898989;      // 悬停边框
```

#### Background
```scss
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

### 2.4 Typography

| 元素 | 大小 | 粗细 | 字间距 |
|------|------|------|--------|
| Header 标题 | 12px | 550 | 1.5px, uppercase |
| 消息正文 | 14px | 400-500 | normal |
| 时间戳 | 12px | 400 | normal |
| 占位符 | 14px | 400 | normal |

---

## 三、UI 设计规范

### 3.1 整体布局

**位置与尺寸**（沿用现有 RightSide）：
```
position: fixed
top: 72px
left: 1335px
width: 500px
height: calc(100vh - 72px - 20px)
```

**组件结构**：
```
Chat (主容器)
├── ChatHeader (标题栏: ALOHA + 清空按钮)
├── MessageList (消息列表，可滚动)
│   └── MessageBubble (消息气泡)
│       ├── UserMessage (右侧，蓝色)
│       └── AIMessage (左侧，白色)
└── ChatInput (输入区域: textarea + 拖动条)
```

### 3.2 ChatHeader

```
高度: 32px (更紧凑)
背景: #ffffff
边框: 底部 1px solid #d8d8d8
阴影: 无

左侧:
  - 🤖 emoji 图标 (14px)
  - "ALOHA" 文字 (12px, uppercase, letter-spacing 1.5px, weight 550, #080808)

右侧:
  - 删除按钮 (el-icon-delete)
  - 悬停: transform translate(6px), 颜色变 #146ef5
```

### 3.3 消息气泡 - 用户消息

```
背景: #146ef5 (Webflow Blue)
文字: #ffffff
圆角: 4px
阴影: 轻量单层阴影
最大宽度: 75%
内边距: 12px 16px
align-self: flex-end
```

### 3.4 消息气泡 - AI 消息

```
背景: #ffffff
文字: #080808
边框: 1px solid #d8d8d8
圆角: 4px
阴影: 5层阴影系统
最大宽度: 75%
内边距: 12px 16px
align-self: flex-start
```

### 3.5 欢迎语气泡

```
背景: #ffffff
边框: 1px solid #d8d8d8
圆角: 4px
阴影: 5层阴影
文字: #ababab (居中)
内边距: 16px 24px
```

### 3.6 输入框

```
背景: #f5f5f5 (灰色底) → 聚焦时 #ffffff (白底)
边框: 1px solid #d8d8d8
圆角: 4px
聚焦边框: #146ef5
内边距: 10px 12px
字体: 14px, weight 400-500, #080808
占位符: #ababab
```

### 3.7 拖动条

```
高度: 4px
背景: 渐变灰 (#d8d8d8 → transparent)
圆角: 2px
悬停: 颜色加深
```

### 3.8 字体规范

| 元素 | 字号 | 颜色 |
|------|------|------|
| 正文 | 14px | #080808 |
| 时间戳 | 12px | #999999 |
| 标题 | 12px | #080808, uppercase |

### 3.9 间距规范

| 元素 | 数值 |
|------|------|
| 气泡内边距 | 12px 16px |
| 气泡间距 | 12px |
| 气泡圆角 | 4px |
| Header 内边距 | 0 12px |

---

## 四、组件详细设计

### 4.1 ChatHeader

```
高度: 32px
背景: #ffffff
边框: 底部 1px solid #d8d8d8

布局:
  左侧:
    - 🤖 emoji 图标 (14px)
    - "ALOHA" 标题 (12px, uppercase, letter-spacing 1.5px, weight 550)
  右侧:
    - 删除图标 (el-icon-delete)
    - 悬停: transform translate(6px), 颜色变 #146ef5
```

### 4.2 MessageList

```
flex: 1
min-height: 0 (允许收缩至0)
overflow-y: auto
padding: 16px
display: flex
flex-direction: column
gap: 12px
背景: #f5f5f5

/* 滚动条样式 */
&::-webkit-scrollbar {
  width: 4px;
}
&::-webkit-scrollbar-thumb {
  background: #d8d8d8;
  border-radius: 2px;
}
```

### 4.3 MessageBubble

**用户消息（右侧）**：
```
align-self: flex-end
background: #146ef5
color: white
border-radius: 4px
max-width: 75%
padding: 12px 16px
```

**AI 消息（左侧）**：
```
align-self: flex-start
background: white
color: #080808
border: 1px solid #d8d8d8
border-radius: 4px
box-shadow: $shadow-5layer
max-width: 75%
padding: 12px 16px
```

**时间戳**：显示在气泡下方，小字灰色

### 4.4 ChatInput

```
布局机制:
  - chat 主容器: flex column, height 100%, overflow hidden
  - chat-header: 固定 32px
  - message-list: flex 1, min-height 0 (可收缩至0)
  - chat-input: 动态高度 (40px ~ 160px)

拖动条:
  高度: 4px
  位置: 输入框上方
  样式: 渐变灰条 (#d8d8d8 → transparent)
  交互: 向上拖动扩大输入区域
  高度范围: 40px ~ 160px

textarea:
  width: 100%
  height: 100%
  border: 1px solid #d8d8d8
  resize: none
  padding: 10px 12px
  font-size: 14px
  背景: #f5f5f5
  聚焦时: border-color: #146ef5, background: #ffffff
```

---

## 五、交互动效

| 元素 | 动效 |
|------|------|
| 删除按钮 | `transform: translate(6px)` + 颜色 `#146ef5` |
| 输入框聚焦 | 边框颜色 `#146ef5` + 背景变白 |
| 消息气泡 | 5层阴影系统 |

---

## 六、交互设计

### 6.1 发送消息

- **回车发送**（无需按钮）
- **Shift+Enter 换行**
- 发送后清空输入框
- 自动滚动到底部
- 发送时禁用输入框（防止重复发送）

### 6.2 输入框拖动

- 鼠标按住拖动条向上拖动 → 输入框高度增加
- **同时消息列表向上收缩**（优先级：先收缩消息列表）
- 当消息列表完全收缩后，输入框才能继续扩大
- 拖动时输入框区域显示高亮背景 (`#f5f5f5`)
- **消息列表在收缩状态下出现滚动条**（当消息内容超出可见区域时）

### 6.3 AI 思考状态

- 显示加载动画（三点跳动）
- 禁止重复发送
- 思考过程（reasoning_content）单独显示，可折叠

### 6.4 空状态

- 显示欢迎语："👋 Aloha! 我是 ALOHA，有什么可以帮你的？"

### 6.5 清空对话

- 点击清空按钮
- 弹出确认提示

---

## 七、Markdown 支持

### 7.1 支持格式

- 标题 (h1-h6)
- 列表 (有序/无序)
- 粗体、斜体
- 代码块（语法高亮）
- 行内代码
- 链接

### 7.2 安全考虑

- 使用 DOMPurify 净化 HTML 输出
- 防止 XSS 攻击

---

## 八、文件结构

### 前端文件

```
frontEnd/src/components/ChatList/
├── chat.vue      # 主组件
└── message.vue   # 消息气泡组件（含 Markdown 渲染 + 思考过程折叠）

# 修改文件
frontEnd/src/components/rightSide.vue  # 替换 Todo → Chat
frontEnd/src/store/index.js            # 新增 chat actions
```

### 后端文件

```
yail/
├── conf/
│   └── dev.py                          # OpenAI 配置
├── lib/yeab/
│   └── web.py                         # 新增 @stream 装饰器
├── www/
│   ├── dao/
│   │   ├── chat_message.py            # 消息 DAO 模型
│   │   └── field_desc.py              # 新增 SessionIdField, RoleField
│   └── handlers/
│       └── chat/
│           ├── chat.py                 # 流式聊天 Handler
│           └── mock_chat.py            # Mock Handler (20条预设回复)
└── tools/
    └── migrate/
        └── 7_chat_message.py          # 数据库迁移
```

---

## 九、Session 管理

### 9.1 设备级 Session 方案

```
session_id = UUID（首次聊天时生成）
- 存储在浏览器 localStorage
- 每个浏览器设备独立会话
- 换设备登录 = 新会话
- 登出再登录 = 同一设备 session 保持
```

### 9.2 Session 流程

| 场景 | 处理方式 |
|------|----------|
| 首次使用 | 前端生成 UUID 作为 sessionId，发送到后端 |
| 页面刷新 | 读取 localStorage 中的 sessionId，继续同一会话 |
| 用户登出 | Session 保留在数据库 |
| 用户换设备 | 生成新的 sessionId |
| 清空对话 | 仅删除该 sessionId 的消息 |

---

## 十、后端架构

### 10.1 技术选型

| 组件 | 方案 | 说明 |
|------|------|------|
| 通信协议 | SSE (Server-Sent Events) | 轻量、单向流 |
| 前端接收 | Fetch API + ReadableStream | 原生支持，无依赖 |
| AI API | MiniMax API | 支持 `reasoning_content` 思考过程 |

### 10.2 MiniMax 特殊字段

MiniMax API 返回的特殊字段：
- `reasoning_content`：AI 思考过程（可用于展示折叠内容）
- `content`：正式回复内容

### 10.3 流式响应流程

```
前端                          后端 (yeab)                      MiniMax
  │                              │                                │
  │  POST /chat/send             │                                │
  │─────────────────────────────>│                                │
  │                              │  stream=True                   │
  │                              │───────────────────────────────>│
  │                              │                                │
  │  SSE 流响应                   │<──────────────────────────────│
  │<─────────────────────────────│   chunk: reasoning_content     │
  │   event: chunk               │                                │
  │   data: {"reasoning": "..."} │                                │
  │                              │                                │
  │  SSE 流响应                   │<──────────────────────────────│
  │<─────────────────────────────│   chunk: content               │
  │   event: chunk               │                                │
  │   data: {"content": "..."}   │                                │
  │                              │                                │
  │  SSE 流响应 (done)            │                                │
  │<─────────────────────────────│                                │
  │   event: done               │                                │
```

---

## 十一、API 接口设计

### 11.1 发送消息（流式）- Mock

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
data: {"reasoning_content": "思考中...", "content": ""}

event: chunk
data: {"content": "你好呀"}
```

### 11.2 发送消息（流式）- 真实

```
POST /chat/send_real
Content-Type: application/json

Request:
{
  "userId": 1,
  "content": "你好",
  "sessionId": "abc-123-uuid"
}

Response: SSE 流
event: chunk
data: {"reasoning_content": "思考中...", "content": ""}

event: chunk
data: {"content": "你好呀"}
```

### 11.3 获取历史

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
    {"role": "user", "content": "你好", "createdAt": "2024-01-01 10:00:00"},
    {"role": "assistant", "content": "你好呀", "createdAt": "2024-01-01 10:00:01"}
  ]
}
```

### 11.4 清空会话

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

## 十二、数据库设计

### 12.1 表结构

```sql
CREATE TABLE t_chat_message (
  id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  user_id         INT NOT NULL COMMENT '用户ID',
  session_id      VARCHAR(64) NOT NULL COMMENT '会话ID(UUID)',
  role            ENUM('user', 'assistant') NOT NULL COMMENT '角色',
  content         TEXT NOT NULL COMMENT '消息内容',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_user_session (user_id, session_id),
  INDEX idx_session_time (session_id, created_at)
) COMMENT '聊天消息表';
```

### 12.2 新增字段描述

```python
# www/dao/field_desc.py

class SessionIdField(StringField):
    def __init__(self, desc='会话ID'):
        super().__init__(name='session_id',
                         primary_key=False,
                         default=None,
                         ddl='varchar(64)',
                         desc=desc)

class RoleField(CharField):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    def __init__(self, name='role', desc='角色'):
        super().__init__(name=name, size=20, default=None, desc=desc)
```

---

## 十三、代码设计

### 13.1 @stream 装饰器 (lib/yeab/web.py)

```python
def stream(coro):
    """
    定义装饰器 @stream
    用于流式响应，返回 web.StreamResponse
    Handler 必须自行处理请求和响应
    """
    @functools.wraps(coro)
    async def wrapper(*args, **kw):
        return await coro(*args, **kw)

    wrapper.__stream__ = True
    return wrapper
```

### 13.2 配置 (conf/dev.py)

```python
ROOT = 'D:/project/linbirg/ww/ww/record/yail'
PIC_DIR = 'D:/project/linbirg/ww/ww/record/frontEnd/static/car'
PIC_URL = 'static/car'

# AI 配置
OPENAI_API_KEY = 'your-api-key'
OPENAI_BASE_URL = 'https://api.minimax.chat/v1'
OPENAI_MODEL = 'MiniMax-M2.7'
OPENAI_MAX_HISTORY = 20
```

### 13.3 Mock 流式 Handler (www/handlers/chat/mock_chat.py)

```python
@post("/chat/send")
@stream
async def mock_chat_send(request):
    data = await request.json()
    user_id = data.get('userId')
    content = data.get('content')
    session_id = data.get('sessionId', str(user_id))

    resp = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )
    await resp.prepare(request)

    # 模拟 AI 思考过程
    for chunk in mock_reasoning_content(content):
        event_data = json.dumps({'reasoning_content': chunk}, ensure_ascii=False)
        await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
        await asyncio.sleep(0.1)

    # 模拟 AI 回复
    for chunk in mock_content(content):
        event_data = json.dumps({'content': chunk}, ensure_ascii=False)
        await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
        await asyncio.sleep(0.2)

    await resp.write(f"event: done\ndata: \n\n".encode('utf-8'))
    await resp.write_eof()
    return resp
```

### 13.4 流式 Handler (www/handlers/chat/chat.py)

```python
@post("/chat/send_real")
@stream
async def chat_send(request):
    data = await request.json()
    user_id = data.get('userId')
    content = data.get('content')
    session_id = data.get('sessionId', str(user_id))

    resp = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )
    await resp.prepare(request)

    # 获取历史消息
    history = yield from ChatMessage.find_by_session(
        user_id, session_id, conf.OPENAI_MAX_HISTORY
    )
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": content})

    # 保存用户消息
    user_msg = ChatMessage(user_id=user_id, session_id=session_id,
                           role='user', content=content)
    yield from user_msg.save()

    # 调用 MiniMax 流式 API
    full_content = ""
    full_reasoning = ""
    try:
        client = openai.OpenAI(
            api_key=conf.OPENAI_API_KEY,
            base_url=conf.OPENAI_BASE_URL
        )
        stream_resp = client.chat.completions.create(
            model=conf.OPENAI_MODEL,
            messages=messages,
            stream=True
        )

        for chunk in stream_resp:
            delta = chunk['choices'][0]['delta']
            if 'reasoning_content' in delta:
                full_reasoning += delta['reasoning_content']
                event_data = json.dumps({'reasoning_content': full_reasoning}, ensure_ascii=False)
                await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
            if 'content' in delta:
                full_content += delta['content']
                event_data = json.dumps({'content': full_content}, ensure_ascii=False)
                await resp.write(f"event: chunk\ndata: {event_data}\n\n".encode('utf-8'))
    except Exception as e:
        await resp.write(f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n".encode('utf-8'))

    # 保存 AI 回复
    if full_content:
        ai_msg = ChatMessage(user_id=user_id, session_id=session_id,
                            role='assistant', content=full_content)
        yield from ai_msg.save()

    await resp.write(f"event: done\ndata: \n\n".encode('utf-8'))
    await resp.write_eof()
    return resp
```

---

## 十四、实施步骤

| 顺序 | 任务 | 状态 | 文件 |
|------|------|------|------|
| 1 | 添加 `openai` 到 requirements.txt | ✅ | `yail/requeriment.txt` |
| 2 | 新增字段描述 | ✅ | `www/dao/field_desc.py` |
| 3 | 创建 DAO 模型 | ✅ | `www/dao/chat_message.py` |
| 4 | 创建数据库迁移 | ✅ | `tools/migrate/7_chat_message.py` |
| 5 | 运行迁移创建表 | ⏳ | `python tools/migrate/7_chat_message.py` |
| 6 | 添加 `@stream` 装饰器 | ✅ | `lib/yeab/web.py` |
| 7 | 添加 OpenAI 配置 | ✅ | `conf/dev.py` |
| 8 | 创建 Mock 流式 Handler | ✅ | `www/handlers/chat/mock_chat.py` |
| 9 | 创建真实 Handler | ✅ | `www/handlers/chat/chat.py` |
| 10 | 前端 Session 管理 + 流式接收 | ✅ | `frontEnd/src/store/index.js` |
| 11 | 安装 Python 依赖 | ⏳ | `pip install openai aiomysql` |
| 12 | 配置 API Key | ⏳ | `conf/dev.py` 中修改 OPENAI_API_KEY |
| 13 | 联调测试 | ⏳ | - |

---

## 十五、已完成的工作

### 前端 ✅

| 文件 | 说明 |
|------|------|
| `frontEnd/src/components/ChatList/chat.vue` | 主聊天组件（流式接收 + 唯一 ID 修复） |
| `frontEnd/src/components/ChatList/message.vue` | 消息气泡组件（Markdown 渲染 + 思考过程折叠） |
| `frontEnd/src/components/rightSide.vue` | 引入 Chat |
| `frontEnd/src/store/index.js` | 新增 `getChatSessionId`, `getChatHistory`, `clearChatSession`, `sendChatMessageStream`（sessionId Promise 问题修复） |
| `frontEnd/package.json` | 已添加 marked, dompurify, highlight.js |

### 后端 ✅

| 文件 | 说明 |
|------|------|
| `yail/requeriment.txt` | 已添加 openai>=1.0.0 |
| `yail/www/dao/field_desc.py` | 已添加 SessionIdField, RoleField |
| `yail/www/dao/chat_message.py` | 消息 DAO，含 find_by_session, delete_by_session |
| `yail/tools/migrate/7_chat_message.py` | 数据库迁移脚本 |
| `yail/lib/yeab/web.py` | 已添加 @stream 装饰器 |
| `yail/conf/dev.py` | 已添加 OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OPENAI_MAX_HISTORY |
| `yail/www/handlers/chat/chat.py` | 流式 Handler（真实 AI） |
| `yail/www/handlers/chat/mock_chat.py` | Mock Handler（20条预设回复） |
| `yail/www/handlers/chat/__init__.py` | 包标识文件 |

---

## 十六、部署说明

### 1. 安装 Python 依赖

```bash
cd yail
pip install openai aiomysql
```

### 2. 配置 AI API

编辑 `yail/conf/dev.py`：

```python
OPENAI_API_KEY = 'your-api-key'
OPENAI_BASE_URL = 'https://api.minimax.chat/v1'
OPENAI_MODEL = 'MiniMax-M2.7'
```

### 3. 运行数据库迁移

```bash
cd yail
python tools/migrate/7_chat_message.py
```

### 4. 启动服务

```bash
# 后端
cd yail
python app.py

# 前端（新窗口）
cd frontEnd
npm run dev
```

---

## 十七、已知问题与修复

### 问题1：Vue 消息内容不能累加显示

**原因**：Vue 2 响应式系统追踪数组元素内部变化存在问题，需使用唯一 ID 作为 key

**修复**：
- 添加 `msgIdCounter: Date.now()` 作为消息 ID 计数器
- 用户/助手消息创建时分配唯一 ID：`id: this.msgIdCounter++`
- 历史消息加载时分配 ID：`id: this.msgIdCounter + idx`

### 问题2：/chat/history 返回 500 错误

**原因**：`this.dispatch('getChatSessionId')` 返回 **Promise**，但代码将其当作字符串使用

**影响**：发送的 JSON 中 `sessionId` 为空对象 `{}`，导致后端查询失败

**修复**：
- `getChatHistory`：`const sessionId = await this.dispatch('getChatSessionId')`
- `clearChatSession`：`const sessionId = await this.dispatch('getChatSessionId')`
- `sendChatMessageStream`：改用 `localStorage.getItem('chatSessionId')` 直接获取
