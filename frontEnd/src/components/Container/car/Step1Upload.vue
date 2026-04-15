<template>
  <div class="step1-upload">
    <p class="step-description">
      请上传行驶证和驾驶证，我们会自动识别其中的信息
    </p>
    
    <div class="uploaders">
      <div class="uploader-item">
        <label class="uploader-label">行驶证</label>
        <ImageUploader
          v-model="drivingLicense"
          placeholder="拖拽或点击上传行驶证"
          alt="行驶证"
          @change="onDrivingLicenseChange"
        />
      </div>
      
      <div class="uploader-item">
        <label class="uploader-label">驾驶证（可选）</label>
        <ImageUploader
          v-model="driverLicense"
          placeholder="拖拽或点击上传驾驶证"
          alt="驾驶证"
          @change="onDriverLicenseChange"
        />
      </div>
    </div>

    <div class="step-actions">
      <button 
        class="btn btn-primary" 
        :disabled="!canOcr || paddleOcrLoading || minimaxLoading"
        @click="handleOcr('paddleocr')"
      >
        <span v-if="paddleOcrLoading" class="loading-spinner white"></span>
        <span v-else>识别行驶证（OCR）</span>
      </button>
      <button 
        class="btn btn-outline"
        :disabled="!canOcr || paddleOcrLoading || minimaxLoading"
        @click="handleOcr('minimax')"
      >
        <span v-if="minimaxLoading" class="loading-spinner blue"></span>
        <span v-else>大模型识别</span>
      </button>
      <button 
        class="btn btn-secondary"
        :disabled="!hasImages"
        @click="handleNext"
      >
        下一步
        <span class="arrow">→</span>
      </button>
    </div>

    <div v-if="ocrResults.driving || ocrResults.driver" class="ocr-results">
      <div class="results-title">识别结果</div>
      <div class="results-grid">
        <div v-if="ocrResults.driving" class="result-item">
          <span class="result-label">车牌号：</span>
          <span class="result-value" :class="{ empty: !ocrResults.driving.carNo }">
            {{ ocrResults.driving.carNo || '未识别' }}
          </span>
        </div>
        <div v-if="getDisplayName" class="result-item">
          <span class="result-label">姓名：</span>
          <span class="result-value" :class="{ empty: !getDisplayName }">
            {{ getDisplayName }}
          </span>
        </div>
        <div v-if="ocrResults.driving" class="result-item">
          <span class="result-label">品牌：</span>
          <span class="result-value" :class="{ empty: !ocrResults.driving.brand }">
            {{ ocrResults.driving.brand || '未识别' }}
          </span>
        </div>
        <div v-if="ocrResults.driving" class="result-item">
          <span class="result-label">型号：</span>
          <span class="result-value" :class="{ empty: !ocrResults.driving.model }">
            {{ ocrResults.driving.model || '未识别' }}
          </span>
        </div>
        <div v-if="ocrResults.driving" class="result-item">
          <span class="result-label">注册日期：</span>
          <span class="result-value" :class="{ empty: !ocrResults.driving.regDate }">
            {{ ocrResults.driving.regDate || '未识别' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageUploader from './ImageUploader.vue';
import { mapActions } from 'vuex';

export default {
  name: 'Step1Upload',
  components: {
    ImageUploader
  },
  data() {
    return {
      drivingLicense: '',
      driverLicense: '',
      paddleOcrLoading: false,
      minimaxLoading: false,
      ocrResults: {}
    };
  },
  computed: {
    hasImages() {
      return this.drivingLicense || this.driverLicense;
    },
    canOcr() {
      return this.drivingLicense;
    },
    getDisplayName() {
      if (this.ocrResults.driving && this.ocrResults.driving.name) {
        return this.ocrResults.driving.name;
      }
      if (this.ocrResults.driver && this.ocrResults.driver.name) {
        return this.ocrResults.driver.name;
      }
      return '';
    }
  },
  methods: {
    ...mapActions(['post']),
    onDrivingLicenseChange(data) {
      this.drivingLicense = data ? data.base64 : '';
    },
    onDriverLicenseChange(data) {
      this.driverLicense = data ? data.base64 : '';
    },
    async handleOcr(engine = 'paddleocr') {
      if (!this.canOcr) return;
      
      if (engine === 'paddleocr') {
        this.paddleOcrLoading = true;
      } else {
        this.minimaxLoading = true;
      }
      
      try {
        const drivingResult = await this.ocrImage(this.drivingLicense, 'driving', engine);
        
        let driverResult = null;
        if (this.driverLicense) {
          driverResult = await this.ocrImage(this.driverLicense, 'driver', engine);
        }
        
        this.ocrResults = {
          driving: drivingResult,
          driver: driverResult
        };
        
        this.$emit('ocr-complete', this.ocrResults);
        this.$message.success('识别完成，请确认信息');
      } catch (error) {
        console.error('OCR error:', error);
        this.$message.error('识别失败，请稍后重试');
      } finally {
        this.paddleOcrLoading = false;
        this.minimaxLoading = false;
      }
    },
    async ocrImage(base64, type, engine = 'paddleocr') {
      const response = await this.post({
        url: 'car/ocr',
        data: { image: base64, type, engine }
      });
      return response;
    },
    handleNext() {
      this.$emit('next', {
        drivingLicense: this.drivingLicense,
        driverLicense: this.driverLicense,
        ocrResults: this.ocrResults
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.step1-upload {
  padding: 24px;
}

.step-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
  text-align: center;
}

.uploaders {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.uploader-item {
  .uploader-label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 8px;
  }
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.btn {
  height: 40px;
  padding: 0 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

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

  .arrow {
    transition: transform 0.2s ease;
  }

  &:hover:not(:disabled) .arrow {
    transform: translate(6px);
  }
}

.btn-outline {
  background: #ffffff;
  color: #146ef5;
  border: 1px solid #146ef5;

  &:hover:not(:disabled) {
    background: #146ef5;
    color: #ffffff;
  }
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  
  &.white {
    border: 2px solid #ffffff;
    border-top-color: transparent;
  }
  
  &.blue {
    border: 2px solid #146ef5;
    border-top-color: transparent;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.ocr-results {
  margin-top: 24px;
  padding: 16px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
}

.results-title {
  font-size: 14px;
  font-weight: 600;
  color: #166534;
  margin-bottom: 12px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 24px;
}

.result-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.result-label {
  color: #374151;
  font-weight: 500;
}

.result-value {
  color: #166534;
  
  &.empty {
    color: #9ca3af;
    font-style: italic;
  }
}

@media (max-width: 768px) {
  .uploaders {
    grid-template-columns: 1fr;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
