<template>
  <div class="chat">
    <div class="chat-header">
      <div class="header-left">
        <span class="logo">🤖</span>
        <span class="title">ALOHA</span>
      </div>
      <i class="el-icon-delete" @click="clearChat"></i>
    </div>
    
    <div class="message-list" ref="messageList">
      <div v-if="messages.length === 0" class="welcome">
        <p>👋 Aloha! 我是 ALOHA，有什么可以帮你的？</p>
      </div>
      <message
        v-for="(msg, index) in messages"
        :key="index"
        :message="msg"
        :isUser="msg.role === 'user'"
      />
      <div v-if="loading" class="loading">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
    
    <div class="chat-input"
      @mousedown="startDrag"
      :style="{ height: inputHeight + 'px' }"
      :class="{ dragging: isDragging }">
      <div class="resize-handle"></div>
      <textarea
        ref="inputArea"
        v-model="inputContent"
        @keydown.enter.exact.prevent="sendMessage"
        @keydown.enter.shift.exact="handleShiftEnter"
        placeholder="输入消息，回车发送，Shift+Enter 换行"
        :disabled="loading"
      ></textarea>
    </div>
  </div>
</template>

<script>
import Message from './message'

export default {
  name: 'Chat',
  components: {
    Message
  },
  data() {
    return {
      inputContent: '',
      messages: [],
      loading: false,
      userId: 0,
      inputHeight: 60,
      minHeight: 40,
      maxHeight: 160,
      isDragging: false,
      startY: 0,
      startHeight: 0
    }
  },
  created() {
    this.userId = this.$store.state.userId
    this.loadHistory()
  },
  methods: {
    sendMessage() {
      if (!this.inputContent.trim() || this.loading) return
      
      const content = this.inputContent.trim()
      this.inputContent = ''
      
      const userMessage = {
        role: 'user',
        content: content,
        createdAt: new Date().toISOString()
      }
      this.messages.push(userMessage)
      this.scrollToBottom()
      
      this.loading = true
      
      let aiContent = ''
      const aiMessage = {
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString()
      }
      this.messages.push(aiMessage)
      
      this.$store.dispatch('sendChatMessageStream', {
        content: content,
        onChunk: (chunk) => {
          aiContent = chunk
          aiMessage.content = chunk
          this.scrollToBottom()
        },
        onDone: () => {
          this.loading = false
        },
        onError: (error) => {
          this.loading = false
          aiMessage.content = '抱歉，发生了错误：' + error
          this.scrollToBottom()
        }
      })
    },
    async loadHistory() {
      try {
        const history = await this.$store.dispatch('getChatHistory')
        if (history && history.length > 0) {
          this.messages = history.map(msg => ({
            role: msg.role,
            content: msg.content,
            createdAt: msg.createdAt
          }))
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      }
    },
    handleShiftEnter(e) {
    },
    startDrag(e) {
      if (e.target.tagName === 'TEXTAREA') return
      this.isDragging = true
      this.startY = e.clientY
      this.startHeight = this.inputHeight
      document.addEventListener('mousemove', this.onDrag)
      document.addEventListener('mouseup', this.stopDrag)
    },
    onDrag(e) {
      if (!this.isDragging) return
      const diff = this.startY - e.clientY
      const newHeight = Math.min(Math.max(this.startHeight + diff, this.minHeight), this.maxHeight)
      this.inputHeight = newHeight
    },
    stopDrag() {
      this.isDragging = false
      document.removeEventListener('mousemove', this.onDrag)
      document.removeEventListener('mouseup', this.stopDrag)
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const list = this.$refs.messageList
        if (list) {
          list.scrollTop = list.scrollHeight
        }
      })
    },
    clearChat() {
      this.$confirm('确定要清空对话记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await this.$store.dispatch('clearChatSession')
        } catch (error) {
          console.error('清空会话失败:', error)
        }
        this.messages = []
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f5f5f5;
  
  .chat-header {
    height: 44px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .logo {
      font-size: 18px;
    }
    
    .title {
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      letter-spacing: 2px;
    }
    
    .el-icon-delete {
      color: rgba(255, 255, 255, 0.7);
      cursor: pointer;
      font-size: 16px;
      padding: 4px;
      border-radius: 4px;
      transition: all 0.3s;
      
      &:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
  
  .message-list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #ccc;
      border-radius: 2px;
    }
    
    .welcome {
      text-align: center;
      color: #888;
      padding: 40px 20px;
      font-size: 14px;
      
      p {
        background: #fff;
        display: inline-block;
        padding: 16px 24px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      }
    }
    
    .loading {
      display: flex;
      justify-content: center;
      padding: 12px;
      
      .dot {
        width: 8px;
        height: 8px;
        background: #999;
        border-radius: 50%;
        margin: 0 4px;
        animation: bounce 1.4s infinite ease-in-out both;
        
        &:nth-child(1) {
          animation-delay: -0.32s;
        }
        
        &:nth-child(2) {
          animation-delay: -0.16s;
        }
      }
      
      @keyframes bounce {
        0%, 80%, 100% {
          transform: scale(0);
        }
        40% {
          transform: scale(1);
        }
      }
    }
  }
  
  .chat-input {
    background: #fff;
    border-top: 1px solid #e0e0e0;
    padding: 8px 10px 10px;
    cursor: ns-resize;
    user-select: none;
    display: flex;
    flex-direction: column;
    
    &.dragging {
      background: #f0f0f0;
    }
    
    .resize-handle {
      height: 4px;
      margin-bottom: 6px;
      background: linear-gradient(90deg, transparent 0%, #ddd 20%, #ddd 80%, transparent 100%);
      border-radius: 2px;
      cursor: ns-resize;
      
      &:hover {
        background: linear-gradient(90deg, transparent 0%, #ccc 20%, #ccc 80%, transparent 100%);
      }
    }
    
    textarea {
      width: 100%;
      height: 100%;
      border: none;
      outline: none;
      resize: none;
      padding: 10px;
      font-size: 14px;
      font-family: inherit;
      line-height: 1.5;
      box-sizing: border-box;
      background: #f5f5f5;
      border-radius: 4px;
      
      &:focus {
        background: #fff;
        box-shadow: 0 0 0 1px #50a2f2;
      }
      
      &:disabled {
        background: #f0f0f0;
        cursor: not-allowed;
      }
    }
  }
}
</style>
