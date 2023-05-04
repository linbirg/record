<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span>{{teamName}}</span>
      <el-button type="primary" @click="exprot">导出</el-button>
    </div>
    <!-- 部门展示start -->
    <div class="team-block" v-if="groupWeekNotes" v-for="groupNote in groupWeekNotes" :key="groupNote.groupName">
      <p class="team-name">{{groupNote.groupName}}</p>
      <group
        :teamWeekNoteRisks="groupNote.groupNoteRisk"
        :editable="false"
        @showAddDialog="showAddDialog"
        @showDelDialong="showDelDialong"
        @showEditDialog="showEditDialog"/>
      <div class="meb-block" v-for="list in groupNote.weekNoteRisksList" :key="list.id">
        <member :list="list"/>
      </div>
    </div>
    <!-- 部门展示end -->
    <!-- 小组展示start -->
    <div v-if="weekNoteRisksList">
      <group
        :teamWeekNoteRisks="teamWeekNoteRisks"
        :editable="true"
        @showAddDialog="showAddDialog"
        @showDelDialong="showDelDialong"
        @showEditDialog="showEditDialog"/>
      <div class="meb-block" v-for="list in weekNoteRisksList" :key="list.id">
        <member :list="list"/>
      </div>
    </div>
    <!-- 小组展示end -->
    <!-- 个人展示start -->
    <member v-if="!groupWeekNotes && !weekNoteRisksList" :list="mebData"/>
    <!-- 个人展示end -->
    <!-- 弹框start -->
    <el-dialog 
    :visible.sync="dialogFormVisible"
    :close-on-click-modal="false"
    >
      <span slot="title" class="dialog-title">
        <!-- {{dialogTitle}} -->
      </span>
      <el-form :model="grpData">
        <el-form-item label="本周工作" :label-width="formLabelWidth">
          <el-input v-model="grpData.job" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="下周计划" :label-width="formLabelWidth">
          <el-input v-model="grpData.newJob" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="风险跟踪" :label-width="formLabelWidth">
          <el-input v-model="grpData.risk" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="预计解决时间" :label-width="formLabelWidth">
          <el-input v-model="grpData.riskSolveTime" placeholder="请输入日期"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" v-if="isAdd" @click="setGroupNoteRisk(1)">确 定</el-button>
        <el-button type="primary" v-if="!isAdd" @click="setGroupNoteRisk(2)">更 新</el-button>
      </div>
    </el-dialog>
    <!-- 弹窗组件 end -->
    <!-- 删除提示弹窗组件 start -->
    <el-dialog title="提示" :visible.sync="dialogDelVisible" width="30%">
      <span>确定删除该记录？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDelVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteGroupNoteRisk">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 删除提示弹窗组件 end -->
  </div>
</template>
<script>
import Group from './group'
import Member from './member'
export default {
  data() {
    return {
      // userId: '1',
      formLabelWidth: '120px',
      dialogFormVisible: false,
      dialogDelVisible: false,
      loading: false,
      isAdd: true,
      teamName: '',
      groupWeekNotes: [],    //一级查询结果
      weekNoteRisksList: [], //二级查询结果
      mebData: {},           //三级查询结果
      teamWeekNoteRisks: {},  //小组周报
      grpData: {
        userId: '',
        groupName: '',
        regDate: '',
        weekCount: '',
        job:'',
        newJob:'',
        risk:'',
        riskSolveTime:''
      }
    }
  },
  components: {
    Group,
    Member
  },
  computed: {
    userId() {
      return this.$store.state.userId
    }
  },
  mounted() {
    this.getWeekNoteRisks()
    this.getGroupWeekNoteRisks()
  },
  methods: {
    // 获取记录
    getWeekNoteRisks() {
      this.loading = true
      this.$store.dispatch('post', {
        url:'noteRisk/selectWeekNoteRisks.json',
        data: {userId: this.userId}
      }).then(response => {
        this.loading = false
        this.teamName = response.departmentName || response.groupName
        this.groupWeekNotes = response.groupWeekNotes
        this.weekNoteRisksList = response.weekNoteRisksList
        this.mebData = response
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '请求有误，请稍后重试',
          type: 'error'
        })
      })
    },
    // 查找小组周报
    getGroupWeekNoteRisks() {
      this.$store.dispatch('post', {
        url:'groupNoteRisk/selectGroupWeekNoteRisks.json',
        data: {userId: this.userId}
      }).then(response => {
        this.teamWeekNoteRisks = response
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '小组周报查询失败',
          type: 'error'
        })
      })
    },
    // 提交或更新小组周报
    setGroupNoteRisk(val) {
      let path = ''
      if(val === 1) {
        path = 'groupNoteRisk/submitGroupNoteRisk.json'
      } else {
        path = 'groupNoteRisk/updateGroupNoteRisk.json'
      }
      this.$store.dispatch('post', {
        url: path,
        data: this.grpData
      }).then(response => {
        this.getGroupWeekNoteRisks()
        this.dialogFormVisible = false
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '提交失败',
          type: 'error'
        })
      })
    },
    // 更新小组周报
    updateGroupNoteRisk() {

    },
    // 删除小组周报
    deleteGroupNoteRisk() {
      this.$store.dispatch('post', {
        url: 'groupNoteRisk/deleteGroupNoteRisk.json',
        data: {id: this.teamWeekNoteRisks.id}
      }).then(response => {
        this.getGroupWeekNoteRisks()
        this.dialogDelVisible = false
      }).catch(error => {
        this.$message({
          showClose: true,
          message: '删除失败',
          type: 'error'
        })
      })
    },
    // 显示添加弹窗
    showAddDialog() {
      this.setNewGrpData()
      this.dialogFormVisible = true
      this.isAdd = true
    },
    // 显示编辑弹窗
    showEditDialog() {
      this.setElderGrpDataBy()
      this.dialogFormVisible = true
      this.isAdd = false
    },
    showDelDialong() {
      this.dialogDelVisible = true
    },
    // 新加周报前数据设置
    setNewGrpData() {
      this.grpData.userId = this.userId
      this.grpData.groupName = this.teamName
      this.grpData.regDate = this.getDate()
      this.grpData.weekCount = this.weekNoteRisksList[0].weekCount
    },
    // 编辑周报前数据设置
    setElderGrpDataBy() {
      this.grpData = JSON.parse(JSON.stringify(this.teamWeekNoteRisks))
    },
    //获取当前时间设置为YY-MM-DD格式
    getDate() {
      var t = new Date();
      var y = t.getFullYear();
      var m = t.getMonth() + 1;
      var d = t.getDate();
      return y + '-' + m + '-' + d;
    },
    exprot() {
      window.open('/record/index')
    }
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
  .team-block {
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
  }
  .team-name{
    font-size: 16px;
    padding: 15px 10px;
  }
  // .meb-block {
  //   margin-top: 10px;
  // }
  // .meb-job {
  //   width: 85%;
  //   p {
  //     margin-bottom: 5px;
  //   }
  //   b {
  //     display: block;
  //   }
  //   i {
  //     font-size: 12px;
  //     color: #ed4014;
  //   }
  // }
  // .grp-wrapper {
  //   border-bottom: 1px solid #ebeef5;
  // }
  // .grp-name {
  //   width: 13%;
  //   font-size: 16px;
  //   text-align: center;
  // }
  // .inline {
  //   display: inline-block;
  //   vertical-align: top;
  // }
  // .inline-m {
  //   display: inline-block;
  //   vertical-align: middle;
  //   padding: 6px 0;
  // }
</style>