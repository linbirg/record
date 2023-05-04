<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span>会议记录</span>
      <el-button
        v-waves
        type="primary"
        icon="el-icon-plus"
        @click="setDialogFormVisible"
      >新增</el-button>
    </div>
    <div v-if="meetings.length > 0">
      <transition-group name="list" tag="div">
        <div
          class="work-note"
          v-for="(meeting, index) in meetings"
          :key="meeting.id"
        >
          <div class="inline-t info">
            <p>会议时间</p>
            <p>{{meeting.regDate}}</p>
            <a href="#"
              @click="showDelDialong(index)"
            >删除</a>
            <a
              href="#"
              @click="editDialog(index)"
            >编辑</a>
          </div>
          <div class="inline-t note">
            <b>会议主题：</b>
            <p class="job">{{meeting.theme}}</p>
            <hr>
            <b>会议类型：</b>
            <p class="job" v-if="meeting.type">{{typeList[meeting.type-1].label}}</p>
            <hr>
            <b>会议记录：</b>
            <p class="new-job">{{meeting.detail}}</p>
            <hr>
            <b>参会人员：</b>
            <span>{{meeting.participants}}</span>
            <hr>
            <b>记录人：</b>
            <span>{{meeting.nickname}}</span>
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
      <el-form :model="meetingData" :rules="rules" ref="meetingData">
        <el-form-item label="会议主题" :label-width="formLabelWidth" prop="theme">
          <el-input v-model="meetingData.theme"></el-input>
        </el-form-item>
        <el-form-item label="会议类型" :label-width="formLabelWidth" prop="type">
          <el-select v-model="meetingData.type">
            <el-option v-for="type in typeList" :key="type.id" :label="type.label" :value="type.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="会议记录" :label-width="formLabelWidth" prop="detail">
          <el-input v-model="meetingData.detail" :rows="8" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="参会人员" :label-width="formLabelWidth" prop="participants">
          <el-input v-model="meetingData.participants"></el-input>
        </el-form-item>
        <el-form-item label="会议时间" :label-width="formLabelWidth" prop="regDate">
          <el-date-picker v-model="meetingData.regDate" placeholder="请选择日期" value-format="yyyy-MM-dd"></el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button
          type="primary"
          v-if="isAdd"
          @click="validate('meetingData')"
        >确 定</el-button>
        <el-button
          type="primary"
          v-if="!isAdd"
          @click="validate('meetingData')"
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
        userId: 0
      },
      meetingData: {
        userId: '',
        type:'',
        theme: '',
        detail: '',
        participants: '',
        regDate: ''
      },
      typeList: [
        {
          id:'1',
          label:'周会'
        },
        {
          id:'2',
          label:'需求讨论'
        },
        {
          id:'3',
          label:'代码评审'
        },
        {
          id:'4',
          label:'技术方案讨论'
        },
        {
          id:'5',
          label:'排期'
        }
      ],
      rules: {  //提交form验证
        theme: [{
          required: true, trigger: 'change', message: '请填写会议主题'
        }],
        type: [{
          required: true, trigger: 'change', message: '请填写会议类型'
        }],
        detail: [{
          required: true, trigger: 'change', message: '请填写会议记录'
        }],
        participants: [{
          required: true, trigger: 'change', message: '请填写参与人'
        }],
        regDate: [{
          required: true, trigger: 'change', message: '请选择时间'
        }]
      },
      meetings: [],
      dialogFormVisible: false,  //编辑新增弹窗是否可见
      dialogDelVisible: false,  //删除弹窗是否可见
      isAdd: true,
      formLabelWidth: '120px',
      dialogTitle: '新增',
      loading: false
    }
  },

  mounted() {
    this.selectMeetingByPage();
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
            this.addMeeting()
          } else {
            this.updateMeeting()
          }
        } else {
          console.log('error submit!!')
          return false;
        }
      })
    },
    //显示新增弹窗
    setDialogFormVisible() {
      // this.meetingData.userName = this.userName;
      this.meetingData.userId = this.$store.state.userId
      this.meetingData.theme = '';
      this.meetingData.type = '';
      this.meetingData.detail = '';
      this.meetingData.participants = '';
      this.meetingData.regDate = '';
      this.dialogFormVisible = true;
      this.dialogTitle = '新增';
      this.isAdd = true;
      this.$refs['meetingData'] && this.$refs['meetingData'].resetFields() //重置表单内容及验证条件，必须在dialog选然后才生效
    },

    // 显示编辑弹窗
    editDialog(index) {
      let meeting = this.meetings[index];
      this.dialogFormVisible = true;
      this.dialogTitle = '编辑';
      this.isAdd = false;
      this.id = meeting.id;
      this.meetingData.userId = this.$store.state.userId
      this.meetingData.theme = meeting.theme;
      this.meetingData.type = String(meeting.type);
      this.meetingData.detail = meeting.detail;
      this.meetingData.participants = meeting.participants;
      this.meetingData.regDate = meeting.regDate;
    },

    // 根据userId获取userName和typeId
    // getUserNameBeforeSetDialog() {
    //   let userId = this.pageData.userId
    //   this.get({
		// 		url: 'user/showUser.do?userId=0'
		// 	}).then(response => {
		// 		response.forEach(e => {
    //       if (e.userId == userId) {
    //         this.userName = e.nickname
    //         this.pageData.typeId = e.typeId
    //         this.meetingData.typeId = e.typeId
    //         this.setDialogFormVisible()
    //       }
		// 		})
		// 	}).catch(err => {
		// 		console.log(err)
		// 	})
		// },

    // 按页查找meeting数据
    selectMeetingByPage() {
      this.loading = true
      this.post({
        url: 'meeting/selectMeetingByPage.action',
        data: this.pageData
      }).then(response => {
        this.loading = false
        this.meetings = response.meeting
        this.pageData = response.page
      }).catch(error => {
        this.loading = false
      })
    },

    // 新增数据
    addMeeting() {
      // this.meetingData.regDate = this.getDate();
      // this.meetingData.weekCount = this.getYearWeek();
      this.post({
        url: 'meeting/submitMeeting.action',
        data: this.meetingData
      }).then(response => {
        this.dialogFormVisible = false
        this.selectMeetingByPage()
      }).catch(() => {
        this.$message({
          showClose: true,
          message: '请求有误，请稍后重试',
          type: 'error'
        })
      })
    },

    // 编辑数据
    updateMeeting() {
      this.post({
        url: 'meeting/updateMeeting.action',
        data: {
          id: this.id,
          userId: this.meetingData.userId,
          type: this.meetingData.type,
          theme: this.meetingData.theme,
          detail: this.meetingData.detail,
          participants: this.meetingData.participants,
          regDate: this.meetingData.regDate
        }
      }).then(() => {
        this.dialogFormVisible = false
        this.selectMeetingByPage()
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
        url: 'meeting/deleteMeetingById.action',
        data: {id: this.id}
      }).then(() => {
        this.dialogDelVisible = false
        this.selectMeetingByPage()
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
      this.selectMeetingByPage()
    },

    // 显示删除提示框
    showDelDialong(index) {
      this.id = this.meetings[index].id;
      this.dialogDelVisible = true;
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
  .no-data {
    text-align: center;
    padding: 20px 0;
  }
</style>
