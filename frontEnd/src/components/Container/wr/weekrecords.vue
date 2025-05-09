<template>
  <el-card class="box-card">
    <div
      slot="header"
      class="clearfix">
      <strong
        ><span style="padding-right: 15px">WW({{ weekCount }})</span><span>{{ startDate }}-{{ endDate }}</span></strong
      >
      <!-- <el-button style="float: right; padding: 3px 0" type="text">操作按钮</el-button> -->
    </div>
    <div
      v-for="(n, index) in notes"
      :key="index">
      <Item
        :weekCount="n.weekCount"
        :monday="startDate"
        :weekDay="n.weekDay"
        :details="n.details"></Item>
    </div>
    <el-row>
      <el-col :span="2"
        ><a
          href="#"
          @click="loadLastWeek"
          style="float: right"
          ><i class="el-icon-d-arrow-left"></i></a
      ></el-col>
      <el-col :span="20"><span style="padding-right: 10px"></span></el-col>
      <el-col :span="2"
        ><a
          href="#"
          @click="loadNextWeek"
          style="float: left"
          ><i class="el-icon-d-arrow-right"></i></a
      ></el-col>
    </el-row>
  </el-card>
</template>

<style>
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both;
  }

  .box-card {
    width: 100%;
  }
</style>

<script>
  import { mapActions } from "vuex";
  import Item from "./item";
  import { dateParse, dateAdd, wwStartOf, wwEndOf } from "../../utils/index";

  export default {
    data() {
      return {
        weekCount: this.getYearWeek(this._get_ww_start_of(new Date())),
        startDate: this.getWWStart(),
        endDate: this.getWWEnd(),
        notes: [],
      };
    },
    mounted() {
      let userId = this.$store.state.userId;
      // alert(userId)
      this.loadCurWeek(userId, this.weekCount, new Date().getFullYear());
    },
    // 监听路由更新
    beforeRouteUpdate(to, from, next) {
      // userId = this.$store.userId
      // this.loadCurWeek(userId,this.weekCount)
      // next() //必须调用next()方法，否则钩子就不会被 resolved
    },
    components: {
      Item,
      // Tabs
    },

    methods: {
      ...mapActions(["get", "post"]),

      getYearWeek(t) {
        // var t = new Date();
        var y = t.getFullYear();
        var m = t.getMonth();
        var d = t.getDate();
        var date1 = new Date(y, m, d),
          date2 = new Date(y, 0, 1),
          c = Math.round((date1.valueOf() - date2.valueOf()) / 86400000);
        return Math.ceil((c + (date2.getDay() + 1 - 1)) / 7);
      },

      getWeekCnt(t) {
        /*
    date1是当前日期
    date2是当年第一天
    d是当前日期是今年第多少天
    用d + 当前年的第一天的周差距的和在除以7就是本年第几周
    */
        var y = t.getFullYear();
        var m = t.getMonth();
        var d = t.getDate();

        var date1 = new Date(y, m, d),
          date2 = new Date(y, 0, 1),
          d = Math.round((date1.valueOf() - date2.valueOf()) / 86400000);
        return Math.ceil((d + ((date2.getDay() || 1) - 1)) / 7);
      },

      getWWStart() {
        var t = new Date();
        let monday = this._get_ww_start_of(t);
        return dateParse(monday);
      },
      getWWEnd() {
        let sunday = this._get_ww_end_of(new Date());
        return dateParse(sunday);
      },

      _get_ww_start_of(t) {
        return wwStartOf(t);
      },

      _get_ww_end_of(t) {
        return wwEndOf(t);
      },

      loadCurWeek(userId, weekCount, year = 2025) {
        // alert(userId)
        console.log(year, weekCount);
        this.loading = true;
        this.post({
          url: "note/query",
          data: { userId: userId, weekCount: weekCount, year: year },
        })
          .then((response) => {
            this.loading = false;
            this.notes = response.note;
          })
          .catch((error) => {
            this.loading = false;
          });
      },
      loadLastWeek() {
        //this.weekCount = this.weekCount - 1;
        this.startDate = dateAdd(this.startDate, -7 * 24 * 60 * 60 * 1000);
        this.endDate = dateAdd(this.endDate, -7 * 24 * 60 * 60 * 1000);

        let userId = this.$store.state.userId;
        this.weekCount = this.getYearWeek(new Date(this.startDate));
        this.loadCurWeek(userId, this.weekCount, new Date(this.startDate).getFullYear());
      },
      loadNextWeek() {
        // this.weekCount = this.weekCount + 1;
        this.startDate = dateAdd(this.startDate, 7 * 24 * 60 * 60 * 1000);
        this.endDate = dateAdd(this.endDate, 7 * 24 * 60 * 60 * 1000);
        this.weekCount = this.getYearWeek(new Date(this.startDate));

        console.log(this.weekCount);
        let userId = this.$store.state.userId;
        this.loadCurWeek(userId, this.weekCount, new Date(this.startDate).getFullYear());
      },
    },
  };
</script>
<style lang="scss" scoped>
  // .title {
  //   font-size: 18px;
  //   border-bottom: 1px solid rgba(0,0,0,.06);
  //   background-color: #ddd;
  //   height: 36px;
  //   padding-top: 10px;
  //   // text-align: center;
  //   // align-items: center;
  //   .ww{
  //     // border-right: 1px red;
  //     padding-right: 15px;
  //   }
  // }

  // ul .wd{
  //   li{
  //     width:100px;
  //     float:left;
  //     display:block;
  //   }
  // }

  // .title .ww{
  //   padding-right: 5px;
  //   border-right: 1px red;
  // }
  // .inline {
  //   display: inline-block;
  //   vertical-align: top;
  //   padding-right: 0;
  //   p {
  //     padding-left: 0;
  //   }
  // }
  // .el-icon-edit, .el-icon-check, .el-icon-close, .el-icon-plus {
  //   float: right;
  //   padding: 5px;
  //   color: #9b9ea0;
  //   cursor: pointer;
  // }
  // .date-range, ul {
  //   color: #373d41;
  // }
  // .gray-ab {
  //   color: #888;
  //   span.obv {
  //     color: #373d41
  //   }
  // }
  // p, li {
  //   padding: 5px 15px;
  //   font-size: 16px;
  // }
  // li p {
  //   display: inline;
  // }
  // .date-input, .name-select {
  //   font-size: 16px;
  // }
  // .name-wrapper {
  //   display: inline-block;
  //   width: 80px;
  //   // &.obv {
  //   //   color: #ff5722;
  //   // }
  // }
</style>
