# AI Chat 对话界面设计方案

## 一、需求概述

将前端界面右边的 Todo List 替换为 AI Chat 对话框。

**技术栈**：
- 前端：Vue 2 + element-ui + webpack 3
- 后端：Python aiohttp + 自研 yeab 框架
- AI：OpenAI ChatGPT API（流式输出）

---

## 二、依赖配置

### 前端依赖 (frontEnd/package.json)

```json
"devDependencies": {
  "marked": "^4.3.0",
  "dompurify": "^3.0.0",
  "highlight.js": "^11.9.0"
}
```

### 后端依赖 (yail/requeriment.txt)

```
watchdog
aiohttp>=3.7.4
aiomysql
cryptography
openai>=1.0.0
```

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

### 3.2 配色方案

| 元素 | 颜色 |
|------|------|
| 背景色 | `#f5f5f5` |
| 用户气泡 | `#50a2f2` (科技蓝) |
| AI 气泡 | `#ffffff` (白色) |
| 标题栏 | 渐变 #667eea → #764ba2 |
| 输入框背景 | `#ffffff` |
| 边框/分割线 | `#e0e0e0` |

### 3.3 字体规范

| 元素 | 字号 | 颜色 |
|------|------|------|
| 正文 | 14px | #333333 |
| 时间戳 | 12px | #999999 |
| 标题 | 15px | #ffffff |

### 3.4 间距规范

| 元素 | 数值 |
|------|------|
| 气泡内边距 | 12px 16px |
| 气泡间距 | 8px |
| 气泡圆角 | 8px |

---

## 四、组件详细设计

### 4.1 ChatHeader

```
高度: 44px
背景: 渐变色 (linear-gradient 135deg, #667eea → #764ba2)
阴影: 0 2px 8px rgba(102, 126, 234, 0.3)

布局:
  左侧:
    - 🤖 emoji 图标 (18px)
    - "ALOHA" 标题 (15px, font-weight 600, letter-spacing 2px)
  右侧:
    - 删除图标 (el-icon-delete)
    - 鼠标悬停时显示半透明背景
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

/* 滚动条样式 */
&::-webkit-scrollbar {
  width: 4px;
}
&::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}
```

### 4.3 MessageBubble

**用户消息（右侧）**：
```
align-self: flex-end
background: #50a2f2
color: white
border-radius: 8px 8px 0 8px
max-width: 75%
```

**AI 消息（左侧）**：
```
align-self: flex-start
background: white
color: #333
border-radius: 8px 8px 8px 0
box-shadow: 0 1px 4px rgba(0,0,0,0.1)
max-width: 75%
```

**时间戳**：显示在气泡下方，小字灰色

### 4.4 ChatInput

```
布局机制:
  - chat 主容器: flex column, height 100%, overflow hidden
  - chat-header: 固定 44px
  - message-list: flex 1, min-height 0 (可收缩至0)
  - chat-input: 动态高度 (40px ~ 160px)

拖动条:
  高度: 4px
  位置: 输入框上方
  样式: 渐变灰条 (#ddd → transparent)
  交互: 向上拖动扩大输入区域
  高度范围: 40px ~ 160px

textarea:
  width: 100%
  height: 100%
  border: none
  resize: none
  padding: 10px
  font-size: 14px
  背景: #f5f5f5
  聚焦时: box-shadow: 0 0 0 1px #50a2f2
```

---

## 五、交互设计

### 5.1 发送消息

- **回车发送**（无需按钮）
- **Shift+Enter 换行**
- 发送后清空输入框
- 自动滚动到底部
- 发送时禁用输入框（防止重复发送）

### 5.2 输入框拖动

- 鼠标按住拖动条向上拖动 → 输入框高度增加
- **同时消息列表向上收缩**（优先级：先收缩消息列表）
- 当消息列表完全收缩后，输入框才能继续扩大
- 拖动时输入框区域显示高亮背景 (`#f0f0f0`)
- **消息列表在收缩状态下出现滚动条**（当消息内容超出可见区域时）

### 5.3 AI 思考状态

- 显示加载动画（三点跳动）
- 禁止重复发送

### 5.4 空状态

- 显示欢迎语："👋 Aloha! 我是 ALOHA，有什么可以帮你的？"

### 5.5 清空对话

- 点击清空按钮
- 弹出确认提示

---

## 六、Markdown 支持

### 6.1 支持格式

- 标题 (h1-h6)
- 列表 (有序/无序)
- 粗体、斜体
- 代码块（语法高亮）
- 行内代码
- 链接

### 6.2 安全考虑

- 使用 DOMPurify 净化 HTML 输出
- 防止 XSS 攻击

---

## 七、文件结构

### 前端文件

```
frontEnd/src/components/ChatList/
├── chat.vue      # 主组件
└── message.vue   # 消息气泡组件（含 Markdown 渲染）

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
│           └── chat.py                 # 流式聊天 Handler
└── tools/
    └── migrate/
        └── 7_chat_message.py          # 数据库迁移
```

---

## 八、Session 管理

### 8.1 设备级 Session 方案

```
session_id = UUID（首次聊天时生成）
- 存储在浏览器 localStorage
- 每个浏览器设备独立会话
- 换设备登录 = 新会话
- 登出再登录 = 同一设备 session 保持
```

### 8.2 Session 流程

| 场景 | 处理方式 |
|------|----------|
| 首次使用 | 前端生成 UUID 作为 sessionId，发送到后端 |
| 页面刷新 | 读取 localStorage 中的 sessionId，继续同一会话 |
| 用户登出 | Session 保留在数据库 |
| 用户换设备 | 生成新的 sessionId |
| 清空对话 | 仅删除该 sessionId 的消息 |

---

## 九、后端架构

### 9.1 技术选型

| 组件 | 方案 | 说明 |
|------|------|------|
| 通信协议 | SSE (Server-Sent Events) | 轻量、单向流 |
| 前端接收 | Fetch API + ReadableStream | 原生支持，无依赖 |
| OpenAI SDK | `openai` Python 包 | 支持流式 `stream=True` |

### 9.2 流式响应流程

```
前端                          后端 (yeab)                      OpenAI
  │                              │                                │
  │  POST /chat/send             │                                │
  │─────────────────────────────>│                                │
  │                              │  stream=True                   │
  │                              │───────────────────────────────>│
  │                              │                                │
  │  SSE 流响应                   │<──────────────────────────────│
  │<─────────────────────────────│   chunk: "你好"                 │
  │   event: chunk               │                                │
  │   data: {"content":"你"}     │                                │
  │                              │                                │
  │  SSE 流响应                   │<──────────────────────────────│
  │<─────────────────────────────│   chunk: "好呀"                │
  │   event: chunk               │                                │
  │   data: {"content":"你好呀"} │                                │
  │                              │                                │
  │  SSE 流响应 (done)            │                                │
  │<─────────────────────────────│                                │
  │   event: done               │                                │
```

---

## 十、API 接口设计

### 10.1 发送消息（流式）

```
POST /chat/send
Content-Type: application/json

Request:
{
  "userId": 1,
  "content": "你好",
  "sessionId": "abc-123-uuid"  // 可选，默认使用 userId
}

Response: SSE 流
event: chunk
data: {"content": "你好呀"}

event: done
data: {}
```

### 10.2 获取历史

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

### 10.3 清空会话

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

## 十一、数据库设计

### 11.1 表结构

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

### 11.2 新增字段描述

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

## 十二、代码设计

### 12.1 @stream 装饰器 (lib/yeab/web.py)

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

### 12.2 配置 (conf/dev.py)

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

### 12.3 流式 Handler (www/handlers/chat/chat.py)

```python
@post("/chat/send")
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
    history = await ChatMessage.find_by_session(
        user_id, session_id, conf.OPENAI_MAX_HISTORY
    )
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": content})

    # 保存用户消息
    user_msg = ChatMessage(user_id=user_id, session_id=session_id,
                           role='user', content=content)
    yield from user_msg.save()

    # 调用 AI 流式 API
    full_content = ""
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

## 十三、实施步骤

| 顺序 | 任务 | 状态 | 文件 |
|------|------|------|------|
| 1 | 添加 `openai` 到 requirements.txt | ✅ | `yail/requeriment.txt` |
| 2 | 新增字段描述 | ✅ | `www/dao/field_desc.py` |
| 3 | 创建 DAO 模型 | ✅ | `www/dao/chat_message.py` |
| 4 | 创建数据库迁移 | ✅ | `tools/migrate/7_chat_message.py` |
| 5 | 运行迁移创建表 | ⏳ | `python tools/migrate/7_chat_message.py` |
| 6 | 添加 `@stream` 装饰器 | ✅ | `lib/yeab/web.py` |
| 7 | 添加 OpenAI 配置 | ✅ | `conf/dev.py` |
| 8 | 创建流式 Handler | ✅ | `www/handlers/chat/chat.py` |
| 9 | 前端 Session 管理 + 流式接收 | ✅ | `frontEnd/src/store/index.js` |
| 10 | 安装 Python 依赖 | ⏳ | `pip install openai aiomysql` |
| 11 | 配置 API Key | ⏳ | `conf/dev.py` 中修改 OPENAI_API_KEY |
| 12 | 联调测试 | ⏳ | - |

---

## 十四、已完成的工作

### 前端 ✅

| 文件 | 说明 |
|------|------|
| `frontEnd/src/components/ChatList/chat.vue` | 主聊天组件（流式接收） |
| `frontEnd/src/components/ChatList/message.vue` | 消息气泡组件（Markdown 渲染） |
| `frontEnd/src/components/rightSide.vue` | 引入 Chat |
| `frontEnd/src/store/index.js` | 新增 `getChatSessionId`, `getChatHistory`, `clearChatSession`, `sendChatMessageStream` |
| `frontEnd/package.json` | 已添加 marked, dompurify, highlight.js |

### 后端 ✅

| 文件 | 说明 |
|------|------|
| `yail/requeriment.txt` | 已添加 openai>=1.0.0 |
| `yail/www/dao/field_desc.py` | 已添加 SessionIdField, RoleField |
| `yail/www/dao/chat_message.py` | 消息 DAO，含 find_by_session, delete_by_session |
| `yail/tools/migrate/7_chat_message.py` | 数据库迁移脚本 |
| `yail/lib/yeab/web.py` | 已添加 @stream 装饰器 |
| `yail/conf/dev.py` | 已添加 OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_HISTORY |
| `yail/www/handlers/chat/chat.py` | 流式 Handler |
| `yail/www/handlers/chat/__init__.py` | 包标识文件 |

---

## 十五、部署说明

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
