<template>
  <div class="meb-block grp-wrapper" v-if="teamWeekNoteRisks.id">
    <div class="grp-name inline">
      <p v-if="editable">本组周报</p>
      <p>第{{teamWeekNoteRisks.weekCount}}周</p>
      <p>{{teamWeekNoteRisks.regDate}}</p>
      <a href="javascript:;" @click="showDelDialong" v-if="editable">删除</a>
      <a href="javascript:;" @click="showEditDialog" v-if="editable">编辑</a>
    </div>
    <div class="meb-job inline">
      <p><b>本周工作：</b>{{teamWeekNoteRisks.job}}</p>
      <p><b>下周计划：</b>{{teamWeekNoteRisks.newJob}}</p>
      <p><b><i class="el-icon-warning"></i>风险跟踪：</b>{{teamWeekNoteRisks.risk}}</p>
      <p><b><i class="el-icon-warning"></i>预计解决时间：</b>{{teamWeekNoteRisks.riskSolveTime}}</p>
    </div>
  </div>
  <div v-else class="grp-wrapper">
    <div class="grp-name inline-m">
      <p>本组周报</p>
    </div>
    <div class="meb-job inline">
      <el-button type="text" @click="showAddDialog">添加周报</el-button>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    teamWeekNoteRisks: {
      type: Object
    },
    editable: {
      type: Boolean,
      required: true
    }
  },
  methods: {
    showEditDialog() {
      this.$emit('showEditDialog')
    },
    showDelDialong() {
      this.$emit('showDelDialong')
    },
    showAddDialog() {
      this.$emit('showAddDialog')
    }
  }
}
</script>
<style lang="scss" scoped>
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


