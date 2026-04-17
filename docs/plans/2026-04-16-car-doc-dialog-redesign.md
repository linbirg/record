# 证件弹窗优化设计

## 1. 需求背景

CarList 证件弹窗存在以下问题：
- 缺少删除功能
- 布局较丑，需要遵循 webflow 设计规范
- "添加证件"按钮显示不美观

## 2. 设计规范（基于 webflow/DESIGN.md）

| 元素 | 规范值 |
|------|--------|
| 主色/CTA | #146ef5 (Webflow Blue) |
| 文字 | #080808 (Near Black) |
| 边框 | #d8d8d8 |
| 按钮悬停 | translate(6px) |
| 卡片 | 1px solid #d8d8d8, 4px-8px radius |
| 阴影 | 5层级联阴影 |
| 悬停动画 | scale(1.05) |

### 颜色规范详情

- **Primary**: #146ef5 (Webflow Blue) - 按钮、CTA
- **Secondary Accents**: #ee1d36 (Red) - 删除按钮
- **Neutral**: #d8d8d8 (Border), #5a5a5a (Link text), #ababab (Muted)

## 3. 功能改动

### 3.1 删除功能

**交互流程：**
1. 用户悬停图片卡片 → 显示红色删除图标（右上角）
2. 点击删除图标 → 弹出自定义确认框
3. 确认删除 → 调用 `car/pic/delete` 接口 → 刷新列表
4. 取消 → 关闭确认框

**确认框设计：**
- 居中弹出，半透明黑色背景
- 显示红色警告图标
- 显示文件名
- 确认/取消按钮

### 3.2 图片卡片样式

```
┌─────────────────┐
│             [×] │  ← 悬停显示红色删除按钮
│                 │
│    [图片]       │
│                 │
└─────────────────┘
```

**样式要点：**
- 1px solid #d8d8d8 边框
- 4px border-radius
- 5层级联阴影
- 悬停时图片 scale(1.05)
- 删除按钮 opacity: 0 → 1

### 3.3 上传区域重新设计

**布局：**
```
┌─────────────────────────────────────┐
│ [证件名称 ▼]  [选择文件]  [取消]    │  ← 始终显示
└─────────────────────────────────────┘
```

**行为：**
- 有证件时：显示在底部，始终可见，添加"取消"按钮
- 无证件时：直接显示，无需点击展开

## 4. 组件结构调整

```
证件弹窗
├── 头部信息 (name - carNo)
├── 图片网格 (doc-images)
│   └── 图片卡片 × N (悬停显示删除按钮)
├── 上传区域 (始终显示)
│   ├── 证件名称选择器
│   ├── 上传按钮
│   └── 取消按钮 (关闭弹窗)
└── 删除确认弹出 (delete-confirm-popup)
    ├── 警告图标
    ├── 确认文字
    ├── 文件名
    └── 确认/取消按钮
```

## 5. 数据结构

### 5.1 新增 data

```javascript
deleteConfirmVisible: false,  // 删除确认弹窗
deleteTargetFile: null,       // 待删除文件
```

### 5.2 新增方法

```javascript
confirmDelete(img)      // 显示删除确认
handleDeleteDoc()       // 执行删除
```

## 6. 样式规范

### 6.1 5层级联阴影

```scss
box-shadow:
  0px 84px 24px rgba(0,0,0,0),
  0px 54px 22px rgba(0,0,0,0.01),
  0px 30px 18px rgba(0,0,0,0.04),
  0px 13px 13px rgba(0,0,0,0.08),
  0px 3px 7px rgba(0,0,0,0.09);
```

### 6.2 删除确认弹窗

```scss
.delete-confirm-popup {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.delete-confirm-content {
  background: white;
  padding: 24px;
  border-radius: 4px;
  min-width: 280px;
  text-align: center;
  box-shadow: 0px 84px 24px rgba(0,0,0,0), ...;
}
```

### 6.3 按钮规范

```scss
.el-button {
  border-radius: 4px;
  font-weight: 500;
  transition: transform 0.2s;

  &:hover {
    transform: translate(6px);
  }
}

.el-button--danger {
  background: #ee1d36;
  border-color: #ee1d36;
}
```

## 7. 涉及文件

| 文件 | 改动 |
|------|------|
| `frontEnd/src/components/Container/car/CarList.vue` | 模板结构调整、样式优化、添加删除功能 |

## 8. 提交记录

- Commit: `xxx` - feat: 优化证件弹窗UI并添加删除功能
