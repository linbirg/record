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
        v-for="msg in messages"
        :key="msg.id"
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
import Vue from 'vue'
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
      startHeight: 0,
      msgIdCounter: Date.now()
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
        id: this.msgIdCounter++,
        role: 'user',
        content: content,
        createdAt: new Date().toISOString()
      }
      this.messages.push(userMessage)
      this.scrollToBottom()
      
      this.loading = true
      
      this.messages.push({
        id: this.msgIdCounter++,
        role: 'assistant',
        content: '',
        reasoning_content: '',
        createdAt: new Date().toISOString()
      })
      
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
        onDone: () => {
          this.loading = false
        },
        onError: (error) => {
          this.loading = false
          const lastMsg = this.messages[this.messages.length - 1]
          lastMsg.content = '抱歉，发生了错误：' + error
          lastMsg.reasoning_content = ''
          this.$forceUpdate()
          this.scrollToBottom()
        }
      })
    },
    async loadHistory() {
      try {
        const history = await this.$store.dispatch('getChatHistory')
        if (history && history.length > 0) {
          this.messages = history.map((msg, idx) => ({
            id: this.msgIdCounter + idx,
            role: msg.role,
            content: msg.content,
            createdAt: msg.createdAt
          }))
          this.msgIdCounter += history.length
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
// Webflow Design System Colors
$near-black: #080808;
$webflow-blue: #146ef5;
$blue-400: #3b89ff;
$blue-hover: #0055d4;
$gray-800: #222222;
$gray-300: #ababab;
$border-gray: #d8d8d8;
$white: #ffffff;
$gray-50: #f5f5f5;

// 5-layer shadow system
$shadow-5layer: 
  0px 84px 24px rgba(0,0,0,0),
  0px 54px 22px rgba(0,0,0,0.01),
  0px 30px 18px rgba(0,0,0,0.04),
  0px 13px 13px rgba(0,0,0,0.08),
  0px 3px 7px rgba(0,0,0,0.09);

.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: $white;
  
  .chat-header {
    height: 32px;
    background: $white;
    border-bottom: 1px solid $border-gray;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .logo {
      font-size: 14px;
    }
    
    .title {
      color: $near-black;
      font-size: 12px;
      font-weight: 550;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }
    
    .el-icon-delete {
      color: $gray-300;
      cursor: pointer;
      font-size: 14px;
      padding: 4px 8px;
      border-radius: 4px;
      transition: all 0.2s ease;
      
      &:hover {
        color: $webflow-blue;
        transform: translate(6px);
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
    background: $gray-50;
    
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: $border-gray;
      border-radius: 2px;
    }
    
    .welcome {
      text-align: center;
      color: $gray-300;
      padding: 40px 20px;
      font-size: 14px;
      
      p {
        background: $white;
        display: inline-block;
        padding: 16px 24px;
        border-radius: 4px;
        border: 1px solid $border-gray;
        box-shadow: $shadow-5layer;
      }
    }
    
    .loading {
      display: flex;
      justify-content: center;
      padding: 12px;
      
      .dot {
        width: 8px;
        height: 8px;
        background: $gray-300;
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
    background: $white;
    border-top: 1px solid $border-gray;
    padding: 8px 10px 10px;
    cursor: ns-resize;
    user-select: none;
    display: flex;
    flex-direction: column;
    
    &.dragging {
      background: $gray-50;
    }
    
    .resize-handle {
      height: 4px;
      margin-bottom: 6px;
      background: linear-gradient(90deg, transparent 0%, $border-gray 20%, $border-gray 80%, transparent 100%);
      border-radius: 2px;
      cursor: ns-resize;
      transition: background 0.2s ease;
      
      &:hover {
        background: linear-gradient(90deg, transparent 0%, $gray-300 20%, $gray-300 80%, transparent 100%);
      }
    }
    
    textarea {
      width: 100%;
      height: 100%;
      border: 1px solid $border-gray;
      outline: none;
      resize: none;
      padding: 10px 12px;
      font-size: 14px;
      font-weight: 400;
      font-family: inherit;
      line-height: 1.5;
      box-sizing: border-box;
      background: $gray-50;
      color: $near-black;
      border-radius: 4px;
      transition: all 0.2s ease;
      
      &:focus {
        background: $white;
        border-color: $webflow-blue;
      }
      
      &::placeholder {
        color: $gray-300;
      }
      
      &:disabled {
        background: $gray-50;
        cursor: not-allowed;
        color: $gray-300;
      }
    }
  }
}
</style>
