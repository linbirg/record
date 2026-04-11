<template>
  <div class="step3-complete">
    <div class="success-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20,6 9,17 4,12"/>
      </svg>
    </div>

    <h2 class="success-title">车辆登记成功！</h2>
    
    <div class="car-info">
      <span class="name">{{ carInfo.name }}</span>
      <span class="separator">-</span>
      <span class="carNo">{{ carInfo.carNo }}</span>
    </div>

    <div class="actions">
      <button class="btn btn-secondary" @click="$emit('back')">
        返回车辆列表
      </button>
      <button class="btn btn-primary" @click="$emit('continue')">
        继续添加下一辆
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Step3Complete',
  props: {
    carInfo: {
      type: Object,
      default: () => ({})
    }
  }
};
</script>

<style lang="scss" scoped>
.step3-complete {
  padding: 48px 24px;
  text-align: center;
}

.success-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 24px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 32px;
    height: 32px;
    color: #10b981;
  }
}

.success-title {
  font-size: 24px;
  font-weight: 600;
  color: #080808;
  margin: 0 0 16px 0;
}

.car-info {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 32px;

  .name {
    font-weight: 500;
    color: #374151;
  }

  .separator {
    margin: 0 8px;
  }
}

.actions {
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
}

.btn-primary {
  background: #146ef5;
  color: #ffffff;
  border: none;

  &:hover {
    background: #0055d4;
    transform: translate(6px);
  }
}

.btn-secondary {
  background: #ffffff;
  color: #080808;
  border: 1px solid #d8d8d8;

  &:hover {
    border-color: #146ef5;
    color: #146ef5;
  }
}
</style>
