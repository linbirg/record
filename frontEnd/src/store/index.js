import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import Cookies from 'js-cookie'
import router from '../router'

Vue.use(Vuex, axios)
// axios.defaults.baseURL = process.env.BASE_URL ? process.env.BASE_URL : '/record'
// axios.defaults.withCredentials = true

const state = {
  url: process.env.BASE_URL ? process.env.BASE_URL : '/record',
  editable: false, //判断是否可编辑的key值
  notes: [], //存储笔记数据
  userList: [], //用户列表
  page: {},
  token: '',
  userId: 0,
  typeId: 0
}

// 同步方法
const mutations = {
  setEditabe(state, key) {
    state.editable = key
  },
  setNotes(state, data) {
    state.notes = data
  },
  setUserList(state, userList) {
    state.userList = userList
  },
  setPage(state, data) {
    state.page = data
  },
  setCookis(state, token) {
    state.token = token
  },
  setUserId(state, userId) {
    state.userId = userId
  },
  setTypeId(state, typeId) {
    state.typeId = typeId
  },
  setCurrentPage(state, currentPage) {
    state.currentPage = currentPage
  }
}

// 异步方法
const actions = {
  // post请求统一接口,为没有commit回调操作的请求使用
  // data.url为请求后端接口名称
  // data.data为前端传递数据
  post({ }, data) {
    const url = this.state.url + '/' + data.url
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: url,
        data: data.data
      }).then(response => {
        if (!!response.data) {
          resolve(response.data)
        } else {
          router.push({ path: '/login' })
        }
      }).catch(error => {
        reject(error)
      })
    })
  },
  get({ }, data) {
    const url = this.state.url + '/' + data.url
    return new Promise((resolve, reject) => {
      axios({
        method: 'get',
        url: url
      }).then(response => {
        if (!!response.data) {
          resolve(response.data)
        } else {
          router.push({ path: '/login' })
        }
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 用户登录
  loginByUserInfo({ commit }, data) {
    const url = this.state.url + '/login.action'
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: url,
        params: data
      }).then(function (response) {
        commit('setUserId', response.data.userId)
        commit('setTypeId', response.data.typeId)
        Cookies.set('userId', response.data.userId)
        Cookies.set('typeId', response.data.typeId)
        resolve(response.data)
      }).catch(function (error) {
        reject(error)
      })
    })
  },

  // 登出
  loginOut() {
    return new Promise(() => {
      Cookies.remove('userId')
      Cookies.remove('typeId')
    })
  }
}

const store = new Vuex.Store({
  state,
  mutations,
  actions
})

export default store