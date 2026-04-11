<template>
  <div class="container" :style="{ marginRight: containerMargin }">
    <div class="cat-pad" :class="{ expanded: !chatVisible }">
      <router-view></router-view>
    </div>
  </div>
</template>
<script>
  import waves from "@/directive/waves/index.js";
  import { mapState } from "vuex";

  export default {
    directives: {
      waves,
    },
    computed: {
      ...mapState(['chatVisible']),
      containerMargin() {
        return this.chatVisible ? '600px' : '68px';
      }
    },
  };
</script>
<style lang="scss" scoped>
  .container {
    margin: 72px 220px;
    transition: margin-right 0.3s;
  }
  .cat-pad {
    width: 1100px;
    min-height: 400px;
    padding: 0px 0;
    background-color: #fff;
    font-size: 14px;
    border: 1px solid #ebeef5;
    -webkit-box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    color: #303133;
    transition: width 0.3s;

    &.expanded {
      width: 100%;
    }

    .btn-item {
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
      text-align: center;
      a {
        margin: 0 5px;
      }
    }
    .note {
      width: 765px;
    }
    .inline-t {
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
  .list-enter-active,
  .list-leave-active {
    transition: all 0.3s;
  }
  .list-enter,
  .list-leave-to {
    opacity: 0;
    transform: translateY(20px);
  }
</style>
