# 车辆批量导入 Word 功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在车辆列表页面实现从 Word 文档批量导入车辆信息（姓名、车牌号）

**Architecture:** 
- 后端新增 `/car/import_word` 接口，使用 python-docx 解析 Word 表格
- 前端新增 ImportWordDialog.vue 弹窗组件，负责文件选择、进度展示
- 复用现有 `/car/add` 接口逐条添加车辆

**Tech Stack:** python-docx, element-ui el-dialog/el-upload/el-progress

---

## 前置准备

**Step 1: 安装 python-docx 依赖**

```bash
cd /mnt/d/project/linbirg/ww/ww/record/yail
source venv/bin/activate  # 或使用 uv
pip install python-docx
```

验证安装：
```bash
python -c "import docx; print(docx.__version__)"
```

---

## Task 1: 后端接口开发

**File:** Create: `yail/www/handlers/car/import_word.py`

**Step 1: 编写解析 Word 表格函数**

```python
# yail/www/handlers/car/import_word.py

import io
from typing import List, Dict, Tuple
from docx import Document

def parse_word_table(file_bytes: bytes) -> Tuple[List[Dict], List[Dict]]:
    """
    解析 Word 文档中的表格，提取姓名和车牌号
    
    Args:
        file_bytes: Word 文件字节数据
    
    Returns:
        (valid_rows, error_rows)
        valid_rows: [{'name': str, 'carNo': str}, ...]
        error_rows: [{'row': int, 'message': str}, ...]
    """
    doc = Document(io.BytesIO(file_bytes))
    
    if not doc.tables:
        raise ValueError("文档中没有找到表格")
    
    table = doc.tables[0]
    if len(table.rows) < 2:
        raise ValueError("文档中没有找到车辆数据")
    
    # 查找表头列索引
    header_row = table.rows[0]
    name_col = -1
    carNo_col = -1
    
    for i, cell in enumerate(header_row.cells):
        text = cell.text.strip()
        if '姓名' in text:
            name_col = i
        elif '车牌号' in text:
            carNo_col = i
    
    if name_col == -1 or carNo_col == -1:
        raise ValueError("表格中未找到姓名和车牌号列")
    
    # 提取数据行
    valid_rows = []
    error_rows = []
    
    for row_idx, row in enumerate(table.rows[1:], start=2):
        try:
            name = row.cells[name_col].text.strip()
            car_no = row.cells[carNo_col].text.strip()
            
            if not name and not car_no:
                continue  # 跳过空行
            
            if not name or not car_no:
                error_rows.append({
                    'row': row_idx,
                    'message': f"姓名或车牌号为空 (姓名:{name}, 车牌号:{car_no})"
                })
                continue
            
            valid_rows.append({'name': name, 'carNo': car_no})
        except Exception as e:
            error_rows.append({'row': row_idx, 'message': str(e)})
    
    return valid_rows, error_rows
```

**Step 2: 运行测试验证**

保存测试文件到临时位置，用以下命令验证：
```bash
cd /mnt/d/project/linbirg/ww/ww/record
python -c "
from yail.www.handlers.car.import_word import parse_word_table
print('parse_word_table 函数导入成功')
"
```

**Step 3: 提交**

```bash
git add yail/www/handlers/car/import_word.py
git commit -m "feat(car): 添加Word表格解析函数"
```

---

## Task 2: 后端 API 接口

**File:** Modify: `yail/www/handlers/car/index.py` (在文件末尾添加新接口)

**Step 1: 添加 import_word 接口**

```python
@route("/car/import_word", method=["POST"])
async def import_word(request):
    """
    批量导入车辆（从Word文档）
    
    请求: multipart/form-data, file字段
    响应: {success, total, added, failed, errors}
    """
    from .import_word import parse_word_table
    
    try:
        files = request.multipart.get("file")
        if not files:
            return json({"success": False, "message": "请选择文件"})
        
        file_data = await files.read()
        
        # 解析表格
        valid_rows, error_rows = parse_word_table(file_data)
        
        if not valid_rows:
            return json({
                "success": False,
                "message": "未找到有效的车辆数据",
                "errors": error_rows
            })
        
        # 逐条添加车辆
        added = 0
        for row in valid_rows:
            try:
                await CarInfo.add(
                    name=row['name'],
                    carNo=row['carNo'],
                    dept="",  # Word导入不包含此字段
                    brand="",
                    carLicense="",
                    license="",
                    abbr="批量导入"
                )
                added += 1
            except Exception as e:
                error_rows.append({'row': -1, 'message': f"{row['name']}: {str(e)}"})
        
        return json({
            "success": True,
            "total": len(valid_rows) + len(error_rows),
            "added": added,
            "failed": len(error_rows),
            "errors": error_rows
        })
        
    except ValueError as e:
        return json({"success": False, "message": str(e)})
    except Exception as e:
        return json({"success": False, "message": f"导入失败: {str(e)}"})
```

**Step 2: 添加 CarInfo.add 静态方法（如果不存在）**

检查 `yail/www/dao/car_info.py` 是否有 add 方法，如果没有需要添加：

```python
@classmethod
async def add(cls, **kwargs):
    """添加车辆记录"""
    return await cls.insert(**kwargs)
```

**Step 3: 测试接口**

```bash
cd /mnt/d/project/linbirg/ww/ww/record
# 启动服务后用 curl 测试
curl -X POST -F "file=@test.docx" http://localhost:8888/car/import_word
```

**Step 4: 提交**

```bash
git add yail/www/handlers/car/index.py yail/www/dao/car_info.py
git commit -m "feat(car): 添加/car/import_word批量导入接口"
```

---

## Task 3: 前端 ImportWordDialog 组件

**File:** Create: `frontEnd/src/components/Container/car/ImportWordDialog.vue`

**Step 1: 创建组件**

```vue
<template>
  <el-dialog
    title="批量导入车辆"
    :visible.sync="visible"
    width="500px"
    :close-on-click-modal="false"
  >
    <div v-if="!uploading && !result">
      <el-upload
        ref="upload"
        class="import-upload"
        drag
        action="#"
        :auto-upload="false"
        :limit="1"
        accept=".docx"
        :on-change="handleFileChange"
        :file-list="fileList"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将 Word 文档拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">只能上传 .docx 文件</div>
      </el-upload>
    </div>

    <div v-if="uploading" class="import-progress">
      <el-progress :percentage="progress" :stroke-width="10"></el-progress>
      <p class="progress-text">正在导入，请稍候...</p>
    </div>

    <div v-if="result" class="import-result">
      <el-result
        :icon="result.success ? 'success' : 'warning'"
        :title="result.success ? '导入完成' : '导入完成（部分失败）'"
      >
        <div slot="extra">
          <p>总计: {{ result.total }} 条</p>
          <p>成功: {{ result.added }} 条</p>
          <p v-if="result.failed > 0">失败: {{ result.failed }} 条</p>
          <div v-if="result.errors && result.errors.length > 0" class="error-list">
            <p v-for="(err, idx) in result.errors.slice(0, 5)" :key="idx">
              {{ err.message }}
            </p>
          </div>
        </div>
      </el-result>
    </div>

    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">取 消</el-button>
      <el-button type="primary" :disabled="!selectedFile || uploading || result" @click="handleImport">
        开始导入
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'ImportWordDialog',
  data() {
    return {
      visible: false,
      uploading: false,
      progress: 0,
      result: null,
      selectedFile: null,
      fileList: []
    }
  },
  methods: {
    open() {
      this.visible = true
      this.reset()
    },
    reset() {
      this.uploading = false
      this.progress = 0
      this.result = null
      this.selectedFile = null
      this.fileList = []
    },
    handleFileChange(file, files) {
      this.selectedFile = file.raw
      this.fileList = files.slice(-1)
    },
    async handleImport() {
      if (!this.selectedFile) return
      
      this.uploading = true
      this.progress = 0

      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        this.progress = 30
        const response = await this.post({
          url: 'car/import_word',
          data: formData
        })
        this.progress = 100
        this.result = response
      } catch (e) {
        this.result = {
          success: false,
          total: 0,
          added: 0,
          failed: 1,
          errors: [{ row: -1, message: e.message || '网络错误' }]
        }
      } finally {
        this.uploading = false
      }
    },
    handleClose() {
      if (this.uploading) return
      this.visible = false
    }
  }
}
</script>

<style scoped>
.import-upload {
  text-align: center;
}
.import-upload .el-icon-upload {
  font-size: 67px;
  color: #C0C4CC;
  margin: 20px 0;
}
.import-progress {
  text-align: center;
  padding: 20px 0;
}
.progress-text {
  margin-top: 20px;
  color: #909399;
}
.import-result .error-list {
  max-height: 150px;
  overflow-y: auto;
  text-align: left;
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
```

**Step 2: 提交**

```bash
git add frontEnd/src/components/Container/car/ImportWordDialog.vue
git commit -m "feat(car): 添加ImportWordDialog批量导入弹窗组件"
```

---

## Task 4: 在 CarList.vue 集成批量导入

**File:** Modify: `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 添加导入弹窗引用**

在 script 部分添加：
```javascript
import ImportWordDialog from './ImportWordDialog.vue'

export default {
  components: {
    ImportWordDialog
  },
  data() {
    return {
      // ... existing data
      importWordDialogRef: null
    }
  }
}
```

**Step 2: 在模板中添加导入按钮**

找到「添加车辆」按钮旁边，添加：
```html
<el-button type="primary" @click="openImportDialog">
  <i class="el-icon-upload2"></i> 批量导入
</el-button>
```

**Step 3: 添加导入弹窗**

在 template 末尾添加：
```html
<import-word-dialog ref="importWordDialogRef"></import-word-dialog>
```

**Step 4: 添加打开弹窗方法**

```javascript
openImportDialog() {
  this.$refs.importWordDialogRef.open()
}
```

**Step 5: 导入后刷新列表**

在 ImportWordDialog 的 handleImport 成功后调用父组件刷新：
```javascript
// 在 ImportWordDialog 中
this.$emit('imported')

// 在 CarList.vue 的 ImportWordDialog 上添加监听
<import-word-dialog ref="importWordDialogRef" @imported="loadCars"></import-word-dialog>
```

**Step 6: 提交**

```bash
git add frontEnd/src/components/Container/car/CarList.vue
git commit -m "feat(car): 在CarList集成批量导入Word功能"
```

---

## Task 5: 整体测试

**Step 1: 启动后端服务**

```bash
cd /mnt/d/project/linbirg/ww/ww/record/yail
python app.py
```

**Step 2: 启动前端**

```bash
cd frontEnd
npm run dev
```

**Step 3: 测试流程**

1. 打开车辆列表页面
2. 点击「批量导入」按钮
3. 弹窗显示正常
4. 选择 .docx 文件
5. 点击「开始导入」
6. 查看导入结果
7. 验证列表中新增的车辆

**Step 4: 提交**

```bash
git add -A
git commit -m "feat(car): 完成批量导入Word功能"
```
