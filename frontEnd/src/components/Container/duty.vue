<template>
  <div>
    <div class="btn-item">
      <span>值班统计</span>
    </div>
    <div class="cat">
      <p class="month-tips">选择要查找的日期：</p>
      <el-date-picker
        v-model="timePeriod"
        type="daterange"
        value-format="yyyyMMdd"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change='search'>
      </el-date-picker>
      <p class="title-p">次数统计:</p>
      <el-table
        :data="dutyData"
        border
        stripe
        class="table">
        <el-table-column
          prop="userName"
          label="人员"
          width="220">
        </el-table-column>
        <el-table-column
          prop="dutyCount"
          label="值班次数">
        </el-table-column>
      </el-table>
      <p class="title-p">明细统计:</p>
      <el-table
        :data="dutyDetail"
        border
        stripe
        class="table">
        <el-table-column
          prop="userName"
          label="人员"
          width="220">
        </el-table-column>
        <el-table-column
          prop="dutyDate"
          label="值班日期">
        </el-table-column>
        <el-table-column
          prop="weekDay"
          label="星期">
        </el-table-column>
        <el-table-column
          prop="weekCount"
          label="周数">
        </el-table-column>
      </el-table>
      <!-- 分页组件start -->
      <Pagination
        :totalItem = "this.parsedTimePeriod.page.totalItem"
        @handleCurrentChange="handleCurrentChange"
      />
      <!-- 分页组件end -->
    </div>
  </div>
</template>
<script>
import {mapActions} from 'vuex'
import Pagination from '../pagination'
export default {
  components: {
    Pagination
  },
  data() {
    return {
      timePeriod: '',  //时间段
      dutyData: [],    //值班次数统计
      // detailDate: [],  
      dutyDetail: [],   //值班日期记录
      parsedTimePeriod:{
        startDate: '',
        endDate: '',
        page: {
          totalItem: 0,
          currentPage: 1,
          pageSize: 10,
          startItem: 0
        }
      }
    }
  },
  methods: {
    ...mapActions(['post']),
    search() {
      this.parsedTimePeriod.startDate = this.timePeriod[0]
      this.parsedTimePeriod.endDate = this.timePeriod[1]
      this.getWeekDutyCount()
      this.selectedTimeDutyByPage()
    },
    // 获得某月份的每人的值班次数
    getWeekDutyCount() {
      this.post({
        url: 'duty/weekDutyCount.json',
        data: this.parsedTimePeriod
      }).then(response => {
        this.dutyData = response
      }).catch(error => {
        // this.$message({
        //   showClose: true,
        //   message: '请求数据失败',
        //   type: 'error'
        // })
      })
    },

    // 每天值班明细
    selectedTimeDutyByPage() {
      this.post({
        url:'duty/selectedTimeDutyByPage.action',
        data: this.parsedTimePeriod
      }).then(response => {
        this.dutyDetail = response.selectedTimeDutyList
        this.parsedTimePeriod.page = response.page
      }).catch(
        // this.$message({
        //   showClose: true,
        //   message: '请求数据失败',
        //   type: 'error'
        // })
      )
    },

    // 翻页
    handleCurrentChange(val) {
      this.parsedTimePeriod.page.currentPage = val
      this.parsedTimePeriod.page.startItem = this.parsedTimePeriod.page.pageSize * (val - 1)
      this.search()
    },
    // 获取某人的值班明细
    // getWeekDutyDetail() {
    //   this.post({
    //     url: 'duty/weekDutyDetail.json',
    //     data: {
    //       userId: '1',
    //       dutyDate: this.timePeriod
    //     }
    //   }).then(response => {
    //     this.detailDate = response
    //   }).catch(error => {
    //     this.$message({
    //       showClose: true,
    //       message: '请求数据失败',
    //       type: 'error'
    //     })
    //   })
    // }
  }
}
</script>
<style lang="scss" scoped>
  .btn-item{
    height: 55px;
    padding: 0 50px;
    border-bottom: 1px solid #ebeef5;
    span {
      font-size: 22px;
    }
    button {
      float: right;
    }
  }
  .cat {
    margin: 20px;
    font-size: 16px;
    .month-tips {
      display: inline;
    }
    .table {
      margin-top: 20px;
    }
  }
  .title-p{
    margin-top: 20px;
  }
</style>
