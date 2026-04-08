# AI Chat Webflow Style Design

## 一、设计原则

基于 Webflow 设计系统的 AI Chat 对话界面重构方案。

| 原则 | 说明 |
|------|------|
| 白色画布 | `#ffffff` 背景，近黑文字 `#080808` |
| Webflow Blue | `#146ef5` 作为主品牌色和交互色 |
| 锐利圆角 | 4px-8px，不超过 8px |
| 5层阴影 | 级联阴影系统保留 |
| translate(6px) | 按钮悬停动效 |
| Uppercase 标签 | 12px-15px, weight 500-600 |

---

## 二、配色方案

### Primary
```scss
$near-black: #080808;        // 主文字
$webflow-blue: #146ef5;      // 主品牌色
$blue-400: #3b89ff;          // 浅蓝交互
$blue-hover: #0055d4;        // 按钮悬停蓝
```

### Neutral
```scss
$gray-800: #222222;          // 次要文字
$gray-300: #ababab;          // 占位符/禁用
$border-gray: #d8d8d8;       // 边框
$border-hover: #898989;      // 悬停边框
```

### Background
```scss
$white: #ffffff;
$gray-50: #f5f5f5;            // 输入框背景
```

### 5层阴影系统
```scss
$shadow-5layer: 
  0px 84px 24px rgba(0,0,0,0),
  0px 54px 22px rgba(0,0,0,0.01),
  0px 30px 18px rgba(0,0,0,0.04),
  0px 13px 13px rgba(0,0,0,0.08),
  0px 3px 7px rgba(0,0,0,0.09);
```

---

## 三、组件样式

### 3.1 ChatHeader

```
高度: 32px (更紧凑)
背景: #ffffff
边框: 底部 1px solid #d8d8d8
阴影: 无

左侧:
  - ALOHA 文字 (12px, uppercase, letter-spacing 1.5px, weight 550, #080808)

右侧:
  - 删除按钮 (el-icon-delete)
  - 悬停: transform translate(6px), 颜色变 #146ef5
```

### 3.2 消息气泡 - 用户消息

```
背景: #146ef5 (Webflow Blue)
文字: #ffffff
圆角: 4px
阴影: 轻量单层阴影
最大宽度: 75%
内边距: 12px 16px
```

### 3.3 消息气泡 - AI 消息

```
背景: #ffffff
文字: #080808
边框: 1px solid #d8d8d8
圆角: 4px
阴影: 5层阴影系统
最大宽度: 75%
内边距: 12px 16px
```

### 3.4 输入框

```
背景: #f5f5f5 (灰色底) → 聚焦时 #ffffff (白底)
边框: 1px solid #d8d8d8
圆角: 4px
聚焦边框: #146ef5
内边距: 10px 12px
字体: 14px, weight 400-500, #080808
占位符: #ababab
```

### 3.5 拖动条

```
高度: 4px
背景: 渐变灰 (#d8d8d8 → transparent)
圆角: 2px
悬停: 颜色加深
```

### 3.6 欢迎语气泡

```
背景: #ffffff
边框: 1px solid #d8d8d8
圆角: 4px
阴影: 5层阴影
文字: #ababab (居中)
```

---

## 四、交互动效

| 元素 | 动效 |
|------|------|
| 删除按钮 | `transform: translate(6px)` + 颜色 `#146ef5` |
| 输入框聚焦 | 边框颜色 `#146ef5` |
| 消息气泡 | 5层阴影系统 |

---

## 五、Typography

| 元素 | 大小 | 粗细 | 字间距 |
|------|------|------|--------|
| Header 标题 | 12px | 550 | 1.5px |
| 消息正文 | 14px | 400-500 | normal |
| 时间戳 | 12px | 400 | normal |
| 占位符 | 14px | 400 | normal |

---

## 六、实施文件

| 文件 | 改动内容 |
|------|----------|
| `frontEnd/src/components/ChatList/chat.vue` | Header 32px 白底、输入框 Webflow 样式、变量定义 |
| `frontEnd/src/components/ChatList/message.vue` | 气泡 4px 圆角、5层阴影、#146ef5 蓝色 |

---

## 七、与原 AI Chat 设计的关系

本文档基于 [[../record/ai_chat_design|AI Chat 设计]] 的功能需求，融入 Webflow 设计系统风格进行视觉升级。

- 功能逻辑保持不变
- 样式全面采用 Webflow 色系和阴影系统
- 交互动效参考 Webflow 规范
