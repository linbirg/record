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
| **序号（默认）** | 证件01、证件02、证件03、证件04、证件05 |
| **预设下拉** | 行驶证、驾驶证、关系证明 |
| **自定义** | 用户手动输入 |

### 2.3 交互流程

```
[证件弹窗]
    │
    ├─ 无证件 ──────────────────────────┐
    │  显示"暂无证件图片"                  │
    │  + 上传区域（证件名称选择 + 选择文件）│
    │  → 选文件 → 选择证件名称 → 上传成功 │
    │
    └─ 有证件 ──────────────────────────┐
       显示证件网格                        │
       + "添加证件"按钮                   │
       → 点击显示上传区域                 │
       → 选文件 → 选择证件名称 → 上传成功 │
```

### 2.4 组件改动

**CarList.vue 证件弹窗：**
- 替换跳转按钮为 el-upload + 证件名称选择器
- 有证件时底部添加"添加证件"按钮
- 新增 `showUploadSection` 控制上传区域显示/隐藏

**后端接口 `car/pic/upload`：**
- 支持接收 `filename` 参数指定文件名
- 使用 `{name}_{date}_{docName}.jpg` 格式

## 3. 实现详情

### 3.1 前端数据

```javascript
data() {
  return {
    docName: "证件01",           // 当前选择的证件名称
    customDocName: "",           // 自定义证件名称
    showUploadSection: false,    // 控制上传区域显示
    docOptions: [                // 证件名称选项
      { label: "证件01", value: "证件01" },
      { label: "证件02", value: "证件02" },
      { label: "证件03", value: "证件03" },
      { label: "证件04", value: "证件04" },
      { label: "证件05", value: "证件05" },
      { label: "行驶证", value: "行驶证" },
      { label: "驾驶证", value: "驾驶证" },
      { label: "关系证明", value: "关系证明" },
    ],
  }
}
```

### 3.2 关键方法

```javascript
getDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}${month}${day}`;
},

generateFileName() {
  const docName = this.docName === "custom" ? this.customDocName : this.docName;
  return `${this.currentCar.name}_${this.getDateString()}_${docName}.jpg`;
},

handleUploadFile(item) {
  const file = item.file;
  const fileName = this.generateFileName();
  const formData = new FormData();
  formData.append("file", file);
  formData.append("no", this.currentCar.no);
  formData.append("filename", fileName);

  this.post({ url: "car/pic/upload", data: formData })
    .then(() => {
      this.$message.success("上传成功");
      this.docName = "证件01";
      this.customDocName = "";
      this.loadDocImages(this.currentCar.no);
    })
    .catch(() => {
      this.$message.error("上传失败");
    });
}
```

### 3.3 后端改动

**文件：** `yail/www/handlers/car/index.py:180`

```python
# 改动前
name = formData.file.filename

# 改动后
name = formData.filename if formData.filename else formData.file.filename
```

## 4. UI 样式

遵循 webflow/DESIGN.md 规范：
- 主色：#146ef5 (Webflow Blue)
- 边框：1px solid #d8d8d8
- 圆角：4px-8px
- 字号：14px-16px

### 证件弹窗样式

```scss
.doc-upload-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.doc-upload-header {
  margin-bottom: 12px;
}

.doc-upload-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-name-selector {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;

  .doc-name-label {
    font-size: 14px;
    color: #374151;
  }
}
```

## 5. 状态处理

| 状态 | 显示 |
|------|------|
| 无证件 | 占位文字 + 上传区域（始终显示） |
| 有证件 | 证件网格 + "添加证件"按钮 |
| 点击添加 | 显示上传区域 |
| 上传成功 | 刷新图片列表，重置表单 |
| 上传失败 | $message.error 提示 |

## 6. 提交记录

- Commit: `3ca3fd2` - feat: 实现CarList证件弹窗上传功能
