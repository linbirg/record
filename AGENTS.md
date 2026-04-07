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
