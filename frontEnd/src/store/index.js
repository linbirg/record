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
  },

  // 获取或创建 sessionId
  getChatSessionId() {
    let sessionId = localStorage.getItem('chatSessionId')
    if (!sessionId) {
      sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
      localStorage.setItem('chatSessionId', sessionId)
    }
    return sessionId
  },

  // 获取聊天历史
  async getChatHistory({ state }) {
    const sessionId = this.dispatch('getChatSessionId')
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: state.url + '/chat/history',
        data: { userId: state.userId, sessionId }
      }).then(response => {
        if (response.data) {
          resolve(response.data.messages || [])
        } else {
          resolve([])
        }
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 清空聊天会话
  async clearChatSession({ state }) {
    const sessionId = this.dispatch('getChatSessionId')
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: state.url + '/chat/clear',
        data: { userId: state.userId, sessionId }
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 发送聊天消息并接收流式响应
  // 返回一个 Promise，通过 onChunk 回调实时推送内容
  sendChatMessageStream({ state }, { content, onChunk, onDone, onError }) {
    const sessionId = this.dispatch('getChatSessionId')
    
    fetch(state.url + '/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: state.userId, content, sessionId })
    }).then(response => {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      const readStream = () => {
        reader.read().then(({ done, value }) => {
          if (done) {
            if (onDone) onDone()
            return
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop()

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.error && onError) {
                  onError(data.error)
                } else if (onChunk) {
                  onChunk(data.content)
                }
              } catch (e) {
                // 忽略解析错误
              }
            }
          }

          readStream()
        })
      }

      readStream()
    }).catch(error => {
      if (onError) onError(error.message || '网络错误')
    })
  }
}

const store = new Vuex.Store({
  state,
  mutations,
  actions
})

export default store