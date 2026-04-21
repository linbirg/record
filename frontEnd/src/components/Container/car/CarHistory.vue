<template>
  <el-dialog
    title="历史记录"
    :visible.sync="visible"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeTab">
      <el-tab-pane label="删除历史" name="delete">
        <div class="search-bar">
          <el-input
            v-model="deleteSearch.keyword"
            placeholder="车牌号或姓名搜索"
            style="width: 200px"
            @keyup.enter.native="loadDeleteHistory"
          />
          <el-date-picker
            v-model="deleteSearch.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            style="width: 240px"
          />
          <el-button @click="loadDeleteHistory">搜索</el-button>
        </div>

        <el-table :data="deleteList" v-loading="deleteLoading">
          <el-table-column prop="carid" label="车牌号" />
          <el-table-column prop="user_name" label="姓名" />
          <el-table-column prop="dept" label="部门" />
          <el-table-column prop="brand" label="品牌" />
          <el-table-column prop="deleted_at" label="删除日期" :formatter="formatDate" />
          <el-table-column label="图片" width="80" align="center">
            <template slot-scope="scope">
              <span v-if="scope.row.pics && scope.row.pics.length > 0">
                <el-popover
                  placement="top"
                  trigger="hover"
                  :open-delay="300"
                  :close-delay="300">
                  <div class="pic-popover">
                    <div class="pic-list">
                      <img
                        v-for="(pic, idx) in scope.row.pics.slice(0, 4)"
                        :key="idx"
                        :src="getPicUrl(pic)"
                        class="pic-thumb"
                        @click="previewPic(getPicUrl(pic))" />
                      <span v-if="scope.row.pics.length > 4" class="pic-more">
                        +{{ scope.row.pics.length - 4 }}
                      </span>
                    </div>
                  </div>
                  <span slot="reference" class="pic-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pic-icon">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                      <circle cx="8.5" cy="8.5" r="1.5" />
                      <polyline points="21,15 16,10 5,21" />
                    </svg>
                    {{ scope.row.pics.length }}
                  </span>
                </el-popover>
              </span>
              <span v-else class="pic-none">-</span>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          layout="total, prev, pager, next"
          :total="deleteTotal"
          :page-size="deleteQuery.pageSize"
          :current-page="deleteQuery.currentPage"
          @current-change="handleDeletePageChange"
        />
      </el-tab-pane>

      <el-tab-pane label="车牌号变更" name="carno">
        <div class="search-bar">
          <el-input
            v-model="carnoSearch.keyword"
            placeholder="姓名或车牌号搜索"
            style="width: 200px"
            @keyup.enter.native="loadCarNoHistory"
          />
          <el-date-picker
            v-model="carnoSearch.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            style="width: 240px"
          />
          <el-button @click="loadCarNoHistory">搜索</el-button>
        </div>

        <el-table :data="carnoList" v-loading="carnoLoading">
          <el-table-column prop="user_name" label="姓名" />
          <el-table-column prop="old_car_no" label="原车牌号" />
          <el-table-column prop="new_car_no" label="新车牌号" />
          <el-table-column prop="changed_at" label="变更日期" :formatter="formatDate" />
        </el-table>

        <el-pagination
          layout="total, prev, pager, next"
          :total="carnoTotal"
          :page-size="carnoQuery.pageSize"
          :current-page="carnoQuery.currentPage"
          @current-change="handleCarNoPageChange"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 图片预览弹窗 -->
    <el-dialog
      :visible.sync="previewVisible"
      width="60%"
      :close-on-click-modal="true"
      append-to-body>
      <img :src="previewUrl" style="width: 100%" />
    </el-dialog>
  </el-dialog>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'CarHistory',
  data() {
    return {
      visible: false,
      activeTab: 'delete',
      deleteList: [],
      deleteTotal: 0,
      deleteLoading: false,
      deleteSearch: {
        keyword: '',
        dateRange: []
      },
      deleteQuery: {
        currentPage: 1,
        pageSize: 20
      },
      carnoList: [],
      carnoTotal: 0,
      carnoLoading: false,
      carnoSearch: {
        keyword: '',
        dateRange: []
      },
      carnoQuery: {
        currentPage: 1,
        pageSize: 20
      },
      previewVisible: false,
      previewUrl: ''
    }
  },
  methods: {
    ...mapActions(['post']),
    open() {
      this.visible = true
      this.loadDeleteHistory()
    },
    loadDeleteHistory() {
      this.deleteLoading = true
      this.post({
        url: 'car/history',
        data: {
          currentPage: this.deleteQuery.currentPage,
          pageSize: this.deleteQuery.pageSize,
          keyword: this.deleteSearch.keyword,
          startDate: (this.deleteSearch.dateRange && this.deleteSearch.dateRange[0]) || '',
          endDate: (this.deleteSearch.dateRange && this.deleteSearch.dateRange[1]) || ''
        }
      }).then(res => {
        this.deleteList = res.records || []
        this.deleteTotal = res.total || 0
      }).finally(() => {
        this.deleteLoading = false
      })
    },
    handleDeletePageChange(page) {
      this.deleteQuery.currentPage = page
      this.loadDeleteHistory()
    },
    loadCarNoHistory() {
      this.carnoLoading = true
      this.post({
        url: 'car/car_no_history',
        data: {
          currentPage: this.carnoQuery.currentPage,
          pageSize: this.carnoQuery.pageSize,
          keyword: this.carnoSearch.keyword,
          startDate: (this.carnoSearch.dateRange && this.carnoSearch.dateRange[0]) || '',
          endDate: (this.carnoSearch.dateRange && this.carnoSearch.dateRange[1]) || ''
        }
      }).then(res => {
        this.carnoList = res.records || []
        this.carnoTotal = res.total || 0
      }).finally(() => {
        this.carnoLoading = false
      })
    },
    handleCarNoPageChange(page) {
      this.carnoQuery.currentPage = page
      this.loadCarNoHistory()
    },
    formatDate(row, column, cellValue) {
      if (!cellValue) return ''
      return cellValue.substring(0, 10)
    },
    getPicUrl(path) {
      return `/static/car/${path}`
    },
    previewPic(url) {
      this.previewUrl = url
      this.previewVisible = true
    }
  }
}
</script>

<style lang="scss" scoped>
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.pic-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  cursor: pointer;
  
  &:hover {
    color: #146ef5;
  }
}

.pic-icon {
  width: 14px;
  height: 14px;
}

.pic-none {
  color: #c0c4cc;
}

.pic-popover {
  .pic-list {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    max-width: 280px;
  }
  
  .pic-thumb {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 4px;
    cursor: pointer;
    border: 1px solid #e5e7eb;
    transition: transform 0.2s, box-shadow 0.2s;
    
    &:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }
  
  .pic-more {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    background: #f5f7fa;
    border-radius: 4px;
    color: #909399;
    font-size: 12px;
  }
}
</style>