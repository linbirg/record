<template>
  <el-row class="dt-row">
    <el-col
      :span="22"
      class="">
      <!-- <input type="checkbox" class="toggle"  v-model="input_item.completed" @change="postToUpdateItem"> -->
      <el-checkbox
        v-model="input_item.completed"
        @change="postToUpdateItem"></el-checkbox>
      <label class="line-1">{{ index + 1 }}</label>
      <el-input
        style="width: 80%"
        v-if="is_editable"
        v-model="input_item.desc"
        @keyup.enter.native="enter_disable_input"
        placeholder="计划做的事情"></el-input>
      <label
        v-else
        class="line-2"
        @dblclick="detail_text_click"
        >{{ input_item.desc }}</label
      >
    </el-col>

    <el-col :span="2">
      <span
        class="destroy"
        @click="detail_text_click"
        ><i class="el-icon-edit"></i
      ></span>
      <span
        class="destroy"
        @click="deleteCurrentItem"
        ><i class="el-icon-remove-outline"></i
      ></span>
    </el-col>
  </el-row>
</template>

<script>
  import { mapActions } from "vuex";
  //   import { format } from "date-fns";
  //   import { zhCN } from "date-fns/locale";

  export default {
    props: {
      index: {
        type: Number,
        required: true,
      },
      item: {
        type: Object,
        required: true,
      },
      weekCount: {
        type: Number,
        required: true,
      },

      weekDay: {
        type: Number,
        required: true,
      },
      monday: {
        type: String,
        default: false,
      },

      editable: {
        type: Boolean,
        default: false,
      },
    },

    computed: {
      is_editable() {
        // console.log('this.item')
        // console.log(this.item.desc)
        if (this.just_inited && JSON.stringify(this.item) == "{}") {
          return true;
        }

        if (this.dt_editable) return true;
      },
    },
    data() {
      return {
        dt_editable: this.editable,
        just_inited: true,
        // input_item:JSON.stringify(this.item) == "{}"?{desc:''}:this.item
        input_item: this.init_edit_input(),
      };
    },
    methods: {
      ...mapActions(["get", "post"]),
      detail_text_click() {
        // alert(this.detail.desc);
        this.dt_editable = true;
        this.input_item = this.init_edit_input();
      },
      init_edit_input() {
        let item_temp = JSON.stringify(this.item) == "{}" ? { desc: "" } : this.item;
        console.log("init_edit_input");
        console.log(item_temp.desc);
        return item_temp;
      },
      blur_handle() {
        console.log("blur_handle");
        this.disable_input();
      },
      enter_disable_input() {
        console.log("enter_disable_input");
        this.disable_input();
      },

      disable_input() {
        this.just_inited = false;
        this.dt_editable = false;
        if (typeof this.input_item.no == "undefined") {
          this.postToInsertItem();
        } else {
          this.postToUpdateItem();
        }
      },

      deleteCurrentItem() {
        this.post({
          url: "note/detail/delete",
          data: { id: this.input_item.no },
        })
          .then((response) => {
            console.log("deleteCurrentItem ok!");
            this.$emit("deleteIndex", this.index);
            // this.loading = false
            // this.notes = response.note
            // this.pageData = response.page
          })
          .catch((error) => {
            // this.loading = false
            console.log(error);
          });
      },

      postToInsertItem() {
        let userId = this.$store.state.userId;
        let st = this.input_item.completed ? "1" : "0";

        console.log("insert weekcount");
        console.log(this.weekCount);

        this.post({
          url: "note/detail/add",
          data: {
            userId: userId,
            weekCount: this.weekCount,
            weekDay: this.weekDay,
            monday: this.parseDateFormate(this.monday),
            desc: this.input_item.desc,
            status: st,
          },
        })
          .then((response) => {
            console.log("postToInsertItem ok!");
            this.input_item.no = response.detail_id;
            console.log(this.input_item.no);
          })
          .catch((error) => {
            // this.loading = false
            console.log(error);
          });
      },
      postToUpdateItem() {
        let st = this.input_item.completed ? "1" : "0";

        this.post({
          url: "note/detail/update",
          data: { detailId: this.input_item.no, desc: this.input_item.desc, status: st },
        })
          .then((response) => {
            console.log("postToUpdateItem ok!");
            console.log(this.input_item.no);
            // this.loading = false
            // this.notes = response.note
            // this.pageData = response.page
          })
          .catch((error) => {
            // this.loading = false
            console.log(error);
          });
      },
      parseDateFormate(monday) {
        const year = String(new Date(monday).getFullYear());
        const month = String(new Date(monday).getMonth() + 1).padStart(2, "0");
        const day = String(new Date(monday).getDate()).padStart(2, "0");
        const formatedDate = `${year}-${month}-${day}`;
        console.log(formatedDate);
        return formatedDate;
      },
    },
  };
</script>

<style lang="scss" scoped>
  .dt-row {
    margin-bottom: 5px;
    // padding-bottom: 5px;
  }

  .todo {
    border-bottom: 1px solid rgb(255, 187, 0);
  }
  .toggle {
    width: 20px;
    height: 20px;
    background-color: #fff;
    -webkit-appearance: none;
    border: 1px solid #c9c9c9;
    border-radius: 2px;
    outline: none;
  }
</style>
