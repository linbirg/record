## 1. Yeab为何？
    用python实现的web框架。Django对小型快速项目有点重。Flask在mvc、模块编程、注解、自动扫描等方面，不是很方便。所以借此机会，参照spring等其他框架，结合自己的经验，尝试书写一个框架，也作为学习的机会。

## 2 一些借鉴的原则
### 1. orm不包含在框架内
### 2. 可以借鉴rails一些习惯，约定大于配置
### 3. 借鉴sping mvc的一些方式，controller最好可以注解

## 3 一些问题记录及解决办法
### 1 before_request的实现
    采用midlware的办法
### 2 session的实现
    参考aiohttp_session的实现，采用cookie的存储方式
### 3 cors的问题
    通过midlware或者filter实现。
    cors带cookie的问题，在axos或者vue中设置 Vue.options.xhr = { withCredentials: true }
### 4 option方法的问题
    通过在filter中回复ok实现
### 5 参照spring方式的注解实现
    注解实现标注，创建app时，实现包下面的自动扫描，添加到midlware，或者route，或者signal来实现
### 6 异步yom
    参照activerecord的实现方式，在同步的基础上采用aiomysql实现，并实现连接池

### 7 自动加载
    廖老师的代码，利用watchdog检测目录，自动重起加载

### 8 json datetime序列化问题
    functools.partial,重构encoder


### 9 如何将request的json作为整体赋值给某个参数