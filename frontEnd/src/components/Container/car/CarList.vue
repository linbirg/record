<template>
  <div class="car-list-container">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="车牌号或姓名搜索..."
          class="search-input"
          @input="handleSearch"
        />
      </div>
      <button class="add-btn" @click="showAddDialog">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>新增车辆</span>
      </button>
    </div>

    <!-- 车辆列表网格 -->
    <div class="car-grid" v-loading="loading">
      <div 
        v-for="car in filteredCars" 
        :key="car.no" 
        class="car-card"
        @click="showEditDialog(car)"
      >
        <div class="card-content">
          <div class="card-main">
            <h3 class="owner-name" :style="{ color: getNameColor(car.carNo) }">
              {{ car.name }}
            </h3>
            <p class="car-plate">
              {{ car.carNo }}
              <span v-if="isElectricCar(car)" class="ev-icon">⚡</span>
            </p>
            <p class="dept-name">{{ car.dept }}</p>
          </div>
          <button class="doc-btn" @click.stop="showDocDialog(car)" title="查看证件">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10,9 9,9 8,9"/>
            </svg>
          </button>
        </div>
        <div class="card-actions">
          <button class="delete-btn" @click.stop="handleDelete(car)" title="删除">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6"/>
              <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6M8,6V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"/>
            </svg>
            <span>删除</span>
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredCars.length === 0" class="empty-state">
        <p v-if="searchQuery">未找到匹配的车辆</p>
        <p v-else>暂无车辆数据</p>
      </div>
    </div>

    <!-- 证件弹窗 -->
    <el-dialog
      :visible.sync="docDialogVisible"
      title="证件信息"
      width="400px"
      :close-on-click-modal="true"
    >
      <div class="doc-content" v-if="currentCar">
        <p class="doc-car-info">{{ currentCar.name }} - {{ currentCar.carNo }}</p>
        <div class="doc-images" v-if="docImages.length > 0">
          <div v-for="(img, index) in docImages" :key="index" class="doc-image-item">
            <img :src="img.url" :alt="img.name" @click="previewImage(img.url)"/>
          </div>
        </div>
        <div v-else class="doc-empty">
          <p>暂无证件图片</p>
          <el-button size="small" @click="goToDetail">上传证件</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 图片预览 -->
    <el-dialog :visible.sync="previewVisible" width="60%" :close-on-click-modal="true">
      <img :src="previewUrl" style="width: 100%" />
    </el-dialog>

    <!-- 编辑/新增弹窗 -->
    <el-dialog
      :visible.sync="editDialogVisible"
      :title="isAdd ? '新增车辆' : '编辑车辆'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="carForm" :rules="rules" ref="carForm" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="carForm.name"></el-input>
        </el-form-item>
        <el-form-item label="部门" prop="dept">
          <el-input v-model="carForm.dept"></el-input>
        </el-form-item>
        <el-form-item label="车牌号" prop="carNo">
          <el-input v-model="carForm.carNo"></el-input>
        </el-form-item>
        <el-form-item label="编号" prop="seqNo">
          <el-row :gutter="10">
            <el-col :span="8">
              <el-select v-model="carForm.seqNoPrefix" placeholder="临No.">
                <el-option label="No." value="No."></el-option>
                <el-option label="临No." value="临No."></el-option>
              </el-select>
            </el-col>
            <el-col :span="16">
              <el-input v-model="carForm.seqNoSuffix" placeholder="编号"></el-input>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="carForm.brand"></el-input>
        </el-form-item>
        <el-form-item label="行驶证" prop="carlicense">
          <el-input v-model="carForm.carlicense"></el-input>
        </el-form-item>
        <el-form-item label="驾驶证" prop="license">
          <el-input v-model="carForm.license"></el-input>
        </el-form-item>
        <el-form-item label="备注" prop="abbr">
          <el-input v-model="carForm.abbr" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </span>
</el-dialog>

    <!-- 新增车辆登记弹窗 -->
    <el-dialog
      :visible.sync="registrationDialogVisible"
      title="新增车辆登记"
      width="600px"
      :close-on-click-modal="true"
    >
      <CarRegistration 
        v-if="registrationDialogVisible"
        @close="registrationDialogVisible = false; fetchCarList();"
      />
    </el-dialog>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import CarRegistration from "./CarRegistration.vue";

export default {
  name: "CarList",
  components: {
    CarRegistration,
  },
  data() {
    return {
      loading: false,
      searchQuery: "",
      carList: [],
      registrationDialogVisible: false,
      docDialogVisible: false,
      editDialogVisible: false,
      previewVisible: false,
      previewUrl: "",
      isAdd: true,
      currentCar: null,
      docImages: [],
      carForm: {
        no: -1,
        name: "",
        dept: "",
        carNo: "",
        seqNoPrefix: "No.",
        seqNoSuffix: "",
        brand: "",
        carlicense: "",
        license: "",
        abbr: "",
      },
      rules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        dept: [{ required: true, message: "请输入部门", trigger: "blur" }],
        carNo: [{ required: true, message: "请输入车牌号", trigger: "blur" }],
      },
      // 姓名颜色色板：按车牌尾号分配
      nameColors: [
        { indices: [0, 1], color: "#1e3a5f" }, // 深蓝
        { indices: [2, 3], color: "#1a4d3e" }, // 深绿
        { indices: [4, 5], color: "#3d2c4d" }, // 深紫
        { indices: [6, 7], color: "#4a3728" }, // 深棕
        { indices: [8, 9], color: "#2d3a4a" }, // 深灰蓝
      ],
      };
  },
  computed: {
    filteredCars() {
      if (!this.searchQuery) {
        return this.carList;
      }
      const query = this.searchQuery.toLowerCase();
      return this.carList.filter(
        (car) =>
          car.name.toLowerCase().includes(query) ||
          car.carNo.toLowerCase().includes(query) ||
          (car.dept && car.dept.toLowerCase().includes(query))
      );
    },
  },
  mounted() {
    this.loadCars();
  },
  methods: {
    ...mapActions(["get", "post"]),

    // 根据车牌号获取姓名颜色
    getNameColor(carNo) {
      if (!carNo) return "#374151";
      const lastDigit = carNo.replace(/\D/g, "").slice(-1);
      if (lastDigit === "") return "#374151";
      const digit = parseInt(lastDigit, 10);
      const colorObj = this.nameColors.find((c) =>
        c.indices.includes(digit)
      );
      return colorObj ? colorObj.color : "#374151";
    },

    // 判断是否是新能源车（车牌8位为新能源，7位为传统）
    isElectricCar(car) {
      if (!car || !car.carNo) return false;
      const plate = car.carNo.replace(/\s/g, '');
      return plate.length === 8;
    },

    loadCars() {
      this.loading = true;
      this.post({
        url: "car/page",
        data: { currentPage: 1, pageSize: 100 },
      })
        .then((response) => {
          this.loading = false;
          this.carList = response.carInfo || [];
        })
        .catch(() => {
          this.loading = false;
          this.$message.error("加载车辆列表失败");
        });
    },

    handleSearch() {
      // 实时过滤，无需请求
    },

    showDocDialog(car) {
      this.currentCar = car;
      this.docDialogVisible = true;
      this.loadDocImages(car.no);
    },

    loadDocImages(carNo) {
      this.post({
        url: "car/pic/filelist",
        data: { no: carNo },
      })
        .then((response) => {
          this.docImages = response || [];
        })
        .catch(() => {
          this.docImages = [];
        });
    },

    previewImage(url) {
      this.previewUrl = url;
      this.previewVisible = true;
    },

    goToDetail() {
      if (this.currentCar) {
        this.$emit("navigate", "detail", this.currentCar.no);
      }
    },

    showAddDialog() {
      this.isAdd = true;
      this.carForm = {
        no: -1,
        name: "",
        dept: "",
        carNo: "",
        seqNoPrefix: "No.",
        seqNoSuffix: "",
        brand: "",
        carlicense: "",
        license: "",
        abbr: "",
      };
      this.registrationDialogVisible = true;
    },

    showEditDialog(car) {
      this.isAdd = false;
      this.currentCar = car;
      this.carForm = {
        no: car.no,
        name: car.name,
        dept: car.dept,
        carNo: car.carNo,
        seqNoPrefix: car.seqNo ? car.seqNo.split(".")[0] + "." : "No.",
        seqNoSuffix: car.seqNo ? car.seqNo.split(".")[1] || "" : "",
        brand: car.brand || "",
        carlicense: car.carlicense || "",
        license: car.license || "",
        abbr: car.abbr || "",
      };
      this.editDialogVisible = true;
    },

    submitForm() {
      this.$refs.carForm.validate((valid) => {
        if (!valid) return;

        const seqNo = this.carForm.seqNoPrefix + this.carForm.seqNoSuffix;
        const submitData = {
          ...this.carForm,
          seqNo: seqNo,
        };
        delete submitData.seqNoPrefix;
        delete submitData.seqNoSuffix;

        const url = this.isAdd ? "car/add" : "car/update";
        this.post({
          url,
          data: submitData,
        })
          .then(() => {
            this.editDialogVisible = false;
            this.loadCars();
            this.$message.success(this.isAdd ? "添加成功" : "更新成功");
          })
          .catch(() => {
            this.$message.error(this.isAdd ? "添加失败" : "更新失败");
          });
      });
    },

    handleDelete(car) {
      this.$confirm(`确定要删除车辆 "${car.name} - ${car.carNo}" 吗？`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }).then(() => {
        return this.post({
          url: 'car/delete',
          data: { no: car.no }
        });
      }).then(() => {
        this.$message.success('删除成功');
        this.loadCars();
      }).catch(() => {
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.car-list-container {
  padding: 24px;
  min-height: 100%;
  background: #f9fafb;
}

// 搜索栏
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.search-input-wrapper {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 16px 0 40px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  background: #ffffff;
  transition: border-color 0.2s, box-shadow 0.2s;

  &::placeholder {
    color: #9ca3af;
  }

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 40px;
  padding: 0 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }
}

// 车辆网格
.car-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

// 车辆卡片
.car-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

    .doc-btn {
      color: #3b82f6;
    }
  }
}

.card-content {
  position: relative;
}

.card-main {
  padding-right: 0;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.2s, opacity 0.2s;
}

.car-card:hover .card-actions {
  max-height: 40px;
  opacity: 1;
}

.owner-name {
  font-size: 26px;
  font-weight: 600;
  margin: 0 0 8px 0;
  line-height: 1.2;
  transition: color 0.2s;
}

.car-plate {
  font-size: 18px;
  font-weight: 500;
  color: #374151;
  margin: 0 0 8px 0;
  line-height: 1.3;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ev-icon {
  font-size: 16px;
  color: #10b981;
  font-weight: 400;
}

.dept-name {
  font-size: 14px;
  font-weight: 400;
  color: #9ca3af;
  margin: 0;
}

.doc-btn {
  position: absolute;
  top: 0;
  right: 0;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  transition: color 0.2s;

  svg {
    width: 24px;
    height: 24px;
  }

  &:hover {
    color: #3b82f6;
  }
}

.delete-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #9ca3af;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;

  svg {
    width: 16px;
    height: 16px;
  }

  &:hover {
    color: #ffffff;
    background: #ee1d36;
    border-color: #ee1d36;
  }
}

// 空状态
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px 0;
  color: #9ca3af;
  font-size: 14px;
}

// 证件弹窗
.doc-content {
  .doc-car-info {
    font-size: 16px;
    font-weight: 500;
    color: #1a1a1a;
    margin: 0 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid #e5e7eb;
  }

  .doc-images {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .doc-image-item {
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid #e5e7eb;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      cursor: pointer;
      transition: transform 0.2s;

      &:hover {
        transform: scale(1.05);
      }
    }
  }

  .doc-empty {
    text-align: center;
    padding: 24px 0;
    color: #9ca3af;

    p {
      margin: 0 0 12px 0;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .car-list-container {
    padding: 16px;
  }

  .search-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .search-input-wrapper {
    width: 100%;
  }

  .car-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .car-card {
    padding: 20px 16px;
  }

  .owner-name {
    font-size: 22px;
  }

  .car-plate {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .car-grid {
    grid-template-columns: 1fr;
  }
}
</style>
