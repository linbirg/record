<template>
  <div>
    <p class="meb-name inline">{{list.userName}}</p>
    <div class="meb-job inline">
      <p><b>本周工作：</b>{{list.job}}</p>
      <p><b>下周计划：</b>{{list.newJob}}</p>
      <p><b><i class="el-icon-warning"></i>风险跟踪：</b>{{list.risk}}</p>
      <p><b><i class="el-icon-warning"></i>预计完成时间：</b>{{list.riskSolveTime}}</p>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    list: {
      type: Object,
      required: true
    }
  }
}
</script>
<style lang="scss" scoped>
  .inline {
    display: inline-block;
    vertical-align: top;
  }
  .meb-name {
    width: 13%;
    font-size: 16px;
    text-align: center;
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
</style>