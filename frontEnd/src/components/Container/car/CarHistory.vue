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
            v-model="deleteSearch.carNo"
            placeholder="车牌号"
            style="width: 150px"
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
          <el-table-column prop="deleted_at" label="删除时间" />
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
            v-model="carnoSearch.carNo"
            placeholder="车牌号"
            style="width: 150px"
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
          <el-table-column prop="old_car_no" label="原车牌号" />
          <el-table-column prop="new_car_no" label="新车牌号" />
          <el-table-column prop="changed_at" label="变更时间" />
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
        carNo: '',
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
        carNo: '',
        dateRange: []
      },
      carnoQuery: {
        currentPage: 1,
        pageSize: 20
      }
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
          carNo: this.deleteSearch.carNo,
          startDate: this.deleteSearch.dateRange?.[0] || '',
          endDate: this.deleteSearch.dateRange?.[1] || ''
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
          carNo: this.carnoSearch.carNo,
          startDate: this.carnoSearch.dateRange?.[0] || '',
          endDate: this.carnoSearch.dateRange?.[1] || ''
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
</style>
