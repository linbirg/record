<template>
  <header>
    <div v-if="typeId == 1" class="all-nav" @mouseenter="showNav" @mouseleave="hideNav"><i class="el-icon-menu"></i></div>
    <div>
      <img src="../assets/images/sge-logo.png" alt="">
      <h2>工作记录</h2>
    </div>
    <div class="log-out" v-if="!!userId">
      <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link"><i class="el-icon-user"></i> {{ userName }}
                <i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="resetPass"><i class="el-icon-setting"></i>重置密码</el-dropdown-item>
              <el-dropdown-item command="showAddDialog"><i class="el-icon-plus"></i> 添加用户</el-dropdown-item>
            <el-dropdown-item command="loginOut"><i class="el-icon-switch-button"></i>退出</el-dropdown-item>
            </el-dropdown-menu>
            </el-dropdown>
              </div>
              <div class="nav-dropdown" :class="{ active: isActive }"
                @mouseenter="showNav" @mouseleave="hideNav">
                <ul>
                  <!-- <li @click="goTo">工作记录</li> -->
                  <li @click="goTo">需求管理</li>
                </ul>
              </div>
              <!-- 弹窗组件 start -->
              <el-dialog
              :visible.sync="dialogFormVisible"
              :close-on-click-modal="false"
              width="40%"
              title="添加新用户"
              >
                <el-form :model="memberData" :label-position="labelPosition" :rules="rules" ref="memberData" label-width="80px">
                  <el-form-item label="账户" style="width:80%" prop="userName">
                    <el-input v-model="memberData.userName"></el-input>
                  </el-form-item>
                  <el-form-item label="姓名" style="width:80%" prop="nickname">
                    <el-input v-model="memberData.nickname"></el-input>
                  </el-form-item>
                  <el-form-item label="密码" style="width:80%" prop="password">
                    <el-input v-model="memberData.password" type="password"></el-input>
                  </el-form-item>
                  <el-form-item label="确认密码" style="width:80%" prop="checkPassword">
                    <el-input v-model="memberData.checkPassword" type="password"></el-input>
                  </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                  <el-button @click="dialogFormVisible = false">取 消</el-button>
                  <el-button
                    type="primary"
                    @click="submitForm('memberData')"
                  >确 定</el-button>
                </div>
              </el-dialog>
              <!-- 弹窗组件 end -->
              <!-- 弹窗组件 start -->
              <el-dialog
              :visible.sync="dialogResetVisible"
              :close-on-click-modal="false"
              width="40%"
              title="重置密码"
              >
                <el-form :model="memberData" :label-position="labelPosition" :rules="rules" ref="memberData" label-width="80px">
                  <el-form-item label="账户" style="width:80%" prop="userName">
                    <el-input v-model="memberData.userName" :disabled="true"></el-input>
                  </el-form-item>
                  <el-form-item label="姓名" style="width:80%" prop="nickname">
                    <el-input v-model="memberData.nickname" :disabled="true"></el-input>
                  </el-form-item>
                  <el-form-item label="密码" style="width:80%" prop="password">
                    <el-input v-model="memberData.password" type="password"></el-input>
                  </el-form-item>
                  <el-form-item label="确认密码" style="width:80%" prop="checkPassword">
                    <el-input v-model="memberData.checkPassword" type="password"></el-input>
                  </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                  <el-button @click="dialogResetVisible = false">取 消</el-button>
                  <el-button
                    type="primary"
                    @click="resetPasswd('memberData')"
                  >确 定</el-button>
                </div>
              </el-dialog>
              <!-- 弹窗组件 end -->
  </header>
</template>
<script>
// import { none } from 'html-webpack-plugin/lib/chunksorter';
import { mapActions } from 'vuex'
export default {
  data() {
    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'));
      } else {
        if (this.memberData.checkPassword !== '') {
          this.$refs.memberData.validateField('checkPassword');
        }
        callback();
      }
    };
    var validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.memberData.password) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    return {
      isActive: false,
      dialogFormVisible: false,
      dialogResetVisible: false,
      labelPosition: 'right',
      userName: '',
      typeId: 0, //组或公司标记
      roleId: 0,  //权限标记
      formLabelWidth: '80px',
      memberData: {
        userName: '',
        nickname: '',
        password: '',
        checkPassword: '',
        typeId: '',
        roleId: ''
      },
      rules: {
        userName: [
          { required: true, message: '请输入账户', trigger: 'blur' }
        ],
        nickname: [
          { required: true, message: '请输入真实姓名', trigger: 'blur' }
        ],
        password: [
          { required: true, validator: validatePass, trigger: 'blur' }
        ],
        checkPassword: [
          { required: true, validator: validatePass2, trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    userId() {
      // this.getUserNameBeforeSetDialog()
      return this.$store.state.userId
    }
  },
  mounted() {
    this.getUserNameBeforeSetDialog()
  },

  methods: {
    ...mapActions(['get', 'post']),
    showNav() {
      this.isActive = true
    },
    hideNav() {
      this.isActive = false
    },
    goTo() {
      window.location.href = '//180.3.13.229:9091/#/task'
    },
    // 登出
    handleCommand(command) {
      if (command == 'showAddDialog') {
        this.dialogFormVisible = true
      }
      if (command == 'resetPass') {
        this.getAndBindUserData()
        this.dialogResetVisible = true
      }
      if (command == 'loginOut') {
        this.$store.dispatch('loginOut').then(location.reload())
      }
    },
    // 根据userId获取userName和typeId
    getUserNameBeforeSetDialog() {
      let userId = this.$store.state.userId
      this.get({
        url: 'user/'
      }).then(response => {
        response.forEach(e => {
          if (e.user_id == userId) {
            this.userName = e.username
            this.typeId = e.typeId
            this.roleId = e.roleId
          }
        })
      }).catch(err => {
        console.log(err)
      })
    },

    // 根据userId加载用户信息并绑定到memberData
    getAndBindUserData() {
      let userId = this.$store.state.userId
      this.get({
        url: 'user/' + userId
      }).then(response => {
        console.log(response)
        this.memberData.userName = response.username, this.memberData.nickname = response.nickname
      }).catch(err => {
        console.log(err)
      })
    },

    // 提交表单前验证
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.addNewMember()
        } else {
          console.log('error submit!!')
          return false;
        }
      });
    },

    resetPasswd(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.post({
            url: 'user/' + this.userId + '/reset',
            data: { 'new_passwd': this.memberData.password }
          }).then(response => {
            this.dialogResetVisible = false
            this.$message.success('添加成功');
          }).catch(error => {
            this.$message.error(error);
          })
        } else {
          console.log('error submit!!')
          return false;
        }
      });
    },
    // 添加新用户
    addNewMember() {
      this.memberData.typeId = this.typeId
      this.memberData.roleId = this.roleId + 1
      this.post({
        url: 'user/submitUser.json',
        data: this.memberData
      }).then(response => {
        this.dialogFormVisible = false
        this.$message.success('添加成功');
      }).catch(error => {
        this.$message.error(error);
      })
    }
  }
}
</script>

<style lang="scss" scoped>
header, .nav-dropdown {
  position: fixed;
  color: #fff;
  background-color: #373d41;
  z-index: 10000;
}
header {
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  line-height: 54px;
  div, img, h2 {
    display: inline-block;
    vertical-align: middle;
  }
  img {
    width: 30px;
    height: 30px;
    margin-left: 20px;
  }
  .all-nav {
    width: 55px;
    font-size: 22px;
    text-align: center;
    border-right: 1px solid hsla(0,0%,100%,.15);
    transition: all .2s ease-in-out;
    &:hover {
      color: #409EFF;
      background-color: hsla(0,0%,100%,.15);
    }
  }
  .log-out{
    float: right;
    cursor: pointer;
    margin-right: 30px;
    .el-dropdown-link {
      color: #fff;
    }
  }
}

.nav-dropdown {
  top: 56px;
  left: -100px;
  width: 100px;
  text-align: center;
  font-size: 14px;
  border-top: 1px solid hsla(0,0%,100%,.15);
  transition: all .2s ease-in-out;
  &.active {
    left: 0;
  }
  li {
    cursor: pointer;
    &:hover {
      color: #409EFF;
    }
  }
}
</style>