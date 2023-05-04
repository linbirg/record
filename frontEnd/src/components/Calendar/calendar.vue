<template>
  <div class="shadow">
    <p class="title">值班表
      <!-- <i v-if="!add" class="el-icon-plus" @click="add = true"></i>
      <i v-if="add" class="el-icon-check" @click="batchAddWeekDuty"></i>
      <i v-if="add" class="el-icon-close" @click="add = false"></i> -->
    </p>
    <div class="date-range">
      <p class="inline">值班时间：</p>
      <div class="inline">
        <el-date-picker
          v-if="add"
          v-model="weekValue"
          class="date-input"
          type="week"
          format="第 WW 周"
          placeholder="选择周"
          @change="concatDate">
        </el-date-picker>
        <p class="gray-ab" v-else>第 <span class="obv">{{weekCount}}</span> 周</p>
        <p class="gray-ab"><span class="obv">{{startDate}}</span> 至 <span class="obv">{{endDate}}</span></p>
      </div>
    </div>
    <ul>
      <li
        v-for="(item, index) in items"
        :key="item.week">
        {{item.week}}：
        <p class="gray-ab" v-if="!item.editable && !add">
          <span
            v-for="list in dutyList"
            v-if="list.weekDay == item.weekDay"
            :class="['name-wrapper', userId == list.userId ? 'obv' : '']"
            :key="list.userId">
          {{list.userName}}</span>
        </p>
        <el-select
          v-else
          class="name-select"
          v-model="item.idList"
          placeholder="值班人"
          multiple
          multiple-limit="2"
          size="mini"
          :style="{width: '220px'}"
        >
          <el-option
            v-for="item in owners"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
        <i v-if="!item.editable && !add" class="el-icon-edit" @click="item.editable = true"></i>
        <i v-if="item.editable && !add" class="el-icon-check" @click="done(index)"></i>
        <i v-if="item.editable && !add" class="el-icon-close" @click="item.editable = false"></i>
      </li>
    </ul>
  </div>
</template>
<script>
import {getWeekCount, dateParse, ymdToDate} from '../utils'
import { mapActions } from 'vuex';
export default {
  data() {
    return {
      add: false,
      typeId: 1,
      weekValue:'',
      weekCount: '',
      startDate: '',
      endDate: '',
      owners: [],
      items: [{
        week:'周一', weekDay: 1, weekCount: '', dutyDate:'', editable: false, idList:[], wids: [] 
      }, {
        week:'周二', weekDay: 2, weekCount: '', dutyDate:'', editable: false, idList:[], wids: []
      }, {
        week:'周三', weekDay: 3, weekCount: '', dutyDate:'', editable: false, idList:[], wids: []
      }, {
        week:'周四', weekDay: 4, weekCount: '', dutyDate:'', editable: false, idList:[], wids: []
      }, {
        week:'周五', weekDay: 5, weekCount: '', dutyDate:'', editable: false, idList:[], wids: []
      }],
      dutyList: [],
      userObj:{}    //以userId为key，和userName组成对象字面量
    }
  },
  mounted() {
    this.getUsersByTypeId()
  },
  computed: {
    userId() {
      return this.$store.state.userId
    }
  },
  methods: {
    ...mapActions(['get', 'post']),
    // 批量新加值班人员
    batchAddWeekDuty() {
      if(this.dutyList.length >0) {
        this.add = false
        return
      }
      this.items.forEach(e => {
        this.dutyList.push({
          weekCount: this.weekCount,
          dutyDate: e.dutyDate,
          weekDay: e.weekDay,
          userId: e.idList[0],
          userName: this.userObj[e.idList[0]]
        },{
          weekCount: this.weekCount,
          dutyDate: e.dutyDate,
          weekDay: e.weekDay,
          userId: e.idList[1],
          userName: this.userObj[e.idList[1]]
        })
      })
      this.$store.dispatch('post', {
				url: 'duty/batchAddWeekDuty.json',
        data: this.dutyList
			}).then(response => {
        this.add = false
        this.getAllUsers()
			}).catch(err => {
				console.log(err)
			})
    },
    //获取typId为1的users
    getUsersByTypeId() {
      let array = []
      this.post({
        data: {typeId: this.typeId},
				url: 'user/selectUserByTypeId.action'
			}).then(response => {
				response.forEach(e => {
					array.push({
						value: e.userId,
						label: e.nickname
					})
				})
        this.owners = array
        this.setUserObj()
        this.getDutyList()
			}).catch(err => {
				console.log(err)
			})
    },
    
    // 以value为key值设置对象字面量
    setUserObj() {
      this.owners.forEach(e => {
        this.$set(this.userObj, e.value, e.label)
      })
    },
    // 获取dutyList
    getDutyList() {
      this.$store.dispatch('get', {
        url: 'duty/selectCurrentWeekDuty.json'
			}).then(response => {
        this.dutyList = response
        this.setIdList()
        this.setDates()
			}).catch(err => {
				console.log(err)
			})
    },
    // 对获取的数据依照weekDay两两分组
    setIdList() {
      this.items.forEach(e => {
        e.idList = []
        e.wids = []
        for (let i = 0, dutyList = this.dutyList; i < dutyList.length; i++) {
          if (e.weekDay == dutyList[i].weekDay) {
            e.idList.push(dutyList[i].userId)
            e.wids.push(dutyList[i].wid)
          }
        }
      })
    },

    // 获取周数并对每个星期添加日期,取dutyList的第一个对象为基准(注意：第一个对象未必是周一的数据)
    setDates() {
      this.weekCount = this.dutyList[0].weekCount
      let refDate = this.dutyList[0].dutyDate
      let refWeekDay = this.dutyList[0].weekDay
      this.items.forEach((e, i) => {
        const count = e.weekDay - refWeekDay
        const date = ymdToDate(refDate)
        e.dutyDate = dateParse(date, count*86400000)
        e.weekCount = this.weekCount
      })
      this.startDate = this.items[0].dutyDate
      this.endDate = this.items[4].dutyDate
    },
    // addItem() {
    //   this.add = true
    // },
    // addCancel() {
    //   this.add = false
    // },
    // edit(index) {
    //   this.items[index].editable = true
    // },
    // cancel(index) {
    //   this.items[index].editable = false
    // },
    // 编辑完成
    done(index) {
      let editDutyItem = []
      let addDutyItem = []
      const item = this.items[index]
      const idList = item.idList
      for (let i = 0; i < 2; i++) {
        if (item.wids[i]) { //某条目存在则编辑
          this.dutyList.forEach(e => {
            if (e.wid == item.wids[i]) {
              e.userId = item.idList[i]
              e.userName = this.userObj[item.idList[i]]
              editDutyItem.push(e)
            }
          })
        } else {
          addDutyItem.push({ //某条目不存在则添加
            weekDay: index + 1,
            dutyDate: item.dutyDate,
            weekCount: item.weekCount,
            userId: item.idList[i] || '', 
            userName: this.userObj[item.idList[i]] || ''
          })
        }
      }
      if (editDutyItem.length) {
        this.updateDuty(editDutyItem, index)
      }
      if (addDutyItem.length) {
        this.addWeekDuty(addDutyItem, index)
      }
    },
    // 单独新增
    addWeekDuty(dutyItem, index) {
      this.$store.dispatch('post', {
        url: 'duty/batchAddWeekDuty.json',
        data: dutyItem
			}).then(response => {
        this.getDutyList()
        this.items[index].editable = false
			}).catch(err => {
				console.log(err)
			})
    },
    // 更新
    updateDuty(dutyItem, index) {
      this.$store.dispatch('post', {
        url: 'duty/updateDuty.json',
        data: dutyItem
			}).then(response => {
        this.getDutyList()
        this.items[index].editable = false
			}).catch(err => {
				console.log(err)
			})
    },
    // select选中的value值推入一个数组
    // selectItem(val) {
    //   this.idListArray = []
    //   this.items.forEach(e => {
    //     this.idListArray.push(e.idList[0] || null, e.idList[1] || null)
    //   })
    // },
    // 根据选中时间计算周数和日期
    concatDate(val) {
      if (val) {
        this.items.forEach((e, i) => {
          e.dutyDate = dateParse(val, i*86400000)
        })
        this.weekCount = getWeekCount(val)
        this.startDate = this.items[0].dutyDate
        this.endDate = this.items[4].dutyDate
      }
    },

    // 设置时间
    // setWeekDate(weekCount, startDate, endDate) {
    //   this.$store.dispatch('post', {
    //     url: 'date/updateWeekDate.json',
    //     data: {
    //       id: 0,
    //       weekCount: weekCount,
    //       startDate: startDate,
    //       endDate: endDate
    //     }
		// 	}).then(() => {
    //     this.getWeekDate()
		// 	}).catch(err => {
		// 		console.log(err)
		// 	})
    // }
  }
}
</script>
<style lang="scss" scoped>
.title {
  font-size: 18px;
  border-bottom: 1px solid rgba(0,0,0,.06);
}
.inline {
  display: inline-block;
  vertical-align: top;
  padding-right: 0;
  p {
    padding-left: 0;
  }
}
.el-icon-edit, .el-icon-check, .el-icon-close, .el-icon-plus {
  float: right;
  padding: 5px;
  color: #9b9ea0;
  cursor: pointer;
}
.date-range, ul {
  color: #373d41;
}
.gray-ab {
  color: #888;
  span.obv {
    color: #373d41
  }
}
p, li {
  padding: 5px 15px;
  font-size: 16px;
}
li p {
  display: inline;
}
.date-input, .name-select {
  font-size: 16px;
}
.name-wrapper {
  display: inline-block;
  width: 80px;
  // &.obv {
  //   color: #ff5722;
  // }
}
</style>
