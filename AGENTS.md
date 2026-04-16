# AGENTS.md

## Repository Structure

- `frontEnd/` - Vue 2 frontend (webpack 3, element-ui)
- `yail/` - Python backend using custom `yeab` framework (aiohttp-based)

## Backend (yail/)

### Run
```bash
python app.py  # Entry point at yail/app.py
```

### Key Paths
- `PIC_DIR` (raw image path): `frontEnd/static/car` - uploaded car images stored here
- `PIC_URL`: `static/car`

### Frameworks
- Custom `yeab` framework in `lib/yeab/`
- `yom` async ORM in `lib/yom.py` (aiomysql-based)
- Auto-reload via `pymonitor.py` (watchdog-based)

### Migrations
```bash
python tools/migrate/rake_migrate.py  # 旧迁移方式
python tools/migrate/7_chat_message.py  # Chat 消息表迁移
```

### Chat Module
- **Handler**: `www/handlers/chat/chat.py`
- **DAO**: `www/dao/chat_message.py`
- **Config**: `conf/dev.py` 中的 `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_MAX_HISTORY`
- **API**: `/chat/send` (SSE流式), `/chat/history`, `/chat/clear`

## Frontend (frontEnd/)

```bash
npm run dev     # dev server
npm run build   # production build
npm run unit    # jest unit tests
```

### Chat UI
- `src/components/ChatList/chat.vue` - 主聊天组件
- `src/components/ChatList/message.vue` - 消息气泡组件
- Session 管理: UUID 存储在 localStorage

## Notes

- Backend CORS uses middleware; Vue axios must set `withCredentials: true`
- `yeab` uses annotation-based routing similar to Spring MVC with auto-scanning
- `@stream` decorator for SSE streaming responses
- `@ResponseBody` decorator for JSON responses

## AI 行为准则（karpathy-guidelines）

### 1. Think Before Coding
- **不问清楚不动手**：假设要显式声明，不确定就问
- **多种理解列出选项**：不要自己偷偷挑一个
- **更简单的方案要说**：如果当前方案过于复杂
- **不清楚就停**：说清楚哪里不清楚，然后问

### 2. Simplicity First
- **不加未要求的功能**
- **不为单次使用做抽象**
- **不加没用到的配置**
- **能 50 行解决就不要写 100 行**

### 3. Surgical Changes
- **只改相关的**：每行改动溯源到用户需求
- **不顺手优化**：不主动改无关代码风格/格式
- **只清理自己产生的孤儿**：自己改动导致的无用 import 要删
- **不删既有死代码**：除非明确要求

### 4. Goal-Driven Execution
- **多步骤任务先列计划**：
  ```
  1. [步骤] → 验证：[如何确认做对了]
  2. [步骤] → 验证：[如何确认做对了]
  ```
- **改 bug 前先写测试**：先复现，再修复
- **加功能前定验收标准**：明确"什么算做对了"
