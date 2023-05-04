import store from '@/store'
import { Message } from 'element-ui';
// 获取周数
export function getWeekCount (t) {
  const y = t.getFullYear();
  const m = t.getMonth();
  const d = t.getDate();
  const date1 = new Date(y, m, d),
    date2 = new Date(y, 0, 1),
    c = Math.round((date1.valueOf() - date2.valueOf()) / 86400000);
  return Math.ceil((c + ((date2.getDay() + 1) - 1)) / 7);
}

// 将Date对象增加一段时间并转为yyyymmdd格式,params为起始时间,millsed为增加的毫秒数(一天为86400000毫秒)
export function dateParse(t) {
  const year = t.getFullYear()
  const month = t.getMonth() + 1
  const day = t.getDate()
  return [year, month, day].map(formatNumber).join('/')
}

// 格式化数字，个位数前面加0
const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}


export function wwStartOf(t){
  let oneDaySecond = 24*60*60*1000
  let today = t.getDay()
  let stepMonday = -today + 1
  if(today == 0){
    stepMonday = -7
  }

  let mondayTime = t.getTime() +  stepMonday * oneDaySecond
  let monday = new Date(mondayTime)
  return monday
}

export function wwEndOf(t){
  let oneDaySecond = 24*60*60*1000
  let sundayTime = t.getTime() + (5-t.getDay())*oneDaySecond;
  let sunday = new Date(sundayTime)
  return sunday
}

export function dateAdd(params, millsed) {
  let tamp = Date.parse(params)
  let t = new Date(tamp + millsed)
  return dateParse(t)
}

// 将yyyymmdd格式转为Date对象
export function ymdToDate(params) {
  params = params.toString()
  const y = params.slice(0, 4)
  const m = params.slice(4, 6)*1 - 1
  const d = params.slice(6)
  return new Date(y, m, d)
}

//获取当前时间设置为YY-MM-DD格式
export const getFormatDate = () => {
  var t = new Date();
  var y = t.getFullYear();
  var m = t.getMonth() + 1;
  var d = t.getDate();
  return y + '-' + m + '-' + d;
}

// 向后端发送请求
export function require(opt) {
  let params = {}
  if (opt.method === 'post') {
    params = {
      url: opt.url,
      data: opt.data
    }
  }
  if (opt.method === 'get') {
    params = {
      url: opt.url
    }
  }
  store.dispatch(opt.method, params)
  .then(response => {
    opt.callback(response)
  })
  .catch(error => {
    Message({
      showClose: true,
      message: '提交请求失败',
      type: 'error'
    })
  })
}