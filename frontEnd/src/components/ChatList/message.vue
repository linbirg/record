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
