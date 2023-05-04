<template>
  <el-pagination
    @current-change="handleCurrentChange"
    :page-size="10"
    layout="prev, pager, next, jumper"
    :total="totalItem">
  </el-pagination>
</template>
<script>
export default {
  props: {
    totalItem: {
			required: true
    },
    // currentPage: {
    //   required: true
    // }
  },

  methods: {
    handleCurrentChange(val) {
      this.$emit('handleCurrentChange', val)
    }
  },
}
</script>
<style lang="scss" scoped>
  .el-pagination {
    text-align: center;
  }
</style>



