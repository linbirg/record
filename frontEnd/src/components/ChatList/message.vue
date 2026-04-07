<template>
  <div :class="['message-bubble', isUser ? 'user' : 'ai']">
    <div class="bubble" v-html="renderedContent"></div>
    <span class="time">{{ formatTime(message.createdAt) }}</span>
  </div>
</template>

<script>
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (e) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

export default {
  name: 'ChatMessage',
  props: {
    message: {
      type: Object,
      required: true
    },
    isUser: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    renderedContent() {
      if (this.isUser) {
        return DOMPurify.sanitize(this.escapeHtml(this.message.content))
      }
      const html = marked.parse(this.message.content)
      return DOMPurify.sanitize(html)
    }
  },
  methods: {
    escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      const pad = n => n < 10 ? '0' + n : n
      return `${pad(date.getHours())}:${pad(date.getMinutes())}`
    }
  }
}
</script>

<style lang="scss" scoped>
.message-bubble {
  display: flex;
  flex-direction: column;
  max-width: 75%;
  
  &.user {
    align-self: flex-end;
    align-items: flex-end;
    
    .bubble {
      background: #50a2f2;
      color: #fff;
      border-radius: 8px 8px 0 8px;
    }
    
    .time {
      margin-right: 8px;
      margin-top: 4px;
    }
  }
  
  &.ai {
    align-self: flex-start;
    align-items: flex-start;
    
    .bubble {
      background: #fff;
      color: #333;
      border-radius: 8px 8px 8px 0;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
      
      ::v-deep {
        code {
          background: #f0f0f0;
          padding: 2px 6px;
          border-radius: 4px;
          font-family: Consolas, Monaco, monospace;
          font-size: 13px;
        }
        
        pre {
          background: #f6f8fa;
          padding: 12px;
          border-radius: 6px;
          overflow-x: auto;
          margin: 8px 0;
          
          code {
            background: none;
            padding: 0;
          }
        }
        
        p {
          margin: 0;
          line-height: 1.5;
        }
        
        p + p {
          margin-top: 8px;
        }
        
        ul, ol {
          margin: 8px 0;
          padding-left: 20px;
        }
        
        a {
          color: #50a2f2;
        }
      }
    }
    
    .time {
      margin-left: 8px;
      margin-top: 4px;
    }
  }
  
  .bubble {
    padding: 12px 16px;
    line-height: 1.5;
    font-size: 14px;
    word-break: break-all;
  }
  
  .time {
    font-size: 12px;
    color: #999;
  }
}
</style>
