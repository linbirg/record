# 车辆列表批量导入 Word 功能设计

## 概述

在车辆列表页面增加「批量导入」按钮，用户可选择 Word 文档（.docx）导入车辆信息。

## Word 表格结构

- 第一行：表头（序号、办理日期、所属单位、姓名、联系电话、车牌号、停车证...）
- 数据行：从第二行开始，每行一辆车
- **仅提取姓名列和车牌号列**

## 数据流程

```
用户选择 .docx 文件 
  → 上传到 /car/import_word 接口 
  → 后端 python-docx 解析表格 
  → 逐条调用现有 /car/add 接口添加 
  → 返回导入结果（成功/失败数量）
  → 前端刷新列表
```

## 前端改动

| 位置 | 改动 |
|------|------|
| CarList.vue | 新增「批量导入」按钮 |
| 新增组件 | ImportWordDialog.vue（上传 + 进度 + 结果展示） |

### ImportWordDialog.vue 交互流程

1. 用户点击「批量导入」按钮
2. 弹出 el-dialog，包含：
   - el-upload 组件（accept=".docx"）
   - 上传后显示文件名
3. 用户确认导入
4. 显示 loading 进度条
5. 导入完成后显示结果：
   - 成功数量
   - 失败数量（如有）
6. 关闭弹窗，刷新列表

## 后端改动

| 位置 | 改动 |
|------|------|
| handlers/car/index.py | 新增 `/car/import_word` 接口 |
| 依赖 | pip install python-docx |

### /car/import_word 接口

**请求：**
- Content-Type: multipart/form-data
- 参数：file (Word 文档)

**响应：**
```json
{
  "success": true,
  "total": 10,
  "added": 9,
  "failed": 1,
  "errors": [
    {"row": 3, "message": "车牌号格式错误"}
  ]
}
```

### 解析逻辑

1. 使用 python-docx 读取 .docx 文件
2. 获取第一个表格
3. 第一行作为表头，查找「姓名」和「车牌号」列索引
4. 遍历数据行，提取对应列的值
5. 调用 `/car/add` 接口逐条添加

## 错误处理

| 错误情况 | 处理 |
|----------|------|
| 文件格式非 .docx | 返回错误"请选择 Word 文档" |
| 文档无表格或表格无数据 | 返回错误"文档中没有找到车辆数据" |
| 单元格为空 | 跳过该行，记录为失败 |
| 车牌号格式错误 | 跳过该行，记录到 errors |

## 界面设计（遵循 webflow 规范）

- 主色调：#146ef5
- 按钮样式：与现有「添加车辆」按钮一致（蓝色背景，白色文字）
- 弹窗：el-dialog，居中显示，宽度 500px
- 进度条：el-progress
- 结果展示：el-result 或自定义卡片样式

## 依赖安装

```bash
pip install python-docx
```

## 实施步骤

1. 后端：安装 python-docx
2. 后端：新增 /car/import_word 接口
3. 前端：新增 ImportWordDialog.vue 组件
4. 前端：在 CarList.vue 集成「批量导入」按钮和弹窗
5. 测试：验证导入功能正常
