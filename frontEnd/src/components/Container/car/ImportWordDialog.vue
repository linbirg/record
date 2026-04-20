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
      <el-button type="primary" :disabled="!selectedFile || uploading || !!result" @click="handleImport">
        开始导入
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
import { mapActions } from 'vuex'

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
    ...mapActions(['post']),
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

<style lang="scss" scoped>
.import-upload {
  text-align: center;

  .el-icon-upload {
    font-size: 67px;
    color: #c0c4cc;
    margin: 20px 0;
  }
}

.import-progress {
  text-align: center;
  padding: 20px 0;
}

.progress-text {
  margin-top: 20px;
  color: #909399;
}

.import-result {
  .error-list {
    max-height: 150px;
    overflow-y: auto;
    text-align: left;
    margin-top: 10px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }
}
</style>
