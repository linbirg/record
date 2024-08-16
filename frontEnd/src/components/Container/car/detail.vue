<template>
  <el-form
    label-position="left"
    label-width="80px"
    class="demo-table-expand">
    <el-row>
      <el-col :span="12">
        <el-form-item label="姓名"
          ><span>{{ name }}</span></el-form-item
        >
      </el-col>
      <el-col :span="12">
        <el-form-item label="部门"
          ><span>{{ dept }}</span></el-form-item
        >
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="12">
        <el-form-item label="车牌号"
          ><span>{{ carNo }}</span></el-form-item
        >
      </el-col>
      <el-col :span="12">
        <el-form-item label="品牌"
          ><span>{{ brand }}</span></el-form-item
        >
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="12">
        <el-form-item label="行驶证"
          ><span>{{ carlicense }}</span></el-form-item
        >
      </el-col>
      <el-col :span="12">
        <el-form-item label="驾驶证"
          ><span>{{ license }}</span></el-form-item
        >
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="12">
        <el-form-item label="证件"
          ><span></span
          ><span style="padding-left: 20px"
            ><el-button @click="showELUpload()">{{ showBtnLabel }}</el-button></span
          ></el-form-item
        >
      </el-col>
      <el-col :span="12">
        <el-form-item label="备注"
          ><span>{{ abbr }}</span></el-form-item
        >
      </el-col>
    </el-row>
    <el-row>
      <el-upload
        v-if="isShowUploadDlg"
        action="#"
        list-type="picture-card"
        :auto-upload="true"
        :http-request="uploadfile"
        :headers="headers"
        :on-change="onChange"
        :file-list="fileList">
        <i
          slot="default"
          class="el-icon-plus"></i>
        <div
          slot="file"
          slot-scope="{ file }">
          <img
            class="el-upload-list__item-thumbnail"
            :src="file.url"
            alt="" />
          <span class="el-upload-list__item-actions">
            <span
              class="el-upload-list__item-preview"
              @click="handlePictureCardPreview(file)">
              <i class="el-icon-zoom-in"></i>
            </span>
            <span
              v-if="!disabled"
              class="el-upload-list__item-delete"
              @click="handleRemove(file)">
              <i class="el-icon-delete"></i>
            </span>
          </span>
        </div>
      </el-upload>
      <el-dialog :visible.sync="dialogVisible">
        <img
          width="100%"
          :src="dialogImageUrl"
          alt="" />
      </el-dialog>
    </el-row>
  </el-form>
</template>

<script>
  import { mapActions } from "vuex";

  export default {
    props: {
      no: {
        type: Number,
        required: true,
      },
      name: {
        type: String,
        required: true,
      },
      dept: {
        type: String,
        required: true,
      },
      carNo: {
        type: String,
        required: true,
      },
      brand: {
        type: String,
        required: false,
      },
      carlicense: {
        type: String,
        required: false,
      },
      license: {
        type: String,
        required: false,
      },
      abbr: {
        type: String,
        required: false,
      },
      imgs: {
        type: String,
        required: false,
      },
    },

    data() {
      return {
        dialogImageUrl: "",
        showBtnLabel: "详情",
        isShowUploadDlg: false,
        dialogVisible: false,
        disabled: false,
        headers: { "Content-Type": "multipart/form-data" },
        fileList: [],
        hasQryedFileList: false,
      };
    },

    mounted() {
      console.log("mounted");
      this.showELUpload();
    },

    methods: {
      ...mapActions(["get", "post"]),

      showELUpload() {
        this.isShowUploadDlg = !this.isShowUploadDlg;
        this.showBtnLabel = this.isShowUploadDlg ? "隐藏" : "详情";

        this.qryFileList();
      },

      qryFileList() {
        if (this.hasQryedFileList) {
          console.log("已查询。");
          return;
        }

        this.post({
          url: "car/pic/filelist",
          data: { no: this.no },
        })
          .then((response) => {
            console.log("查询文件列表成功。");
            this.fileList = response;
            this.hasQryedFileList = true;
          })
          .catch((error) => {
            console.log("查询文件列表失败");
          });
      },

      handleRemove(file) {
        // alert('handleRemove');
        // console.log(file);
        this.post({
          url: "car/pic/delete",
          data: { no: this.no, filename: file.name },
        })
          .then((response) => {
            console.log("删除文件成功。");
            // this.fileList = response
            this.hasQryedFileList = false;
            this.qryFileList();
          })
          .catch((error) => {
            console.log("删除文件失败");
          });
      },

      handlePictureCardPreview(file) {
        this.dialogImageUrl = file.url;
        this.dialogVisible = true;
      },

      uploadfile(item) {
        console.log("uploadfile");
        console.log(item);
        //   alert(this.no)
        let fileData = new FormData();
        fileData.append("file", item.file);
        fileData.append("no", this.no);
        console.log(fileData);
        this.post({
          url: "car/pic/upload",
          data: fileData,
        })
          .then((response) => {
            console.log("文件上传成功。");
            this.hasQryedFileList = false;
          })
          .catch((error) => {
            console.log("上传文件失败");
          });
      },
      onChange(file, fileList) {
        //   alert('onChange');
        console.log(file);
        console.log(fileList);
      },
    },
  };
</script>
