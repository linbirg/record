<template>
  <div
    v-loading="loading"
    class="cat-pad">
    <div class="btn-item">
      <span>车辆登记</span>
      <div class="search-wrapper">
        <el-form :inline="true">
          <el-form-item>
            <el-input
              style="width: 240px"
              placeholder="请输入查找内容"
              clearable
              v-model="qry"
              @keyup.enter.native="search">
              <el-select
                style="width: 100px"
                v-model="select"
                slot="prepend"
                placeholder="车牌号">
                <el-option
                  v-for="item in qry_options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"></el-option>
              </el-select>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              class="search-btn el-button--infoSearch"
              icon="el-icon-search"
              circle
              @click="search"></el-button>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              icon="el-icon-plus"
              circle
              @click="showAddDialog"></el-button>
          </el-form-item>
        </el-form>
        <div class="clearFix"></div>
      </div>
    </div>

    <el-table
      :data="tableData"
      stripe>
      <el-table-column
        prop="no"
        type="index"
        label="序号"
        width="60">
      </el-table-column>
      <el-table-column
        prop="name"
        label="姓名"
        width="80">
      </el-table-column>
      <el-table-column
        prop="dept"
        label="部门">
      </el-table-column>
      <el-table-column
        prop="carNo"
        label="车牌号">
      </el-table-column>
      <el-table-column
        prop="seqNo"
        label="编号">
      </el-table-column>
      <el-table-column
        prop="brand"
        label="品牌">
      </el-table-column>
      <el-table-column
        prop="regDate"
        label="登记日期">
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <!-- <a>编辑</a><a>删除</a><a>历史</a> -->
          <el-button
            @click="showEditDialog(scope.row)"
            type="text"
            size="small"
            >编辑</el-button
          >
          <el-button
            @click="showDelDialog(scope.row)"
            type="text"
            size="small"
            >删除</el-button
          >
          <el-button
            @click="showHisDialog(scope.row)"
            type="text"
            size="small"
            >历史</el-button
          >
        </template>
      </el-table-column>
      <el-table-column type="expand">
        <template slot-scope="props">
          <Detail
            :no="props.row.no"
            :name="props.row.name"
            :dept="props.row.dept"
            :carNo="props.row.carNo"
            :brand="props.row.brand"
            :carlicense="props.row.carlicense"
            :license="props.row.license"
            :abbr="props.row.abbr"
            :imgs="props.row.imgs"></Detail>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件start -->
    <Pagination
      :totalItem="this.pageData.totalItem"
      :currentPage="this.pageData.currentPage"
      @handleCurrentChange="handleCurrentChange" />
    <!-- 分页组件end -->
    <!-- 弹窗组件 start -->
    <el-dialog
      :visible.sync="dialogFormVisible"
      :close-on-click-modal="false"
      width="30%">
      <span
        slot="title"
        class="dialog-title">
        {{ dialogTitle }}
      </span>
      <el-form
        :model="carInfo"
        :rules="rules"
        ref="carInfo"
        label-width="120px"
        size="medium">
        <el-form-item
          label="姓名"
          prop="name">
          <el-input v-model="carInfo.name"></el-input>
        </el-form-item>
        <el-form-item
          label="部门"
          prop="dept">
          <el-input v-model="carInfo.dept"></el-input>
        </el-form-item>
        <el-form-item
          label="车牌号"
          prop="carNo">
          <el-input v-model="carInfo.carNo"></el-input>
        </el-form-item>
        <el-form-item
          label="编号"
          prop="seqNo">
          <el-row :gutter="20">
            <el-col
              :span="6"
              :offset="0"
              style="padding-left: 0px">
              <el-select
                v-model="carInfo.seqNoPrefix"
                placeholder="临No."
                style="padding-left: 0px"
                @change="seqSelectChange">
                <el-option
                  label="No."
                  value="No."></el-option>
                <el-option
                  label="临No."
                  value="临No."></el-option>
              </el-select>
            </el-col>
            <el-col
              :span="17"
              :offset="0"
              style="padding-right: 2px"
              ><el-input v-model="carInfo.seqNoSuffix"></el-input
            ></el-col>
          </el-row>
        </el-form-item>
        <el-form-item
          label="品牌"
          prop="brand">
          <el-input v-model="carInfo.brand"></el-input>
        </el-form-item>
        <el-form-item
          label="登记日期"
          prop="regDate">
          <el-input v-model="carInfo.regDate"></el-input>
        </el-form-item>
        <el-form-item
          label="行驶证"
          prop="carlicense">
          <el-input v-model="carInfo.carlicense"></el-input>
        </el-form-item>
        <el-form-item
          label="驾驶证"
          prop="license">
          <el-input v-model="carInfo.license"></el-input>
        </el-form-item>
        <el-form-item
          label="备注"
          prop="abbr">
          <el-input v-model="carInfo.abbr"></el-input>
        </el-form-item>
      </el-form>
      <div
        slot="footer"
        class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button
          type="primary"
          v-if="isAdd"
          @click="validate('carInfo')"
          >确 定</el-button
        >
        <el-button
          type="primary"
          v-if="!isAdd"
          @click="validate('carInfo')"
          >更 新</el-button
        >
      </div>
    </el-dialog>
    <!-- 弹窗组件 end -->
    <!-- 删除提示弹窗组件 start -->
    <el-dialog
      title="提示"
      :visible.sync="dialogDelVisible"
      width="30%">
      <span>确定删除该记录？</span>
      <span
        slot="footer"
        class="dialog-footer">
        <el-button @click="dialogDelVisible = false">取 消</el-button>
        <el-button
          type="primary"
          @click="deleteCarInfo()"
          >确 定</el-button
        >
      </span>
    </el-dialog>
    <!-- 删除提示弹窗组件 end -->
  </div>
</template>
<script>
  import waves from "@/directive/waves/index.js"; // 水波纹指令
  import Pagination from "../../pagination";
  import { mapActions } from "vuex";

  import Detail from "./detail";

  export default {
    components: {
      Pagination,
      Detail,
    },
    data() {
      return {
        loading: false,
        isAdd: true,
        formLabelWidth: "120px",
        dialogFormVisible: false,
        dialogDelVisible: false,
        dialogTitle: "",
        delId: "",
        tableData: [],
        qry: "",
        select: 1,
        qry_options: [],
        carInfo: {
          no: -1,
          name: "",
          dept: "",
          carNo: "",
          seqNoPrefix: "",
          seqNoSuffix: "",
          seqNo: "",
          brand: "",
          regDate: "",
          carlicense: "",
          license: "",
          abbr: "",
          imgs: "",
        },
        pageData: {
          totalItem: 20,
          currentPage: 1,
          pageSize: 10,
          startItem: 0,
          userId: 0,
          typeId: 0,
          userName: "",
        },
        rules: {
          //提交form验证
          name: [
            {
              required: true,
              trigger: "change",
              message: "请填写名称",
            },
          ],
          dept: [
            {
              required: true,
              trigger: "change",
              message: "请填写部门",
            },
          ],
          carNo: [
            {
              required: true,
              trigger: "change",
              message: "请填写车牌号",
            },
          ],
        },
      };
    },

    mounted() {
      this.load_search_options();
      this.queryByPage();
    },
    // 自定义指令
    directives: {
      waves,
    },

    methods: {
      ...mapActions(["get", "post"]),

      //表单验证
      validate(formName, operation) {
        this.$refs[formName].validate((valid) => {
          if (!valid) {
            console.log("error submit!!");
            return false;
          }

          if (this.isAdd) {
            this.submitCarInfo();
            return true;
          }
          if (!this.isAdd) {
            this.updateCarInfo();
            return true;
          }
        });
      },

      load_search_options() {
        this.qry_options = [];
        this.get({
          url: "car/search/options",
        })
          .then((response) => {
            this.qry_options = response;
          })
          .catch((error) => {
            this.errorMessage("获取搜索选项失败");
          });
      },

      // 添加机器资源信息
      submitCarInfo() {
        this.carInfo.seqNo = this.carInfo.seqNoPrefix + this.carInfo.seqNoSuffix;
        this.post({
          url: "car/add",
          data: this.carInfo,
        })
          .then((response) => {
            this.dialogFormVisible = false;
            this.queryByPage();
          })
          .catch((error) => {
            this.errorMessage("添加");
          });
      },

      // 删除机器资源信息
      deleteCarInfo() {
        this.post({
          url: "car/delete",
          data: { no: this.delNo },
        })
          .then((response) => {
            this.dialogDelVisible = false;
            this.queryByPage();
          })
          .catch((error) => {
            this.errorMessage("删除");
          });
      },

      // 修改机器资源信息
      updateCarInfo() {
        this.carInfo.seqNo = this.carInfo.seqNoPrefix + this.carInfo.seqNoSuffix;
        console.log(this.carInfo);
        this.post({
          url: "car/update",
          data: this.carInfo,
        })
          .then((response) => {
            this.dialogFormVisible = false;
            this.queryByPage();
          })
          .catch((error) => {
            this.errorMessage("修改");
          });
      },

      seqSelectChange(value) {
        // 根据下拉框的值修改变量carInfo对应的seqNo属性
        console.log("seqSelectChange");
        console.log(value);
        if (value === "临No.") {
          this.carInfo.seqNoPrefix = "临No.";
        } else {
          this.carInfo.seqNoPrefix = "No.";
        }
        // this.$forceUpdate(); // 强制更新组件
      },

      // 查找资源信息
      queryByPage() {
        this.loading = true;
        this.post({
          url: "car/page",
          data: this.pageData,
        })
          .then((response) => {
            this.loading = false;
            this.tableData = response.carInfo;
            this.pageData.totalItem = response.totalItem;
            this.pageData.currentPage = 1;
          })
          .catch((error) => {
            this.loading = false;
            this.errorMessage("查找");
            alert(error.message);
          });
      },

      // 翻页
      handleCurrentChange(val) {
        this.pageData.currentPage = val;
        this.pageData.startItem = this.pageData.pageSize * (val - 1);
        this.queryByPage();
      },

      showAddDialog() {
        this.isAdd = true;
        this.carInfo = {};
        this.dialogFormVisible = true;
        this.dialogTitle = "新增";
        //重置表单内容及验证条件，必须在dialog选然后才生效
        this.$refs["carInfo"] && this.$refs["carInfo"].resetFields();
      },

      // 显示修改弹框
      showEditDialog(data) {
        console.log("showEditDialog");
        this.isAdd = false;
        this.carInfo = JSON.parse(JSON.stringify(data)); //简单深拷贝，防止内存引用重复
        if (
          this.carInfo.seqNo !== null &&
          this.carInfo.seqNo !== undefined &&
          this.carInfo.seqNo !== "" &&
          this.carInfo.seqNo.indexOf(".") > -1
        ) {
          this.$set(this.carInfo, "seqNoPrefix", this.carInfo.seqNo.split(".")[0] + ".");
          this.$set(this.carInfo, "seqNoSuffix", this.carInfo.seqNo.split(".")[1]);
        }

        this.dialogFormVisible = true;
        this.dialogTitle = "编辑";
      },

      // 显示删除弹窗
      showDelDialog(data) {
        this.dialogDelVisible = true;
        this.delNo = data.no;
      },

      // 显示删除弹窗
      showHisDialog(data) {
        // this.dialogDelVisible = true;
        this.delNo = data.no;
      },

      // 失败弹窗
      errorMessage(text) {
        this.$message({
          showClose: true,
          message: text + ",请稍后重试",
          type: "error",
        });
      },
      search() {
        console.log(this.qry);
        console.log(this.select);

        this.loading = true;
        this.pageData.option = this.select;
        this.pageData.query = this.qry;
        this.post({
          url: "car/search",
          // data: { option: this.select, query: this.qry },
          data: this.pageData,
        })
          .then((response) => {
            this.loading = false;
            this.tableData = response.carInfo;
            this.pageData.totalItem = response.totalItem;
            this.pageData.currentPage = 1;
          })
          .catch((error) => {
            this.loading = false;
            this.errorMessage("查找");
            alert(error.message);
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
  .cat-pad {
    width: 1100px;
    min-height: 400px;
    border-radius: 4px;
    padding: 3px 0;
    background-color: #fff;
    font-size: 14px;
    border: 1px solid #ebeef5;
    -webkit-box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    color: #303133;
    .btn-item {
      height: 45px;
      padding-top: 10px;
      padding-left: 20px;
      border-bottom: 1px solid #ebeef5;
      span {
        font-size: 22px;
      }
      .search-wrapper {
        // display:inline-block;
        float: right;
        .el-form {
          height: 45px;
        }
        el-input {
          width: 100px;
        }
        button {
          float: right;
        }
      }
    }

    .el-table {
      // margin-top: 1px;
      width: 98%;
      padding-left: 15px;

      .demo-table-expand {
        font-size: 0;
        padding-left: 15px;
        .detail-title {
          font-size: 14px;
          margin: 0 auto;
        }
      }
      .demo-table-expand label {
        width: 90px;
        color: #99a9bf;
      }
      .demo-table-expand .el-form-item {
        margin-right: 0;
        margin-bottom: 0;
        width: 50%;
      }
    }
  }

  .name-input {
    height: 40px;
    line-height: 40px;
    outline: 0;
    padding: 0 15px;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    box-sizing: border-box;
    color: #606266;
  }
  .dialog-title {
    line-height: 24px;
    font-size: 18px;
    color: #303133;
  }

  // .el-form-item {
  //   display: inline-block;
  // }
</style>
