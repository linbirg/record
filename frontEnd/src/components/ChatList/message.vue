<template>
  <div :class="['message-bubble', isUser ? 'user' : 'ai']">
    <div v-if="!isUser && hasReasoning" class="reasoning-wrapper">
      <div class="reasoning-toggle" @click="toggleReasoning">
        <span class="toggle-icon">{{ isReasoningExpanded ? '▼' : '▶' }}</span>
        <span class="toggle-text">{{ isReasoningExpanded ? '收起思考过程' : '展开思考过程' }}</span>
      </div>
      <div v-show="isReasoningExpanded" class="reasoning-content" v-html="renderedReasoning"></div>
    </div>
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
  data() {
    return {
      isReasoningExpanded: false
    }
  },
  computed: {
    hasReasoning() {
      return this.message.reasoning_content && this.message.reasoning_content.length > 0
    },
    renderedContent() {
      if (this.isUser) {
        return DOMPurify.sanitize(this.escapeHtml(this.message.content))
      }
      if (!this.message.content) return ''
      const html = marked.parse(this.message.content)
      return DOMPurify.sanitize(html)
    },
    renderedReasoning() {
      if (!this.message.reasoning_content) return ''
      return DOMPurify.sanitize(this.escapeHtml(this.message.reasoning_content))
    }
  },
  watch: {
    'message.reasoning_content': {
      handler(newVal) {
        if (newVal && newVal.length > 0) {
          this.isReasoningExpanded = true
        }
      },
      immediate: true
    },
    'message.content': {
      handler() {
        this.$forceUpdate()
      }
    }
  },
  methods: {
    toggleReasoning() {
      this.isReasoningExpanded = !this.isReasoningExpanded
    },
    escapeHtml(text) {
      if (!text) return ''
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
// Webflow Design System Colors
$near-black: #080808;
$webflow-blue: #146ef5;
$blue-400: #3b89ff;
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

// Light shadow for user bubble
$shadow-light: 0px 2px 8px rgba(0, 0, 0, 0.08);

.message-bubble {
  display: flex;
  flex-direction: column;
  max-width: 75%;
  
  &.user {
    align-self: flex-end;
    align-items: flex-end;
    
    .bubble {
      background: $webflow-blue;
      color: $white;
      border-radius: 4px;
      box-shadow: $shadow-light;
    }
    
    .time {
      margin-right: 8px;
      margin-top: 4px;
      color: $gray-300;
      font-size: 12px;
      font-weight: 400;
    }
  }
  
  &.ai {
    align-self: flex-start;
    align-items: flex-start;
    
    .reasoning-wrapper {
      width: 100%;
      margin-bottom: 8px;
    }
    
    .reasoning-toggle {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      font-size: 12px;
      color: $gray-300;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.2s ease;
      user-select: none;
      
      &:hover {
        color: $webflow-blue;
        background: rgba($webflow-blue, 0.05);
      }
      
      .toggle-icon {
        font-size: 10px;
      }
      
      .toggle-text {
        font-weight: 400;
      }
    }
    
    .reasoning-content {
      background: $gray-50;
      border: 1px solid $border-gray;
      border-radius: 4px;
      padding: 8px 12px;
      font-size: 12px;
      color: $gray-800;
      line-height: 1.5;
      margin-top: 4px;
    }
    
    .bubble {
      background: $white;
      color: $near-black;
      border: 1px solid $border-gray;
      border-radius: 4px;
      box-shadow: $shadow-5layer;
      
      ::v-deep {
        code {
          background: $gray-50;
          padding: 2px 6px;
          border-radius: 4px;
          font-family: Consolas, Monaco, monospace;
          font-size: 13px;
          font-weight: 400;
        }
        
        pre {
          background: $gray-50;
          padding: 12px;
          border-radius: 4px;
          overflow-x: auto;
          margin: 8px 0;
          border: 1px solid $border-gray;
          
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
          color: $webflow-blue;
        }
      }
    }
    
    .time {
      margin-left: 8px;
      margin-top: 4px;
      color: $gray-300;
      font-size: 12px;
      font-weight: 400;
    }
  }
  
  .bubble {
    padding: 12px 16px;
    line-height: 1.5;
    font-size: 14px;
    font-weight: 400;
    word-break: break-all;
  }
}
</style>
