import Vue from 'vue'
import Router from 'vue-router'
import Cookies from 'js-cookie'
import store from '../store'
// import Login from '../components/Login'
// import Layout from '../components/Layout'
// import Records from '../components/Container/records'
// import Team from '../components/Container/Team/team'
// import Department from '../components/Container/department'
// import Duty from '../components/Container/duty'
// import Meeting from '../components/Container/meeting'
// import AddressBook from '../components/Container/addresssBook'
const Login = () => import('../components/Login')
const Layout = () => import('../components/Layout')
const Records = () => import('../components/Container/records')
const WeekRecords = () => import('../components/Container/wr/weekrecords')
const Reports = () => import('../components/Container/report/reports')
const Team = () => import('../components/Container/Team/team')
const Department = () => import('../components/Container/department')
const Duty = () => import('../components/Container/duty')
const Meeting = () => import('../components/Container/meeting')
const AddressBook = () => import('../components/Container/addresssBook')
const CarsReg = () => import('../components/Container/car/carsReg')

Vue.use(Router)

const router = new Router({
  routes: [{
    path: '/login',
    component: Login
  }, {
    path: '/',
    redirect: '/record/personal'
  }, {
    path: '/record',
    redirect: '/record/personal'
  }, {
    path: '/container',
    component: Layout,
    children: [
      {
        path: '/record/all',
        component: Records
      },{
      path: '/record/personal',
      component: WeekRecords
    }, {
      path: '/team',
      component: Team
    }, {
      path: '/department',
      component: Department
    }, {
      path: '/duty',
      component: Duty
    }, {
      path: '/meeting',
      component: Meeting
    }, {
      path: '/addressbook',
      component: AddressBook
    }, {
      path: '/carsReg',
      component: CarsReg
    },{
      path: '/report',
      component: Reports
    }]
  }]
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  const userId = Cookies.get('userId')
  const typeId = Cookies.get('typeId')
  if (userId && typeId) {
    store.commit('setUserId', userId)
    store.commit('setTypeId', typeId)
    next()
  } else {
    if (to.path === '/login') {
      next() //必须调用next()方法，否则钩子就不会被 resolved
    } else {
      next({ path: '/login'})
    }
  }
})

export default router