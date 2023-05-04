<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span>通讯录</span>
      <div class="search-wrapper">
        部门：
        <el-select
          v-model="department" placeholder="选择部门" 
          @change="selectAddressBookByDepartment"
        >
          <el-option
            v-for="item in departmentList"
            :key="item.index"
            :label="item.department"
            :value="item.department">
          </el-option>
        </el-select>
        姓名：
        <input class="name-input" type="text" v-model="cname" @keyup="filterKeyCode">
      </div>
    </div>
    <el-table
      :data="tableData"
      stripe
      border
      style="width: 100%">
      <el-table-column
        prop="department"
        label="部门"
        width="280">
      </el-table-column>
      <el-table-column
        prop="cname"
        label="姓名"
        width="120">
      </el-table-column>
      <el-table-column
        prop="tel"
        label="座机号"
        width="120">
      </el-table-column>
      <el-table-column
        prop="ext"
        label="分机号"
        width="80">
      </el-table-column>
      <el-table-column
        prop="phone"
        label="手机号">
      </el-table-column>
    </el-table>
  </div>
</template>
<script>
import waves from '@/directive/waves/index.js' // 水波纹指令
import { mapActions } from 'vuex'
export default {
  data() {
    return {
      loading: false,
      department: '技术开发中心',
      cname: '',
      tableData: [],
      departmentList: []
    }
  },
  
  mounted() {
    this.selectDepartment();
    this.selectAddressBookByDepartment();
  },
  // 自定义指令
  directives: {
    waves
  },

  methods: {
    ...mapActions(['get', 'post']),

    // 过滤键盘事件，只监听字母键，回车键，回退键，及中文输入是触发的229键
    filterKeyCode(e){
      const keyCode = e.keyCode
      if ((keyCode > 64 && keyCode < 91) || keyCode == 13 || keyCode == 8 || keyCode == 229) {
        this.selectAddressBookByCname()
      }
    },

    // 查找部门
    selectDepartment() {
      this.get({
        url:'addressBook/selectDepartment.action'
      }).then(response => {
        this.departmentList = response
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '部门分类查找失败,请稍后重试',
          type: 'error'
        })
      })
    },

    // 按部门查找
    selectAddressBookByDepartment() {
      this.post({
        url:'addressBook/selectAddressBookByDepartment.action',
        data:{department:this.department}
      }).then(response => {
        this.tableData = response
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '查找失败,请稍后重试',
          type: 'error'
        })
      })
    },
    
    // 按姓名查找
    selectAddressBookByCname() {
      if (this.cname == '') {
        this.selectAddressBookByDepartment()
      } else {
        this.post({
          url:'addressBook/selectAddressBookByCname.action',
          data:{cname: this.cname}
        }).then(response => {
          this.tableData = response
        }).catch(error => {
          this.$message({
            showClose: true,
            message: '查找失败,请稍后重试',
            type: 'error'
          })
        })
      }
    },
  }
}
</script>
<style lang="scss" scoped>
  .container {
    margin: 72px 225px;
  }
  .cat-pad {
    width: 900px;
    min-height: 400px;
    // border-radius: 4px;
    padding: 20px 0;
    background-color: #fff;
    font-size: 14px;
    border: 1px solid #ebeef5;
    -webkit-box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
    box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
    color: #303133;
    .btn-item{
      height: 55px;
      padding: 0 50px;
      border-bottom: 1px solid #ebeef5;
      span {
        font-size: 22px;
      }
    }
    .el-input {
      width: 200px;
    }
  }
  .search-wrapper{
    float: right;
  }
  .name-input {
    height: 40px;
    line-height: 40px;
    outline: 0;
    padding: 0 15px;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    box-sizing: border-box;
    color: #606266;
  }
</style>