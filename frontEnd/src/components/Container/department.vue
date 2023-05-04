<template>
  <div v-loading="loading">
    <div class="btn-item">
      <span>外围部</span>
    </div>
    <div class="part-block">
      <p class="part-title">本周工作内容
        <el-button type="text" @click="showAddDialog(1)">添加</el-button>
      </p>
      <div class="ctx-blk">
        <el-table
          :data="departmentNotes"
          border
          stripe>
          <el-table-column prop="projectName" label="项目" width="100"></el-table-column>
          <el-table-column prop="projectDetail" label="工作内容" min-width="200"></el-table-column>
          <el-table-column prop="groupName" label="开发组" width="80"></el-table-column>
          <el-table-column prop="manager" label="负责人" width="80"></el-table-column>
          <el-table-column prop="participants" label="参与人员" width="80"></el-table-column>
          <el-table-column label="操作" width="100" v-if="!jobDisdraggable">
            <template slot-scope="scope">
              <el-button
                size="mini"
                type="danger"
                @click="showDelDialog(1, scope.row)">删除</el-button>
              <el-button
                size="mini"
                type="primary"
                @click="showEditDialog(1, scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <div class="part-block">
      <p class="part-title">下周工作计划
        <el-button type="text" @click="showAddDialog(2)">添加</el-button>
      </p>
      <div class="ctx-blk">
        <el-table
          :data="nextDepartmentNotes"
          border
          stripe>
          <el-table-column prop="projectName" label="项目" width="100"></el-table-column>
          <el-table-column prop="projectDetail" label="工作内容" min-width="200"></el-table-column>
          <el-table-column prop="groupName" label="开发组" width="80"></el-table-column>
          <el-table-column prop="manager" label="负责人" width="80"></el-table-column>
          <el-table-column prop="participants" label="参与人员" width="80"></el-table-column>
          <el-table-column label="操作" width="100" v-if="!jobDisdraggable">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="danger"
                  @click="showDelDialog(2, scope.row)">删除</el-button>
                <el-button
                  size="mini"
                  type="primary"
                  @click="showEditDialog(2, scope.row)">编辑</el-button>
              </template>
            </el-table-column>
        </el-table>
      </div>
    </div>
    <div class="part-block">
      <p class="part-title">风险跟踪情况
        <el-button type="text" @click="showAddDialog(3)">添加</el-button>
      </p>
      <div class="ctx-blk">
        <el-table
          :data="departmentRisk"
          border
          stripe>
          <el-table-column prop="groupName" label="开发组" width="80"></el-table-column>
          <el-table-column prop="riskDetail" label="风险内容" min-width="200"></el-table-column>
          <el-table-column prop="manager" label="风险负责人" width="80"></el-table-column>
          <el-table-column prop="riskSolveTime" label="预计解决时间点" width="80"></el-table-column>
          <el-table-column label="操作" width="100" v-if="!jobDisdraggable">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="danger"
                  @click="showDelDialog(3, scope.row)">删除</el-button>
                <el-button
                  size="mini"
                  type="primary"
                  @click="showEditDialog(3, scope.row)">编辑</el-button>
              </template>
            </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 弹框start -->
    <el-dialog :visible.sync="dialogFormVisible">
      <span slot="title" class="dialog-title">
        <p v-if="isAdd">添加</p>
        <p v-if="!isAdd">编辑</p>
      </span>
      <el-form
        :model="temDepartmentNotes"
        v-if="submitFlag == 1 || submitFlag == 2 || updateFlag == 1 || updateFlag == 2">
        <el-form-item label="项目名称" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentNotes.projectName"></el-input>
        </el-form-item>
        <el-form-item label="工作内容" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentNotes.projectDetail" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="开发组" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentNotes.groupName"></el-input>
        </el-form-item>
        <el-form-item label="负责人" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentNotes.manager"></el-input>
        </el-form-item>
        <el-form-item label="参与人员" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentNotes.participants"></el-input>
        </el-form-item>
      </el-form>
      <el-form :model="temDepartmentRisk" v-else>
        <el-form-item label="开发组" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentRisk.groupName"></el-input>
        </el-form-item>
        <el-form-item label="风险内容" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentRisk.riskDetail" :autosize="{ minRows: 2, maxRows: 5}" auto-complete="off" type="textarea" resize="none"></el-input>
        </el-form-item>
        <el-form-item label="风险负责人" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentRisk.manager"></el-input>
        </el-form-item>
        <el-form-item label="预计解决时间点" :label-width="formLabelWidth">
          <el-input v-model="temDepartmentRisk.riskSolveTime"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" v-if="isAdd" @click="submitNote()">确 定</el-button>
        <el-button type="primary" v-if="!isAdd" @click="updateNote()">更 新</el-button>
      </div>
    </el-dialog>
    <!-- 弹窗组件 end -->
    <!-- 删除提示弹窗组件 start -->
    <el-dialog title="提示" :visible.sync="dialogDelVisible" width="30%">
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
import {require, getFormatDate} from '@/components/utils'
export default {
  data() {
    return {
      firstFlag: 0, //判断是否第一次进入本组件
      activeName: 'first',
      submitFlag: '',
      updateFlag: '',
      delFlag: '',
      delId: '',
      dialogFormVisible: false,
      dialogDelVisible: false,
      isAdd: true,
      lastDepartmentNotes: {},      //上周工作
      departmentNotes: [],          //本周工作
      nextDepartmentNotes: [],      //下周工作
      departmentRisk: [],           //风险跟踪
      temDepartmentNotes: {         //本周和下周工作提交对象
        id: '',
        projectName: '',
        projectDetail: '',
        regDate: '',
        weekCount: '',
        groupName: '',
        manager: '',
        participants: ''
      },
      temDepartmentRisk: {         //风险提交对象
        id: '',
        groupName: '',
        riskDetail: '',
        regDate: '',
        weekCount: '',
        manager: '',
        riskSolveTime: ''
      }
    }
  },
  mounted() {
    this.selectAllDepartmentNotes()
    this.selectAllNextDepartmentNotes()
    this.selectAllDepartmentRisks()
    // this.selectLastWeekDepartmentNoteRisks()
  },
  methods: {
    // 初始化数据
    initNote() {
      this.temDepartmentNotes.id = ''
      this.temDepartmentNotes.projectName = ''
      this.temDepartmentNotes.projectDetail = ''
      this.temDepartmentNotes.regDate = ''
      this.temDepartmentNotes.weekCount = ''
      this.temDepartmentNotes.groupName = ''
      this.temDepartmentNotes.manager = ''
      this.temDepartmentNotes.participants = ''
    },
    // 初始化风险数据
    initRisk() {
      this.temDepartmentRisk.id = '',
      this.temDepartmentRisk.groupName = '',
      this.temDepartmentRisk.riskDetail = '',
      this.temDepartmentRisk.regDate = '',
      this.temDepartmentRisk.weekCount = '',
      this.temDepartmentRisk.manager = '',
      this.temDepartmentRisk.riskSolveTime = ''
    },
    // 显示添加弹框
    showAddDialog(val) {
      this.submitFlag = val
      if (this.submitFlag === 3) {
        this.initRisk()
      } else {
        this.initNote()
      }
      this.dialogFormVisible = true
      this.isAdd = true
    },
    // 显示编辑弹窗
    showEditDialog(index, row) {
      this.updateFlag = index
      if (this.updateFlag === 3) {
        this.temDepartmentRisk = row
      } else {
        this.temDepartmentNotes = row
      }
      this.dialogFormVisible = true
      this.isAdd = false
    },
    // 显示删除弹框
    showDelDialog(index, row) {
      this.dialogDelVisible = true
      this.delFlag = index
      this.delId = row.id
    },
    // 提交操作
    submitNote() {
      this.dialogFormVisible = false
      if (this.submitFlag === 1) {
        this.submitDepartmentNote()
      }
      if (this.submitFlag === 2) {
        this.submitNextDepartmentNote()
      }
      if (this.submitFlag === 3) {
        this.submitDepartmentRisk()
      }
    },
    // 更新操作
    updateNote() {
      this.dialogFormVisible = false
      if (this.updateFlag === 1) {
        this.updateDepartmentNote()
      }
      if (this.updateFlag === 2) {
        this.updateNextDepartmentNote()
      }
      if (this.updateFlag === 3) {
        this.updateDepartmentRisk()
      }
    },
    //删除操作
    deleteNote() {
      this.dialogDelVisible = false
      // 删除本周
      if (this.delFlag === 1) {
        this.deleteDepartmentNote()
      }
      // 删除下周
      if (this.delFlag === 2) {
        this.deleteNextDepartmentNote()
      }
      // 删除风险
      if (this.delFlag === 3) {
        this.deleteDepartmentRisk()
      }
    },
    // 提交本周工作
    submitDepartmentNote() {
      let _this = this
      _this.temDepartmentNotes.regDate = getFormatDate()
      require({
        method: 'post',
        url:'departmentNote/submitDepartmentNote.json',
        data: _this.temDepartmentNotes,
        callback(response) {
          _this.selectAllDepartmentNotes()
        }
      })
    },
    // 更新本周工作
    updateDepartmentNote() {
      let _this = this
      require({
        method: 'post',
        url:'departmentNote/updateDepartmentNote.json',
        data: _this.temDepartmentNotes,
        callback(response) {
          _this.selectAllDepartmentNotes()
        }
      })
    },
    // 删除本周工作
    deleteDepartmentNote() {
      let _this = this
      require({
        method: 'post',
        url:'departmentNote/deleteDepartmentNote.json',
        data: {id: _this.delId},
        callback(response) {
          _this.selectAllDepartmentNotes()
        }
      })
    },
    // 查找本周工作
    selectAllDepartmentNotes() {
      let _this = this
      _this.firstFlag ++ 
      _this.departmentNotes = []
      this.loading = true
      require({
        method: 'get',
        url: 'departmentNote/selectAllDepartmentNotes.json',
        callback(response) {
          _this.loading = false
          if (response.length || _this.firstFlag > 1) { //有记录就显示记录否则显示上周计划
            _this.departmentNotes = response 
          } else {
            _this.selectLastWeekDepartmentNoteRisks()
          }
        }
      })
    },

    // 提交下周工作
    submitNextDepartmentNote() {
      let _this = this
      _this.temDepartmentNotes.regDate = getFormatDate()
      require({
        method: 'post',
        url:'nextDepartmentNote/submitNextDepartmentNote.json',
        data: _this.temDepartmentNotes,
        callback(response) {
          _this.selectAllNextDepartmentNotes()
        }
      })
    },
    // 更新下周工作
    updateNextDepartmentNote() {
      let _this = this
      require({
        method: 'post',
        url:'nextDepartmentNote/updateNextDepartmentNote.json',
        data: _this.temDepartmentNotes,
        callback(response) {
          _this.selectAllNextDepartmentNotes()
        }
      })
    },
    // 删除下周工作
    deleteNextDepartmentNote() {
      let _this = this
      require({
        method: 'post',
        url:'nextDepartmentNote/deleteNextDepartmentNote.json',
        data: {id: this.delId},
        callback(response) {
          _this.selectAllNextDepartmentNotes()
        }
      })
    },
    // 查找下周工作
    selectAllNextDepartmentNotes() {
      let _this = this
      require({
        method: 'get',
        url:'nextDepartmentNote/selectAllNextDepartmentNotes.json',
        callback(response) {
          _this.nextDepartmentNotes = response
        }
      })
    },
    // 提交风险跟踪
    submitDepartmentRisk() {
      let _this = this
      _this.temDepartmentRisk.regDate = getFormatDate()
      require({
        method: 'post',
        url:'departmentRisk/submitDepartmentRisk.json',
        data: _this.temDepartmentRisk,
        callback(response) {
          _this.selectAllDepartmentRisks()
        }
      })
    },
    // 更新风险跟踪
    updateDepartmentRisk() {
      let _this = this
      require({
        method: 'post',
        url:'departmentRisk/updateDepartmentRisk.json',
        data: _this.temDepartmentRisk,
        callback(response) {
          _this.selectAllDepartmentRisks()
        }
      })
    },
    // 删除风险跟踪
    deleteDepartmentRisk() {
      let _this = this
      require({
        method: 'post',
        url:'departmentRisk/deleteDepartmentRisk.json',
        data: {id: _this.delId},
        callback(response) {
          _this.selectAllDepartmentRisks()
        }
      })
    },
    // 查找风险跟踪
    selectAllDepartmentRisks() {
      let _this = this
      require({
        method: 'get',
        url:'departmentRisk/selectAllDepartmentRisks.json',
        callback(response) {
          _this.departmentRisk = response
        }
      })
    },
    // 查找上周工作记录
    selectLastWeekDepartmentNoteRisks() {
      let _this = this
      require({
        method: 'get',
        url:'departmentNote/selectLastWeekDepartmentNoteRisks.json',
        callback(response) {
          const arr = response.currentWeekDepartmentNoteList
          arr.forEach(e => {
            e.id = ''
            _this.temDepartmentNotes = e
            _this.submitDepartmentNote()
          })
        }
      })
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
  .part-block {
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
  }
  .part-title {
    font-size: 16px;
    padding: 0 20px;
    line-height: 42px
  }
  .ctx-blk {
    padding: 0 20px;
    .title {
      width: 100px;
      font-size: 16px;
    }
  }
  .team-name{
    font-size: 16px;
    padding: 15px 10px;
  }
  .meb-block {
    margin-top: 10px;
  }
  .meb-job {
    width: 85%;
    p {
      margin-bottom: 5px;
    }
    b {
      display: block;
    }
    i {
      font-size: 12px;
      color: #ed4014;
    }
  }
  .grp-wrapper {
    border-bottom: 1px solid #ebeef5;
  }
  .grp-name {
    width: 13%;
    font-size: 16px;
    text-align: center;
  }
  .inline {
    display: inline-block;
    vertical-align: top;
  }
  .inline-m {
    display: inline-block;
    vertical-align: middle;
    padding: 6px 0;
  }
</style>