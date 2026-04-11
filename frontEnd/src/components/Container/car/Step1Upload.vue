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
        :disabled="!canOcr || isOcrLoading"
        @click="handleOcr"
      >
        <span v-if="isOcrLoading" class="loading-spinner"></span>
        <span v-else>识别全部</span>
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
  </div>
</template>

<script>
import ImageUploader from './ImageUploader.vue';

export default {
  name: 'Step1Upload',
  components: {
    ImageUploader
  },
  props: {
    ocrApiKey: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      drivingLicense: '',
      driverLicense: '',
      isOcrLoading: false,
      ocrResults: {}
    };
  },
  computed: {
    hasImages() {
      return this.drivingLicense || this.driverLicense;
    },
    canOcr() {
      return this.drivingLicense && !this.isOcrLoading;
    }
  },
  methods: {
    onDrivingLicenseChange(data) {
      this.drivingLicense = data ? data.base64 : '';
    },
    onDriverLicenseChange(data) {
      this.driverLicense = data ? data.base64 : '';
    },
    async handleOcr() {
      if (!this.canOcr) return;
      
      this.isOcrLoading = true;
      
      try {
        // 识别行驶证
        const drivingResult = await this.ocrImage(this.drivingLicense, 'driving');
        
        // 如果有驾驶证也识别
        let driverResult = null;
        if (this.driverLicense) {
          driverResult = await this.ocrImage(this.driverLicense, 'driver');
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
        this.isOcrLoading = false;
      }
    },
    async ocrImage(base64, type) {
      // MiniMax Vision API 调用
      const API_URL = 'https://api.minimax.chat/v1/text/chatcompletion_v2';
      
      let prompt = '';
      if (type === 'driving') {
        prompt = '请从这张行驶证图片中提取信息，返回JSON格式：车牌号(carNo)、车辆品牌(brand)、车辆型号(model)、注册日期(regDate)。只返回JSON，不要其他文字。';
      } else {
        prompt = '请从这张驾驶证图片中提取信息，返回JSON格式：姓名(name)。只返回JSON，不要其他文字。';
      }
      
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.ocrApiKey}`
        },
        body: JSON.stringify({
          model: 'MiniMax-VL01',
          messages: [{
            role: 'user',
            content: [
              { type: 'text', text: prompt },
              { type: 'image_url', image_url: { url: base64 } }
            ]
          }]
        })
      });
      
      const data = await response.json();
      
      if (data.choices && data.choices[0] && data.choices[0].message) {
        const content = data.choices[0].message.content;
        // 尝试解析 JSON
        try {
          // 去除 markdown 代码块
          const jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
          return JSON.parse(jsonStr);
        } catch (e) {
          console.error('Parse OCR result failed:', e);
          return this.parseTextResult(content, type);
        }
      }
      
      return null;
    },
    parseTextResult(text, type) {
      // 简单文本解析作为后备
      const result = {};
      
      if (type === 'driving') {
        const carNoMatch = text.match(/车牌[号号码]?\s*[:：]?\s*([\u4e00-\u9fa5A-Z0-9]+)/i);
        const brandMatch = text.match(/品牌\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z]+)/i);
        const modelMatch = text.match(/型号\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9]+)/i);
        
        if (carNoMatch) result.carNo = carNoMatch[1];
        if (brandMatch) result.brand = brandMatch[1];
        if (modelMatch) result.model = modelMatch[1];
      } else {
        const nameMatch = text.match(/姓名\s*[:：]?\s*([\u4e00-\u9fa5]{2,4})/i);
        if (nameMatch) result.name = nameMatch[1];
      }
      
      return result;
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

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .uploaders {
    grid-template-columns: 1fr;
  }
}
</style>
