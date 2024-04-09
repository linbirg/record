<template>
  <el-card class="box-card">
    <div
      slot="header"
      class="clearfix">
      <strong
        ><span style="padding-right: 15px">({{ year }}){{ month }}月简报</span></strong
      >
    </div>
    <div class="block">
      <el-timeline>
        <el-timeline-item
          v-for="(activity, index) in activities"
          :key="index"
          :timestamp="activity.timestamp"
          placement="top">
          <p
            v-for="(detail, index) in activity.details"
            :key="index">
            {{ detail }}
          </p>
        </el-timeline-item>
      </el-timeline>
    </div>
    <el-row>
      <el-col :span="1"
        ><a
          href="#"
          style="float: right"
          ><i class="el-icon-d-arrow-left"></i></a
      ></el-col>
      <el-col :span="22"><span style="padding-right: 10px"></span></el-col>
      <el-col :span="1"
        ><a
          href="#"
          style="float: left"
          ><i class="el-icon-d-arrow-right"></i></a
      ></el-col>
    </el-row>
  </el-card>
</template>

<script>
  import { mapActions } from "vuex";

  export default {
    data() {
      return {
        activities: [],
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
      };
    },
    mounted() {
      let userId = this.$store.state.userId;
      this.loadActivities(userId, 11);
    },

    methods: {
      ...mapActions(["get", "post"]),

      loadActivities(userId, month, year = 2022) {
        this.post({
          url: "reports/activity/query",
          data: { userId: userId, month: this.month, year: this.year },
        })
          .then((response) => {
            this.activities = response.activities;
          })
          .catch((error) => {
            console.log("error");
          });
      },
    },
  };
</script>
