// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import ElementUI from 'element-ui'
import router from './router'
import store from './store'
import 'element-ui/lib/theme-chalk/index.css'
import './assets/styles/reset.css'
import './assets/styles/styles.css'

Vue.config.productionTip = false
// cros for cookie


Vue.use(ElementUI)
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>',
  render: h => h(App)
})

Vue.options.xhr = { withCredentials: true }

// Vue.http.interceptors.push(function(request) {
//   request.credentials = true
//   return function(response) {
//   };
// });


