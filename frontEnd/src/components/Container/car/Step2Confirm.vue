<template>
  <div class="step2-confirm">
    <p class="step-description">
      已识别到以下信息，请确认或修改
    </p>

    <div class="preview-section">
      <div class="preview-item">
        <div class="preview-image" v-if="drivingLicense">
          <img :src="drivingLicense" alt="行驶证" />
          <button class="reupload-btn" @click="$emit('reupload', 'driving')">重新上传</button>
        </div>
        <div class="preview-placeholder" v-else>
          <span>未上传行驶证</span>
        </div>
      </div>
      <div class="preview-item">
        <div class="preview-image" v-if="driverLicense">
          <img :src="driverLicense" alt="驾驶证" />
          <button class="reupload-btn" @click="$emit('reupload', 'driver')">重新上传</button>
        </div>
        <div class="preview-placeholder" v-else>
          <span>未上传驾驶证</span>
        </div>
      </div>
    </div>

    <div class="form-section">
      <div class="form-group recognized">
        <label class="form-label">
          车牌号
          <span class="status-badge recognized" v-if="form.carNo">✓ 已识别</span>
          <span class="status-badge" v-else>未识别</span>
        </label>
        <input 
          type="text" 
          v-model="form.carNo" 
          class="form-input" 
          placeholder="请输入车牌号"
        />
      </div>

      <div class="form-group recognized">
        <label class="form-label">
          车辆品牌
          <span class="status-badge recognized" v-if="form.brand">✓ 已识别</span>
        </label>
        <input 
          type="text" 
          v-model="form.brand" 
          class="form-input" 
          placeholder="请输入车辆品牌"
        />
      </div>

      <div class="form-group recognized">
        <label class="form-label">
          车辆型号
          <span class="status-badge recognized" v-if="form.model">✓ 已识别</span>
        </label>
        <input 
          type="text" 
          v-model="form.model" 
          class="form-input" 
          placeholder="请输入车辆型号"
        />
      </div>

      <div class="form-group recognized">
        <label class="form-label">
          姓名
          <span class="status-badge recognized" v-if="form.name">✓ 已识别</span>
        </label>
        <input 
          type="text" 
          v-model="form.name" 
          class="form-input" 
          placeholder="请输入姓名"
        />
      </div>

      <div class="form-divider"></div>

      <div class="form-group">
        <label class="form-label">部门</label>
        <input 
          type="text" 
          v-model="form.dept" 
          class="form-input" 
          placeholder="请输入部门"
        />
      </div>

      <div class="form-group">
        <label class="form-label">编号</label>
        <div class="seq-no-input">
          <select v-model="form.seqNoPrefix" class="seq-prefix">
            <option value="No.">No.</option>
            <option value="临No.">临No.</option>
          </select>
          <input 
            type="text" 
            v-model="form.seqNoSuffix" 
            class="seq-suffix" 
            placeholder="编号"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">注册日期</label>
        <input 
          type="text" 
          v-model="form.regDate" 
          class="form-input" 
          placeholder="如：2024-01-15"
        />
      </div>

      <div class="form-group">
        <label class="form-label">行驶证号</label>
        <input 
          type="text" 
          v-model="form.carlicense" 
          class="form-input" 
          placeholder="请输入行驶证号"
        />
      </div>

      <div class="form-group">
        <label class="form-label">驾驶证号</label>
        <input 
          type="text" 
          v-model="form.license" 
          class="form-input" 
          placeholder="请输入驾驶证号"
        />
      </div>

      <div class="form-group">
        <label class="form-label">备注</label>
        <textarea 
          v-model="form.abbr" 
          class="form-textarea" 
          placeholder="请输入备注"
          rows="2"
        ></textarea>
      </div>
    </div>

    <div class="step-actions">
      <button class="btn btn-secondary" @click="$emit('prev')">
        ← 上一步
      </button>
      <button 
        class="btn btn-primary" 
        :disabled="!isValid"
        @click="handleSubmit"
      >
        确认添加
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Step2Confirm',
  props: {
    initialData: {
      type: Object,
      default: () => ({})
    },
    ocrResults: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      drivingLicense: this.initialData.drivingLicense || '',
      driverLicense: this.initialData.driverLicense || '',
      form: {
        carNo: '',
        brand: '',
        model: '',
        name: '',
        dept: '',
        seqNoPrefix: 'No.',
        seqNoSuffix: '',
        regDate: '',
        carlicense: '',
        license: '',
        abbr: ''
      }
    };
  },
  watch: {
    ocrResults: {
      immediate: true,
      handler(results) {
        if (results.driving) {
          const d = results.driving;
          if (d.carNo) this.form.carNo = d.carNo;
          if (d.brand) this.form.brand = d.brand;
          if (d.model) this.form.model = d.model;
          if (d.regDate) this.form.regDate = d.regDate;
        }
        if (results.driver && results.driver.name) {
          this.form.name = results.driver.name;
        }
      }
    }
  },
  computed: {
    isValid() {
      return this.form.name && this.form.carNo;
    }
  },
  methods: {
    handleSubmit() {
      if (!this.isValid) return;
      
      const submitData = {
        ...this.form,
        seqNo: this.form.seqNoPrefix + this.form.seqNoSuffix
      };
      delete submitData.seqNoPrefix;
      delete submitData.seqNoSuffix;
      
      this.$emit('submit', submitData);
    }
  }
};
</script>

<style lang="scss" scoped>
.step2-confirm {
  padding: 24px;
}

.step-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
  text-align: center;
}

.preview-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.preview-item {
  .preview-image {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e5e7eb;

    img {
      width: 100%;
      height: 120px;
      object-fit: cover;
    }

    .reupload-btn {
      position: absolute;
      bottom: 8px;
      left: 50%;
      transform: translateX(-50%);
      padding: 4px 12px;
      background: rgba(255, 255, 255, 0.9);
      border: none;
      border-radius: 4px;
      font-size: 12px;
      color: #374151;
      cursor: pointer;
      opacity: 0;
      transition: opacity 0.2s;

      &:hover {
        background: #ffffff;
      }
    }

    &:hover .reupload-btn {
      opacity: 1;
    }
  }

  .preview-placeholder {
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f9fafb;
    border: 1px dashed #d8d8d8;
    border-radius: 8px;
    color: #9ca3af;
    font-size: 14px;
  }
}

.form-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;

  &.recognized .form-input {
    background: #ffffff;
  }
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.status-badge {
  font-size: 12px;
  font-weight: 400;
  padding: 2px 8px;
  border-radius: 10px;
  background: #e5e7eb;
  color: #6b7280;

  &.recognized {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
  }
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 14px;
  background: #ffffff;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #146ef5;
  }

  &::placeholder {
    color: #9ca3af;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.seq-no-input {
  display: flex;
  gap: 8px;

  .seq-prefix {
    width: 100px;
    padding: 10px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    font-size: 14px;
    background: #ffffff;

    &:focus {
      outline: none;
      border-color: #146ef5;
    }
  }

  .seq-suffix {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: #146ef5;
    }
  }
}

.form-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 20px 0;
}

.step-actions {
  display: flex;
  justify-content: space-between;
}

.btn {
  height: 40px;
  padding: 0 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: #146ef5;
  color: #ffffff;
  border: none;

  &:hover:not(:disabled) {
    background: #0055d4;
    transform: translate(6px);
  }
}

.btn-secondary {
  background: #ffffff;
  color: #080808;
  border: 1px solid #d8d8d8;

  &:hover:not(:disabled) {
    border-color: #146ef5;
    color: #146ef5;
  }
}

@media (max-width: 768px) {
  .preview-section {
    grid-template-columns: 1fr;
  }
}
</style>
