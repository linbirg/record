<template>
  <div class="container">
    <div class="cat-pad">
      <router-view></router-view>
    </div>
  </div>
</template>
<script>
import waves from '@/directive/waves/index.js' // 水波纹指令
export default {
  // 自定义指令
  directives: {
    waves
  }
}
</script>
<style lang="scss" scoped>
  .container {
    margin: 72px 220px;
  }
  .cat-pad {
    width: 900px;
    min-height: 400px;
    // border-radius: 4px;
    padding: 0px 0;
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
    }
    .inline-t{
      display: inline-block;
      vertical-align: top;
    }
  }
  hr {
    border: 1px dashed #ccc;
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
</style>