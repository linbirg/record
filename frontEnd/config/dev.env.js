'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  BASE_URL: '"//127.0.0.1:9000"'
  // BASE_URL: '"//192.168.114.201:5000/record"'
})