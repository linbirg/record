<template>
  <div class="car-registration">
    <div class="registration-header">
      <h2 class="title">新增车辆登记</h2>
      <button class="close-btn" @click="handleClose">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="step-indicator">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <span class="step-number">1</span>
        <span class="step-label">上传证件</span>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <span class="step-number">2</span>
        <span class="step-label">确认信息</span>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
      <div class="step" :class="{ active: currentStep >= 3 }">
        <span class="step-number">3</span>
        <span class="step-label">完成</span>
      </div>
    </div>

    <div class="step-content">
      <Step1Upload 
        v-if="currentStep === 1"
        @next="onStep1Next"
      />
      
      <Step2Confirm 
        v-if="currentStep === 2"
        :initialData="step1Data"
        :ocrResults="step1OcrResults"
        @prev="currentStep = 1"
        @submit="onStep2Submit"
        @reupload="onReupload"
      />
      
      <Step3Complete 
        v-if="currentStep === 3"
        :carInfo="submittedCar"
        @back="handleBack"
        @continue="handleContinue"
      />
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Step1Upload from './Step1Upload.vue';
import Step2Confirm from './Step2Confirm.vue';
import Step3Complete from './Step3Complete.vue';

export default {
  name: 'CarRegistration',
  components: {
    Step1Upload,
    Step2Confirm,
    Step3Complete
  },
  data() {
    return {
      currentStep: 1,
      step1Data: {},
      step1OcrResults: {},
      submittedCar: {}
    };
  },
  methods: {
    ...mapActions(['post']),
    
    onStep1Next(data) {
      this.step1Data = data;
      this.step1OcrResults = data.ocrResults || {};
      this.currentStep = 2;
    },
    
    async onStep2Submit(formData) {
      try {
        const requestData = {
          ...formData,
          drivingLicense: this.step1Data.drivingLicense || null,
          driverLicense: this.step1Data.driverLicense || null
        };
        
        await this.post({
          url: 'car/add',
          data: requestData
        });
        
        this.submittedCar = {
          name: formData.name,
          carNo: formData.carNo
        };
        
        this.currentStep = 3;
      } catch (error) {
        console.error('提交失败:', error);
        this.$message.error('添加失败，请稍后重试');
      }
    },
    
    onReupload(type) {
      this.currentStep = 1;
    },
    
    handleClose() {
      this.$emit('close');
    },
    
    handleBack() {
      this.$emit('close');
      this.$router.push('/carsReg');
    },
    
    handleContinue() {
      this.currentStep = 1;
      this.step1Data = {};
      this.step1OcrResults = {};
    }
  }
};
</script>

<style lang="scss" scoped>
.car-registration {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 
    0px 84px 24px rgba(0,0,0,0),
    0px 54px 22px rgba(0,0,0,0.01),
    0px 30px 18px rgba(0,0,0,0.04),
    0px 13px 13px rgba(0,0,0,0.08),
    0px 3px 7px rgba(0,0,0,0.09);
  overflow: hidden;
}

.registration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;

  .title {
    font-size: 16px;
    font-weight: 600;
    color: #080808;
    margin: 0;
  }

  .close-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    color: #9ca3af;
    transition: color 0.2s;

    svg {
      width: 20px;
      height: 20px;
    }

    &:hover {
      color: #080808;
    }
  }
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;

  .step-number {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e5e7eb;
    color: #9ca3af;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .step-label {
    font-size: 14px;
    color: #9ca3af;
    transition: color 0.2s;
  }

  &.active {
    .step-number {
      background: #146ef5;
      color: #ffffff;
    }

    .step-label {
      color: #080808;
      font-weight: 500;
    }
  }

  &.completed {
    .step-number {
      background: #10b981;
      color: #ffffff;
    }
  }
}

.step-line {
  width: 60px;
  height: 2px;
  background: #e5e7eb;
  transition: background 0.2s;

  &.active {
    background: #146ef5;
  }
}

.step-content {
  min-height: 400px;
}
</style>
