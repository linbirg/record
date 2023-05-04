<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span v-if="!editable">全体工作记录</span>
      <span v-if="editable">个人工作记录</span>
      <el-button
        v-waves
        type="primary"
        icon="el-icon-plus"
        v-if="editable"
        @click="getUserNameBeforeSetDialog"
      >新增</el-button>
      <div v-if="showSearch" class="search-bar">
        <!-- searchString 模型与文本域创建绑定 -->
        <input v-if="showSearch" class="name-input" type="text" @keyup.enter="queryNoteByUserName" v-model="pageData.userName" placeholder="输入名字" />
      </div>
 
    </div>
    <div v-if="this.pageData.totalItem > 0">
    <transition-group name="list" tag="div">
      <div
        class="work-note"
        v-if="notes"
        v-for="(note, index) in notes"
        :key="note.id"
      >
        <div class="inline-t info">
          <p>{{note.userName}}</p>
          <p>第{{note.weekCount}}周</p>
          <p>{{note.regDate}}</p>
          <a href="#"
            v-if="editable"
            @click="showDelDialong(index)"
          >删除</a>
          <a
            href="#"
            v-if="editable"
            @click="editDialog(index)"
          >编辑</a>
        </div>
        <div class="inline-t note">
          <b>本周工作：</b>
          <p class="job">{{note.job}}</p>
          <hr>
          <b>下周计划：</b>
          <p class="new-job">{{note.newJob}}</p>
          <hr>
          <b><i class="el-icon-warning"></i>风险跟踪：</b>
          <p class="job">{{note.risk}}</p>
          <b><i class="el-icon-warning"></i>预计完成时间：</b>
          <p class="job">{{note.riskSolveTime}}</p>
        </div>
      </div>
    </transition-group>
    </div>
    <div v-else>
      <p class="no-data">暂无记录</p>
    </div>
    <!-- 分页组件start -->
    <Pagination
      :totalItem = "this.pageData.totalItem"
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
      <el-form :model="noteData">
        <el-form-item label="本周工作" :label-width="formLabelWidth">
          <el-input v-model="noteData.job" :autosize="{ minRows: 2, maxRows: 8}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="下周计划" :label-width="formLabelWidth">
          <el-input v-model="noteData.newJob" :autosize="{ minRows: 2, maxRows: 8}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="风险跟踪" :label-width="formLabelWidth">
          <el-input v-model="noteData.risk" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="预计解决时间" :label-width="formLabelWidth">
          <el-input v-model="noteData.riskSolveTime" placeholder="请输入日期"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button
          type="primary"
          v-if="isAdd"
          @click="addRecord"
        >确 定</el-button>
        <el-button
          type="primary"
          v-if="!isAdd"
          @click="updateRecord"
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
        <el-button type="primary" @click="deleteNote()">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 删除提示弹窗组件 end -->
  </div>
</template>
<script>
import waves from '@/directive/waves/index.js' // 水波纹指令
import Pagination from '../pagination'
import {getWeekCount} from '../utils/index'
import { mapActions } from 'vuex'
export default {
  components: {
    Pagination
  },
  data() {
    return {
      id: 0, //单独条目的id
      userName: '',
      pageData: {
        totalItem: 0,
        currentPage: 1,
        pageSize: 10,
        startItem: 0,
        userId: 0,
        typeId: 0,
        userName: ''
      },
      noteData: {
        userId: '',
        typeId: '',
        userName: '',
        weekCount: '',
        regDate: '',
        newJob: '',
        job: '',
        risk: '',
        riskSolveTime: ''
      },
      notes: [],
      editable: false,
      showSearch: false,
      dialogFormVisible: false,  //编辑新增弹窗是否可见
      dialogDelVisible: false,  //删除弹窗是否可见
      isAdd: true,
      formLabelWidth: '120px',
      dialogTitle: '新增',
      loading: false
    }
  },
  // 监听路由更新
  beforeRouteUpdate(to, from, next) {
    const type = to.params.type
    this.pageData.currentPage = 1
    this.pageData.startItem = 0
    this.doSelectNoteRiskByPage(type)
    next() //必须调用next()方法，否则钩子就不会被 resolved
  },
  mounted() {
    const type = this.$route.params.type
    this.doSelectNoteRiskByPage(type)
  },
  // 自定义指令
  directives: {
    waves
  },  

  methods: {
    ...mapActions(['get', 'post']),
    // 根据tpye类型设置typeId,userId,editable后请求数据
    doSelectNoteRiskByPage(type) {
      if (type == 'all') {
        this.pageData.typeId = this.$store.state.typeId
        this.pageData.userId = 0
        this.editable = false
        this.showSearch = true
      }
      if (type == 'personal') {
        this.pageData.typeId = this.$store.state.typeId
        this.pageData.userId = this.$store.state.userId
        this.editable = true
        this.showSearch = false
      }
      if (type == 'primeton') {
        this.pageData.typeId = 2
        this.pageData.userId = 0
        this.editable = false
        this.showSearch = true
      }
      if (type == 'handsun') {
        this.pageData.typeId = 3
        this.pageData.userId = 0
        this.editable = false
        this.showSearch = true
      }
      this.selectNoteRiskByPage()
    },
    //显示新增弹窗
    setDialogFormVisible() {
      this.noteData.userName = this.userName;
      this.noteData.userId = this.$store.state.userId
      this.noteData.typeId = this.$store.state.typeId
      this.noteData.newJob = '';
      this.noteData.job = '';
      this.noteData.risk = '';
      this.noteData.riskSolveTime = '';
      this.dialogFormVisible = true;
      this.dialogTitle = '新增';
      this.isAdd = true;
    },

    // 显示编辑弹窗
    editDialog(index) {
      let note = this.notes[index];
      this.dialogFormVisible = true;
      this.dialogTitle = '编辑';
      this.isAdd = false;
      this.id = note.id;
      this.noteData.newJob = note.newJob;
      this.noteData.job = note.job;
      this.noteData.risk = note.risk;
      this.noteData.riskSolveTime = note.riskSolveTime;
    },

    // 根据userId获取userName和typeId
    getUserNameBeforeSetDialog() {
      let userId = this.pageData.userId
      this.get({
				url: 'user/'
			}).then(response => {
				response.forEach(e => {
          if (e.userId == userId) {
            this.userName = e.nickname
            this.pageData.typeId = e.typeId
            this.noteData.typeId = e.typeId
            this.setDialogFormVisible()
          }
				})
			}).catch(err => {
				console.log(err)
			})
		},

    // 按页和username查找note数据,带risk项
    queryNoteByUserName(e) {
      if (this.pageData.userName == '') {
        this.$message({
          showClose: true,
          message: '查询条件不能为空！',
          type: 'warning'
        });
        return;
      }
      this.loading = true;
      this.post({
        url: 'noteRisk/queryNoteRiskByUserName.action',
        data: this.pageData
      }).then(response => {
        this.loading = false
        this.notes = response.note
        this.pageData = response.page
        if (this.pageData.totalItem <= 0) {
          this.$message({
            showClose: true,
            message: '查无此人！',
            type: 'warning'
          })}
      }).catch(error => {
          this.$message({
            showClose: true,
            message: '查找失败,请稍后重试',
            type: 'error'
          })
      })
      
    },

    // 按页查找note数据,带risk项
    selectNoteRiskByPage() {
      this.loading = true
      this.post({
        url: 'noteRisk/selectNoteRiskByPage.action',
        data: this.pageData
      }).then(response => {
        this.loading = false
        this.notes = response.note
        this.pageData = response.page
      }).catch(error => {
        this.loading = false
      })
    },

    // 新增数据
    addRecord() {
      if (this.noteData.newJob.trim()) {
        this.noteData.regDate = this.getDate();
        this.noteData.weekCount = this.getYearWeek();
        this.post({
          url: 'noteRisk/submitNoteRisk.action',
          data: this.noteData
        }).then(response => {
          this.dialogFormVisible = false
          this.selectNoteRiskByPage()
        }).catch(() => {
          this.$message({
            showClose: true,
            message: '请求有误，请稍后重试',
            type: 'error'
          })
        })
      }
    },

    // 编辑数据
    updateRecord() {
      this.post({
        url: 'noteRisk/updateNoteRisk.json',
        data: {
          id: this.id,
          job: this.noteData.job,
          newJob: this.noteData.newJob,
          risk: this.noteData.risk,
          riskSolveTime: this.noteData.riskSolveTime
        }
      }).then(() => {
        this.dialogFormVisible = false
        this.selectNoteRiskByPage()
      }).catch(() => {
        this.$message({
          showClose: true,
          message: '请求有误，请稍后重试',
          type: 'error'
        })
      })
    },

    // 删除数据
    deleteNote() {
      const id = this.id;
      this.post({
        url: 'noteRisk/deleteNoteRisk.json',
        data: {id: this.id}
      }).then(() => {
        this.dialogDelVisible = false
        this.selectNoteRiskByPage()
      }).catch(() => {
        this.$message({
          showClose: true,
          message: '请求有误，请稍后重试',
          type: 'error'
        })
      })
    },

    // 翻页
    handleCurrentChange(val) {
      this.loading = true
      // this.pageData = this.$store.state.page
      this.pageData.currentPage = val
      this.pageData.startItem = this.pageData.pageSize * (val - 1)
      if(this.pageData.userName != ''){
        this.queryNoteByUserName()
      }else{
        this.selectNoteRiskByPage()
      }
    },

    // 显示删除提示框
    showDelDialong(index) {
      this.id = this.notes[index].id;
      this.dialogDelVisible = true;
    },

    // 判断第几周
    getYearWeek() {
      var t = new Date();
      var y = t.getFullYear();
      var m = t.getMonth();
      var d = t.getDate();
      var date1 = new Date(y, m, d),
          date2 = new Date(y, 0, 1),
          c = Math.round((date1.valueOf() - date2.valueOf()) / 86400000);
      return Math.ceil((c + ((date2.getDay() + 1) - 1)) / 7);
    },

    //获取当前时间设置为YY-MM-DD格式
    getDate() {
      var t = new Date();
      var y = t.getFullYear();
      var m = t.getMonth() + 1;
      var d = t.getDate();
      return y + '-' + m + '-' + d;
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
    .work-note {
      width: 100%;
      margin: 10px auto 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid #ccc;
    }
    .info {
      width: 120px;
      // margin-right: 20px;
      text-align: center;
      a{
        margin:0 5px;
      }
    }
    .note {
      width: 765px;
      i {
        color: #ed4014;
        font-size: 12px;
      }
    }
    .inline-t{
      display: inline-block;
      vertical-align: top;
    }
  }
  hr {
    border: .5px dashed #ccc;
    margin: 5px 0;
  }
  .dialog-title {
    line-height: 24px;
    font-size: 18px;
    color: #303133;
  }
  textarea {
    width: 600px;
  }
  .list-enter-active, .list-leave-active {
    transition: all .3s;
  }
  .list-enter, .list-leave-to {
    opacity: 0;
    transform: translateY(20px);
  }
  .search-bar {
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
  .no-data {
  text-align: center;
  padding: 20px 0;
  }
</style>