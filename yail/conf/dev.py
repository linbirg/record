import os
from pathlib import Path

ROOT = 'D:/project/linbirg/ww/ww/record/yail'
PIC_DIR = 'D:/project/linbirg/ww/ww/record/frontEnd/static/car'
PIC_URL = 'static/car'

OPENAI_API_KEY = 'your-api-key'
OPENAI_BASE_URL = 'https://api.minimax.chat/v1'
OPENAI_MODEL = 'MiniMax-M2.7'
OPENAI_MAX_HISTORY = 20

# === AI Chat 上下文管理配置 ===

# 聊天会话目录
CHAT_SESSIONS_DIR = Path(os.path.expanduser('~')) / '.chat_sessions'

# === Layer 1: Tool Result Budget ===
TOOL_RESULT_BUDGET_ENABLED = True
TOOL_RESULT_BUDGET_MAX_CHARS = 2000
TOOL_RESULT_BUDGET_MIN_PREVIEW = 500
TOOL_RESULT_BUDGET_REPLACE_TEXT = "[工具结果已裁剪]"

# === Layer 2: Microcompact ===
MICROCOMPACT_ENABLED = True
MICROCOMPACT_TOOLS = {'Read', 'Bash', 'Grep', 'Glob'}
MICROCOMPACT_STUB = "[早期工具调用已压缩]"

# === Layer 5: Auto Summarization ===
SUMMARIZE_TRIGGER_COUNT = 20
SUMMARIZE_TRIGGER_TOKENS = 8000
SUMMARIZE_TRIGGER_DELTA = 3000
SUMMARIZE_TRIGGER_NO_TOOL_ROUNDS = 2
SUMMARIZE_DEBOUNCE_SECONDS = 300
SUMMARIZE_KEEP_MESSAGES = 10
SUMMARIZE_SUMMARY_RESERVE = 2000

# === Prompt Cache 优化 ===
SUMMARIZE_CACHE_ENABLED = True
SUMMARIZE_CACHE_TTL = 3600
TOOL_SCHEMA_REFERENCE = True
TOOL_SCHEMA_CACHE = {}
MESSAGE_DEDUP_ENABLED = True