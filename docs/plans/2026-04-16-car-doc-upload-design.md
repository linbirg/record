# 车辆证件上传功能设计

## 1. 需求背景

CarList 证件弹窗中：
- 无证件时：只有"上传证件"跳转按钮，未实现功能
- 有证件时：只能查看，无法继续添加

## 2. 设计方案

### 2.1 命名规则

```
{车主姓名}_{YYYYMMDD}_{证件名称}.jpg
例：张三_20260416_证件01.jpg
例：李四_20260416_行驶证.jpg
```

### 2.2 证件名称

| 模式 | 选项 |
|------|------|
| **序号（默认）** | 证件01、证件02、证件03... |
| **预设下拉** | 行驶证、驾驶证、关系证明 |
| **自定义** | 用户手动输入 |

### 2.3 交互流程

```
[证件弹窗]
    │
    ├─ 无证件 ──────────────────────────┐
    │  显示"暂无证件图片"                  │
    │  + el-upload 点击上传              │
    │  → 选文件 → 选择证件名称 → 上传成功 │
    │
    └─ 有证件 ──────────────────────────┐
       显示证件网格                        │
       + 底部"添加证件"按钮               │
       → 选文件 → 选择证件名称 → 上传成功 │
```

### 2.4 组件改动

**CarList.vue 证件弹窗：**
- 替换跳转按钮为 el-upload 组件
- 有证件时底部添加"添加证件"按钮
- 新增证件名称选择器（序号/预设/自定义）

**后端接口 `car/pic/upload`：**
- 支持接收 `filename` 参数指定文件名
- 使用 `{name}_{date}_{docName}.jpg` 格式

## 3. 前端实现

### 3.1 证件名称选择器

```vue
<el-select v-model="docName" placeholder="选择证件名称">
  <el-option-group label="序号">
    <el-option label="证件01" value="证件01" />
    <el-option label="证件02" value="证件02" />
  </el-option-group>
  <el-option-group label="预设">
    <el-option label="行驶证" value="行驶证" />
    <el-option label="驾驶证" value="驾驶证" />
    <el-option label="关系证明" value="关系证明" />
  </el-option-group>
  <el-option-group label="自定义">
    <el-option label="自定义输入" value="custom">
      <el-input v-model="customDocName" size="small" placeholder="请输入" />
    </el-option>
  </el-option-group>
</el-select>
```

### 3.2 文件命名函数

```javascript
generateFileName(name, docName) {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  return `${name}_${date}_${docName}.jpg`;
}
```

## 4. 后端改动

### 4.1 接口 `car/pic/upload`

**当前问题：** 直接使用原始文件名

**改动方案：** 接收 `filename` 参数

```python
@post("/car/pic/upload")
async def upload(no, filename=None):
    if filename is None:
        filename = formData.file.filename
    # 使用传入的文件名保存
```

## 5. UI 样式

遵循 webflow/DESIGN.md 规范：
- 主色：#146ef5 (Webflow Blue)
- 边框：1px solid #d8d8d8
- 圆角：4px-8px
- 字号：14px-16px

## 6. 状态处理

| 状态 | 显示 |
|------|------|
| 无证件 | 占位文字 + 上传按钮 |
| 加载中 | el-upload loading 状态 |
| 上传成功 | 刷新图片列表 |
| 上传失败 | $message.error 提示 |
