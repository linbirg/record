<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span>机器资源</span>
      <el-button
        v-waves
        type="primary"
        icon="el-icon-plus"
        @click="showAddDialog"
      >新增</el-button>
    </div>
    <el-table
      :data="tableData"
      stripe
      border
      style="width: 100%">
      <el-table-column
        prop="systemName"
        label="系统">
      </el-table-column>
      <el-table-column
        prop="ip"
        label="IP">
      </el-table-column>
      <el-table-column
        prop="envCN"
        label="环境">
      </el-table-column>
      <el-table-column
        prop="resourceInfo"
        label="机器信息">
      </el-table-column>
      <el-table-column
        prop="abbr"
        label="备注">
      </el-table-column>
      <el-table-column
        label="操作">
        <template slot-scope="scope">
          <el-button @click="showEditDialog(scope.row)" type="text" size="small">编辑</el-button>
          <el-button @click="showDelDialog(scope.row)" type="text" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件start -->
    <Pagination
      :totalItem = "this.pageData.totalItem"
      :currentPage = "this.pageData.currentPage"
      @handleCurrentChange="handleCurrentChange"
    />
    <!-- 分页组件end -->
    <!-- 弹窗组件 start -->
    <el-dialog
    :visible.sync="dialogFormVisible"
    :close-on-click-modal="false"
    >
      <span slot="title" class="dialog-title">
        {{dialogTitle}}
      </span>
      <el-form :model="mechineInfo" :rules="rules" ref="mechineInfo">
        <el-form-item label="系统" :label-width="formLabelWidth" prop="systemName">
          <el-input v-model="mechineInfo.systemName"></el-input>
        </el-form-item>
        <el-form-item label="IP" :label-width="formLabelWidth" prop="ip">
          <el-input v-model="mechineInfo.ip"></el-input>
        </el-form-item>
        <el-form-item label="环境" :label-width="formLabelWidth" prop="environment">
          <el-select
            class="name-select"
            v-model="mechineInfo.environment"
          >
            <el-option
              v-for="item in env"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="机器信息" :label-width="formLabelWidth" prop="resourceInfo">
          <el-input v-model="mechineInfo.resourceInfo"></el-input>
        </el-form-item>
        <el-form-item label="备注" :label-width="formLabelWidth" prop="abbr">
          <el-input v-model="mechineInfo.abbr"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button
          type="primary"
          v-if="isAdd"
          @click="validate('mechineInfo')"
        >确 定</el-button>
        <el-button
          type="primary"
          v-if="!isAdd"
          @click="validate('mechineInfo')"
        >更 新</el-button>
      </div>
    </el-dialog>
    <!-- 弹窗组件 end -->
    <!-- 删除提示弹窗组件 start -->
    <el-dialog
      title="提示"
      :visible.sync="dialogDelVisible"
      width="30%"
    >
      <span>确定删除该记录？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDelVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteMachineResource()">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 删除提示弹窗组件 end -->
  </div>
</template>
<script>
import waves from '@/directive/waves/index.js' // 水波纹指令
import Pagination from '../pagination'
import { mapActions } from 'vuex'
export default {
  components: {
    Pagination
  },
  data() {
    return {
      loading: false,
      isAdd: true,
      formLabelWidth: '120px',
      dialogFormVisible: false,
      dialogDelVisible: false,
      dialogTitle: '',
      delId: '',
      tableData: [],
      mechineInfo: {
        systemName: '',
        ip: '',
        environment: '',
        resourceInfo: '',
        abbr: ''
      },
      pageData: {
        totalItem: 0,
        currentPage: 1,
        pageSize: 10,
        startItem: 0,
        userId: 0,
        typeId: 0,
        userName: ''
      },
      envInfo: {
        1: '生产',
        2: '开发'
      },
      env: [{
        value: 1,
        label: '生产'
      },{
        value: 2,
        label: '开发'
      }],
      rules: {  //提交form验证
        systemName: [{
          required: true, trigger: 'change', message: '请填写系统名称'
        }],
        ip: [{
          required: true, trigger: 'change', message: '请填写ip'
        }],
        environment: [{
          required: true, trigger: 'change', message: '请选择环境'
        }],
        resourceInfo: [{
          required: true, trigger: 'change', message: '请填写机器信息'
        }]
      }
    }
  },
  
  mounted() {
    this.selectMachineResourceByPage();
  },
  // 自定义指令
  directives: {
    waves
  },

  methods: {
    ...mapActions(['get', 'post']),

    //表单验证
    validate(formName, operation) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (this.isAdd) {
            this.submitMachineResource()
          } else {
            this.updateMachineResource()
          }
        } else {
          console.log('error submit!!')
          return false;
        }
      })
    },

    // 添加机器资源信息
    submitMachineResource() {
      this.post({
        url:'machine/submitMachineResource.action',
        data: this.mechineInfo
      }).then(response => {
        this.dialogFormVisible = false
        this.selectMachineResourceByPage()
      }).catch(error => {
        this.errorMessage('添加')
      })
    },

    // 删除机器资源信息
    deleteMachineResource() {
      this.post({
        url:'machine/deleteMachineResource.action',
        data: {id: this.delId}
      }).then(response => {
        this.dialogDelVisible = false
        this.selectMachineResourceByPage()
      }).catch(error => {
        this.errorMessage('删除')
      })
    },

    // 修改机器资源信息
    updateMachineResource() {
      this.post({
        url:'machine/updateMachineResource.action',
        data: this.mechineInfo
      }).then(response => {
        this.dialogFormVisible = false
        this.selectMachineResourceByPage()
      }).catch(error => {
        this.errorMessage('修改')
      })
    },

    // 查找机器资源信息
    selectMachineResourceByPage() {
      this.loading = true
      this.post({
        url:'machine/selectMachineResourceByPage.action',
        data: this.pageData
      }).then(response => {
        this.loading = false
        this.tableData = response.machineResource
        this.pageData = response.page
        this.formatData(this.tableData)
      }).catch(error => {
        this.loading = false
        this.errorMessage('查找')
      })
    },

    // 翻页
    handleCurrentChange(val) {
      this.pageData.currentPage = val
      this.pageData.startItem = this.pageData.pageSize * (val - 1)
      this.selectMachineResourceByPage()
    },

    // 显示新增弹框
    showAddDialog() {
      this.isAdd = true
      this.mechineInfo = {}
      this.dialogFormVisible = true
      this.dialogTitle = '新增'
      this.$refs['mechineInfo'] && this.$refs['mechineInfo'].resetFields() //重置表单内容及验证条件，必须在dialog选然后才生效
    },

    // 显示修改弹框
    showEditDialog(data) {
      this.isAdd = false
      this.mechineInfo = JSON.parse(JSON.stringify(data)) //简单深拷贝，防止内存引用重复
      this.dialogFormVisible = true
      this.dialogTitle = '编辑'
    },

    // 显示删除弹窗
    showDelDialog(data) {
      this.dialogDelVisible = true
      this.delId = data.id
    },

    // environment数字码转为对应的汉字名称
    formatData(data) {
      data.forEach(e => {
        e.environment = e.environment * 1
        this.$set(e, 'envCN', this.envInfo[e.environment])
      })
    },

    // 失败弹窗
    errorMessage(text) {
      this.$message({
        showClose: true,
        message: text+'机器资源信息失败,请稍后重试',
        type: 'error'
      })
    }
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
      button {
        float: right;
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
  .dialog-title {
    line-height: 24px;
    font-size: 18px;
    color: #303133;
  }
  
  .el-form-item {
    display: inline-block;
  }
</style>