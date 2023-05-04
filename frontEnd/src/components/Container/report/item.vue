<template>
  <div class="text item">
    <el-row class="ww-row">
        <el-col :span="2" class="row-header"><strong>周{{to_zh(weekDay)}}</strong><span class="ww-day">{{getDate(weekDay)}}</span></el-col>
        <el-col :span="20" ref='details'>
            <el-row
                v-for="(dt,index) in details" :key="dt.no"
            >
                <Detail
                :index = index
                :item = dt
                :weekCount = weekCount
                :weekDay = weekDay
                @deleteIndex="deleteOne"
                ></Detail>
            </el-row>
        </el-col>
        <el-col :span="2" class="row-action"><span class="destroy" @click="addDetail"><i class="el-icon-circle-plus-outline"></i></span></el-col>
    </el-row>
  </div>
</template>

<script>
import Detail from './detail'
import {dateAdd,wwStartOf} from '../../utils/index'
	export default {
		props: {
            weekCount: {
				type: Number,
				required: true
			},
            monday:{
                type: String,
				required: true
            },
			weekDay: {
				type: Number,
				required: true
			},
            details:{
                type: Array,
                required: true
            }
		},
        components: {
		    Detail
	    },
		methods: {
            to_zh(wd){
                let zh = {1:'一',2:'二',3:'三',4:'四',5:'五'}
                return zh[wd]
            },
            addDetail(){
                this.details.push({})
            },

            deleteOne(index){
                // if (index !== 0) {
                console.log("deleteOne")
                console.log(index)
                this.details.splice(index, 1)
                // }
            },

            getDate(weekDay){
                console.log(this.monday)
                let tdy = dateAdd(this.monday,(weekDay-1)*24*60*60*1000)
                console.log(tdy)
                return tdy.slice(5,10);
            }
        }
	}
</script>

<style lang="scss" scoped>

    // .ww-row{
    //     border: red 10px;
    // }

    .text {
        font-size: 16px;
    }

    .item {
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #ebeef5;
        .ww-day{
            font-size: 12px;
            color: #909399;
        }
    }
    .row-header{
        padding-left: 10px;
        // border: 1px solid #ccc;
    }
</style>