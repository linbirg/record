---
title: AI Chat Webflow 风格设计
type: concept
tags: [ui, webflow, design, chat]
created: 2026-04-08
updated: 2026-04-08
sources: [sources/design/ai-chat-webflow/SKILL.md]
summary: 基于 Webflow 设计系统的 AI Chat 界面视觉升级方案
---

## 摘要

将 AI Chat 对话界面从当前渐变风格升级为 Webflow 设计系统风格，采用 `#146ef5` Webflow Blue、5层阴影系统和锐利圆角设计。

---

## 核心设计原则

| 原则 | 说明 |
|------|------|
| 白色画布 | `#ffffff` 背景，近黑文字 `#080808` |
| Webflow Blue | `#146ef5` 作为主品牌色和交互色 |
| 锐利圆角 | 4px，不超过 8px |
| 5层阴影 | 级联阴影系统 |
| translate(6px) | 按钮悬停动效 |

---

## 配色方案

### Primary Colors
- **Near Black** `#080808` - 主文字
- **Webflow Blue** `#146ef5` - 主品牌色
- **Blue 400** `#3b89ff` - 浅蓝交互
- **Blue Hover** `#0055d4` - 按钮悬停

### Neutral Colors
- **Gray 800** `#222222` - 次要文字
- **Gray 300** `#ababab` - 占位符/禁用
- **Border Gray** `#d8d8d8` - 边框

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

## 组件变化

### ChatHeader
- 高度: 44px → 32px
- 背景: 渐变 → 纯白 `#ffffff`
- 底部边框: 添加 1px `#d8d8d8`
- 标题: 12px uppercase, letter-spacing 1.5px, weight 550
- 删除按钮: hover 时 `transform: translate(6px)` + 颜色变 `#146ef5`

### 消息气泡
- 圆角: 8px → 4px
- 用户气泡: `#50a2f2` → `#146ef5`
- AI 气泡: 添加 1px `#d8d8d8` 边框 + 5层阴影

### 输入框
- 边框: 1px `#d8d8d8`
- 聚焦边框: `#50a2f2` → `#146ef5`
- 圆角: 4px

---

## 交互动效

| 元素 | 动效 |
|------|------|
| 删除按钮 | `transform: translate(6px)` + 颜色 `#146ef5` |
| 输入框聚焦 | 边框颜色 `#146ef5` |
| 消息气泡 | 5层阴影系统 |

---

## 相关链接

[[ai-chat-design]] [[ui]] [[webflow]]