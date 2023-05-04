<template>
  <div id="tabs">
    <el-col v-if="roleId > 3">
      <el-menu
        class="el-menu-vertical-demo"
        router
      >
        <el-menu-item
          v-if="state.index < 3"
          v-for="state in states" 
          :index="state.link"
          :key="state.index"
        >
          {{state.text}}
        </el-menu-item>
      </el-menu>
    </el-col>
    <el-col v-else>
      <el-menu
        class="el-menu-vertical-demo"
        router
      >
        <el-submenu index="1">
          <template slot="title">
            <span>周报</span>
          </template>
          <el-menu-item 
            v-if="(state.index !== 4 || (state.index === 4 && roleId == 1)) && state.index < 8"
            v-for="state in states"
            :index="state.link"
            :key="state.index"
          >
            {{state.text}}
          </el-menu-item>
        </el-submenu>
        <el-menu-item
          v-if="state.index > 7"
          v-for="state in states" 
          :index="state.link"
          :key="state.index"
        >
          {{state.text}}
        </el-menu-item>
      </el-menu>
    </el-col>
  </div>
</template>
<script>
import waves from '@/directive/waves/index.js' // 水波纹指令
import {mapActions, mapMutations} from 'vuex'
export default {
  data() {
    return {
      roleId: '',
      states: [{
        index: 1,
        text: '个人',
        link: '/record/personal'
      }, {
        index: 2,
        text: '全体',
        link: '/record/all'
      },
      // {
      //   index: 3,
      //   text: '组别',
      //   link: '/team'
      // }, 
      {
        index: 4,
        text: '部门',
        link: '/department'
      }, 
      // {
      //   index: 5,
      //   text: '值班',
      //   link: '/duty'
      // }, 
      // {
      //   index: 8,
      //   text: '会议记录',
      //   link: '/meeting'
      // },
      // {
      //   index: 9,
      //   text: '通讯录',
      //   link: '/addressBook'
      // }, 
      {
        index: 10,
        text: '车辆登记',
        link: '/carsReg'
      },{
        index: 11,
        text: '简报',
        link: '/report'
      }]
    }
  },
  directives: {
    waves
  },
  computed: {
    userId() {
      return this.$store.state.userId
    }
  },
  mounted() {
    this.getRoleId()
  },
  methods: {
    ...mapActions(['post', 'get']), // 将 `this.post()` 映射为 `this.$store.dispatch('post')`
    // 获取roleId
    getRoleId() {
      this.get({
				url: 'user/' //获取所有用户列表
				// url: 'user/showUser.do?userId=0' //获取所有用户列表
			}).then(response => {
				response.forEach(e => {
					if (this.userId == e.userId) {
            this.roleId = e.roleId
          }
        })
			}).catch(err => {
				console.log(err)
			})
    }
  }
}
</script>
<style lang="scss" scoped>
  #tabs{
    position: fixed;
    top: 72px;
    left: 15px;
    width: 201px;
    font-size: 16px;
  }
  // li {
  //   span {
  //     display: inline-block;
  //     width: 100%;
  //   }
  // }
  .list-btn {
    li {
    text-align: center;
    margin-bottom: 5px;
    background-color: #fff;
    cursor: pointer;
    .router-link-active {
      border: 1px solid #ccc;
      background-color: #ccc;
    }
    a {
      display: inline-block;
      padding: 8px 25px;
      width: 85px;
      height:42px;
      line-height: 42px;
      border: 1px solid #fff;
      color: #222;
      transition: border-color .2s ease-in-out;
      &:hover {
        border-color: #ccc;
      }
    }
  }
  }
</style>