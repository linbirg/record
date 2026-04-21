# 证件上传弹窗交互优化实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 优化 CarList.vue 证件弹窗的上传流程，改為先选择图片再命名，符合操作习惯

---

## Task 1: 修改默认值

**File:** `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 修改 docName 默认值**

```javascript
// data() 中
docName: "驾驶证",  // 从 "关系证明" 改为 "驾驶证"

// docOptions 第一个选项也是 "驾驶证"
docOptions: [
  { label: "驾驶证", value: "驾驶证" },  // 第一个选项
  { label: "关系证明", value: "关系证明" },
  // ... 其他选项
]
```

**Step 2: 提交**

```bash
git add frontEnd/src/components/Container/car/CarList.vue
git commit -m "refactor(car): 证件名称默认值改为驾驶证"
```

---

## Task 2: 修改 el-upload 配置

**File:** `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 修改 el-upload 配置**

在 `doc-upload-section` 区域中：

```vue
<el-upload
  class="doc-uploader"
  action="#"
  :auto-upload="false"  <!-- 改为手动上传 -->
  :on-change="handleUploadFile"  <!-- 使用 on-change 而非 http-request -->
  :show-file-list="false"
  accept="image/jpeg,image/png,image/jpg">
  <el-button type="primary">选择文件</el-button>
</el-upload>
```

**注意：** `el-upload` 的 `:on-change` 回调参数为 `(file, fileList)`，其中 `file.raw` 是实际的 File 对象。不能使用 `:http-request`，因为其参数格式不同。

**Step 2: 修改 handleUploadFile 方法**

```javascript
handleUploadFile(file, fileList) {
  // file.raw 是实际的 File 对象
  this.pendingFile = file.raw;
  this.pendingFileName = file.name;
}
```

**注意：** 不能使用 `http-request`，因为 `on-change` 回调参数格式不同。

**Step 3: 新增确认上传方法**

```javascript
confirmUpload() {
  if (!this.pendingFile) return;
  
  // 构建 FormData 上传
  let fileData = new FormData();
  fileData.append("file", this.pendingFile);
  fileData.append("no", this.currentCar.no);
  
  const docName = this.docName === "custom" ? this.customDocName : this.docName;
  fileData.append("name", docName);  // 如果后端支持命名
  
  // 上传成功后重置状态
  this.post({
    url: "car/pic/upload",
    data: fileData,
  }).then(() => {
    this.pendingFile = null;
    this.pendingFileName = "";
    this.docName = "驾驶证";  // 重置默认值
    this.qryFileList();  // 刷新图片列表
  });
}

cancelUpload() {
  this.pendingFile = null;
  this.pendingFileName = "";
}
```

---

## Task 3: 添加待上传确认区域 UI

**File:** `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 添加 v-show 确认区域**

在 `doc-upload-section` 中：

```vue
<div class="doc-upload-section">
  <!-- 现有下拉框区域 -->
  <div class="doc-name-selector">
    <span class="doc-name-label">证件名称：</span>
    <el-select v-model="docName" style="width: 160px">
      <el-option
        v-for="opt in docOptions"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value" />
    </el-select>
    <el-input
      v-if="docName === 'custom'"
      v-model="customDocName"
      placeholder="自定义名称"
      size="small"
      style="width: 120px; margin-left: 8px" />
  </div>
  
  <!-- 原上传按钮 -->
  <div class="doc-upload-actions">
    <el-upload
      class="doc-uploader"
      action="#"
      :auto-upload="false"
      :http-request="handleUploadFile"
      :show-file-list="false"
      accept="image/jpeg,image/png,image/jpg">
      <el-button type="primary">选择文件</el-button>
    </el-upload>
    <el-button @click="docDialogVisible = false">取消</el-button>
  </div>
  
  <!-- 新增：待上传确认区域（文件选择后显示） -->
  <div v-if="pendingFile" class="doc-pending-confirm">
    <span class="pending-file-name">已选: {{ pendingFileName }}</span>
    <el-button type="primary" size="small" @click="confirmUpload">确定上传</el-button>
    <el-button size="small" @click="cancelUpload">取消</el-button>
  </div>
</div>
```

**Step 2: 添加 CSS 样式**

```scss
.doc-pending-confirm {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin-top: 10px;
  background: #f0f9eb;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
  
  .pending-file-name {
    flex: 1;
    color: #606266;
    font-size: 14px;
  }
}
```

---

## Task 4: 新增 data 字段

**File:** `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 在 data() 中添加**

```javascript
docName: "驾驶证",
customDocName: "",
pendingFile: null,         // 待上传文件对象
pendingFileName: "",       // 待上传文件名
deleteConfirmVisible: false,
```

---

## Task 5: 整体测试

1. 打开证件弹窗
2. 选择图片文件，确认待上传区域出现
3. 确认下拉框默认值为"驾驶证"
4. 修改下拉框选择其他证件名称
5. 点击确定上传，观察上传成功和图片列表刷新
6. 点击取消，观察待上传区域消失

---

## 已知问题

无

---

## 提交

```bash
git add frontEnd/src/components/Container/car/CarList.vue
git commit -m "refactor(car): 优化证件上传流程 - 先选图片再命名"
```