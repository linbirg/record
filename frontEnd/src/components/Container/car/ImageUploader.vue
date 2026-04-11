<template>
  <div 
    class="image-uploader"
    :class="{ 'has-image': imageUrl, 'is-dragging': isDragging }"
    @click="triggerUpload"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <input 
      type="file" 
      ref="fileInput" 
      accept="image/jpeg,image/png" 
      @change="onFileSelect"
      style="display: none"
    />
    
    <div v-if="!imageUrl" class="upload-placeholder">
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17,8 12,3 7,8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      <span class="upload-text">{{ placeholder }}</span>
      <span class="upload-hint">支持 JPG、PNG 格式</span>
    </div>
    
    <div v-else class="image-preview">
      <img :src="imageUrl" :alt="alt" />
      <div class="image-overlay">
        <button class="reupload-btn" @click.stop="triggerUpload">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17,8 12,3 7,8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          重新上传
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUploader',
  props: {
    value: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '点击或拖拽上传'
    },
    alt: {
      type: String,
      default: '图片'
    }
  },
  data() {
    return {
      isDragging: false,
      imageUrl: this.value
    };
  },
  watch: {
    value(val) {
      this.imageUrl = val;
    }
  },
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click();
    },
    onDragOver(e) {
      this.isDragging = true;
    },
    onDragLeave(e) {
      this.isDragging = false;
    },
    onDrop(e) {
      this.isDragging = false;
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFile(files[0]);
      }
    },
    onFileSelect(e) {
      const files = e.target.files;
      if (files.length > 0) {
        this.handleFile(files[0]);
      }
    },
    handleFile(file) {
      if (!file.type.match(/image\/(jpeg|png)/)) {
        this.$message.error('只能上传 JPG 或 PNG 格式的图片');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageUrl = e.target.result;
        this.$emit('input', e.target.result);
        this.$emit('change', {
          file: file,
          base64: e.target.result
        });
      };
      reader.readAsDataURL(file);
    }
  }
};
</script>

<style lang="scss" scoped>
.image-uploader {
  width: 100%;
  height: 160px;
  border: 2px dashed #d8d8d8;
  border-radius: 8px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
  position: relative;

  &:hover {
    border-color: #146ef5;
    background: rgba(20, 110, 245, 0.02);
  }

  &.is-dragging {
    border-color: #146ef5;
    background: rgba(20, 110, 245, 0.05);
  }

  &.has-image {
    border-style: solid;
    height: auto;
    min-height: 160px;
  }
}

.upload-placeholder {
  height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .upload-icon {
    width: 32px;
    height: 32px;
    color: #9ca3af;
  }

  .upload-text {
    font-size: 14px;
    color: #374151;
    font-weight: 500;
  }

  .upload-hint {
    font-size: 12px;
    color: #9ca3af;
  }
}

.image-preview {
  position: relative;
  
  img {
    width: 100%;
    height: auto;
    max-height: 200px;
    object-fit: contain;
    display: block;
  }

  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s ease;

    &:hover {
      opacity: 1;
    }
  }

  .reupload-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    color: #080808;
    cursor: pointer;
    transition: all 0.2s ease;

    svg {
      width: 16px;
      height: 16px;
    }

    &:hover {
      transform: translate(6px);
    }
  }
}
</style>
