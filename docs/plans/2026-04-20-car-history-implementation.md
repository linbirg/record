# 车辆历史记录功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现车辆历史记录功能，包括删除历史和车牌号变更历史的记录与查询

**Architecture:** 
- 新增两张历史表：t_car_info_history（删除历史）、t_car_no_history（车牌号变更）
- 修改现有删除和更新接口记录历史
- 前端新增历史管理页面

**Tech Stack:** SQLite, python, Vue + ElementUI

---

## Task 1: 创建数据库迁移脚本

**File:** Create: `yail/tools/migrate_sqlite/6_car_history.py`

**Step 1: 创建迁移脚本**

```python
# yail/tools/migrate_sqlite/6_car_history.py

import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建删除历史表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_info_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_id INTEGER,
        user_name TEXT,
        dept TEXT,
        carid TEXT,
        brand TEXT,
        car_license TEXT,
        license TEXT,
        abbr TEXT,
        deleted_at TEXT DEFAULT (datetime('now', 'localtime'))
    )
    ''')
    
    # 创建车牌号变更历史表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_no_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        old_car_no TEXT,
        new_car_no TEXT,
        changed_at TEXT DEFAULT (datetime('now', 'localtime'))
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration 6: car_history tables created successfully")

def down():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS t_car_info_history')
    cursor.execute('DROP TABLE IF EXISTS t_car_no_history')
    conn.commit()
    conn.close()
    print("Migration 6: car_history tables dropped")

if __name__ == '__main__':
    up()
```

**Step 2: 运行迁移**

```bash
cd /mnt/d/project/linbirg/ww/ww/record/yail
python tools/migrate_sqlite/6_car_history.py
```

**Step 3: 提交**

```bash
git add yail/tools/migrate_sqlite/6_car_history.py
git commit -m "feat(car): 添加车辆历史记录表迁移脚本"
```

---

## Task 2: 创建 CarHistory DAO

**File:** Create: `yail/www/dao/car_history.py`

**Step 1: 创建 DAO**

```python
# yail/www/dao/car_history.py

from lib.yom import Model, FieldDef as fd
from datetime import datetime


class CarInfoHistory(Model):
    __table__ = "t_car_info_history"
    
    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    original_id = fd.IntField(name="original_id")
    user_name = fd.UserNameField()
    dept = fd.DepartmentField()
    carid = fd.CarNoField()
    brand = fd.BrandField()
    car_license = fd.CarLicenseField()
    license = fd.LicenseField()
    abbr = fd.AbbrField()
    deleted_at = fd.CreatedAtField()


class CarNoHistory(Model):
    __table__ = "t_car_no_history"
    
    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    car_id = fd.IntField(name="car_id")
    old_car_no = fd.CarNoField()
    new_car_no = fd.CarNoField()
    changed_at = fd.CreatedAtField()
```

**Step 2: 验证导入**

```bash
cd /mnt/d/project/linbirg/ww/ww/record/yail
python -c "from www.dao.car_history import CarInfoHistory, CarNoHistory; print('DAO import OK')"
```

**Step 3: 提交**

```bash
git add yail/www/dao/car_history.py
git commit -m "feat(car): 添加 CarHistory 和 CarNoHistory DAO"
```

---

## Task 3: 修改 CarInfo.delete 方法

**File:** Modify: `yail/www/dao/car_info.py`

**Step 1: 添加 save_to_history 方法**

在 CarInfo 类中添加：

```python
async def save_to_history(self):
    """保存当前记录到历史表"""
    history = CarInfoHistory()
    history.original_id = self.no
    history.user_name = self.name
    history.dept = self.dept
    history.carid = self.carNo
    history.brand = self.brand
    history.car_license = self.carLicense
    history.license = self.license
    history.abbr = self.abbr
    await history.save()
```

**Step 2: 提交**

```bash
git add yail/www/dao/car_info.py
git commit -m "feat(car): CarInfo 添加 save_to_history 方法"
```

---

## Task 4: 修改 /car/delete 接口

**File:** Modify: `yail/www/handlers/car/index.py`

**Step 1: 修改 delete 函数**

在删除前先保存到历史表：

```python
@post("/car/delete")
@ResponseBody
async def delete(no):
    car = await CarInfo.find_one(no=no)
    if not car:
        return Message("ok!")
    
    # 保存到历史表
    await car.save_to_history()
    
    pics = await CarPics.find(carID=car.no)
    for p in pics:
        pic_path = "/".join([PIC_DIR, p.path])
        if os.path.exists(pic_path):
            os.remove(pic_path)
        await p.delete()
    
    await car.delete()
    return Message("ok!")
```

**Step 2: 导入 CarInfoHistory（如果需要）**

确保文件中已导入 CarInfo

**Step 3: 提交**

```bash
git add yail/www/handlers/car/index.py
git commit -m "feat(car): delete 接口改为先保存历史再删除"
```

---

## Task 5: 修改 /car/update 接口记录车牌号变更

**File:** Modify: `yail/www/handlers/car/index.py`

**Step 1: 修改 update 函数**

在车牌号变更时记录到历史表：

```python
@post("/car/update")
@ResponseBody
@RequestBody("carInfo", kls=VoCarInfo)
async def update(carInfo):
    from www.dao.car_history import CarNoHistory
    
    car = await CarInfo.find_one(no=carInfo.no)
    
    # 记录车牌号变更
    if car.carNo != carInfo.carNo:
        history = CarNoHistory()
        history.car_id = car.no
        history.old_car_no = car.carNo
        history.new_car_no = carInfo.carNo
        await history.save()
    
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr
    await car.update()
    return Message("ok!")
```

**Step 2: 提交**

```bash
git add yail/www/handlers/car/index.py
git commit -m "feat(car): update 接口添加车牌号变更记录"
```

---

## Task 6: 添加历史查询接口

**File:** Modify: `yail/www/handlers/car/index.py`

**Step 1: 添加 /car/history 接口**

```python
@post("/car/history")
@ResponseBody
async def get_history(request):
    from www.dao.car_history import CarInfoHistory
    
    data = await request.post()
    current_page = int(data.get("currentPage", 1))
    page_size = int(data.get("pageSize", 20))
    car_no = data.get("carNo", "")
    start_date = data.get("startDate", "")
    end_date = data.get("endDate", "")
    
    # 构建查询
    where = "1=1"
    params = []
    if car_no:
        where += " AND carid LIKE ?"
        params.append(f"%{car_no}%")
    if start_date:
        where += " AND deleted_at >= ?"
        params.append(start_date)
    if end_date:
        where += " AND deleted_at <= ?"
        params.append(end_date)
    
    # 查询总数
    count_sql = f"SELECT COUNT(*) FROM t_car_info_history WHERE {where}"
    total = await CarInfoHistory.execute(count_sql, params)
    
    # 分页查询
    offset = (current_page - 1) * page_size
    sql = f"SELECT * FROM t_car_info_history WHERE {where} ORDER BY deleted_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    records = await CarInfoHistory.execute(sql, params)
    
    return {
        "success": True,
        "records": records,
        "total": total,
        "currentPage": current_page,
        "pageSize": page_size
    }
```

**Step 2: 添加 /car/car_no_history 接口**

```python
@post("/car/car_no_history")
@ResponseBody
async def get_car_no_history(request):
    from www.dao.car_history import CarNoHistory
    
    data = await request.post()
    current_page = int(data.get("currentPage", 1))
    page_size = int(data.get("pageSize", 20))
    car_no = data.get("carNo", "")
    start_date = data.get("startDate", "")
    end_date = data.get("endDate", "")
    
    where = "1=1"
    params = []
    if car_no:
        where += " AND (old_car_no LIKE ? OR new_car_no LIKE ?)"
        params.extend([f"%{car_no}%", f"%{car_no}%"])
    if start_date:
        where += " AND changed_at >= ?"
        params.append(start_date)
    if end_date:
        where += " AND changed_at <= ?"
        params.append(end_date)
    
    count_sql = f"SELECT COUNT(*) FROM t_car_no_history WHERE {where}"
    total = await CarNoHistory.execute(count_sql, params)
    
    offset = (current_page - 1) * page_size
    sql = f"SELECT * FROM t_car_no_history WHERE {where} ORDER BY changed_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    records = await CarNoHistory.execute(sql, params)
    
    return {
        "success": True,
        "records": records,
        "total": total,
        "currentPage": current_page,
        "pageSize": page_size
    }
```

**Step 3: 提交**

```bash
git add yail/www/handlers/car/index.py
git commit -m "feat(car): 添加 /car/history 和 /car/car_no_history 查询接口"
```

---

## Task 7: 前端 CarHistory.vue 组件

**File:** Create: `frontEnd/src/components/Container/car/CarHistory.vue`

**Step 1: 创建组件**

```vue
<template>
  <el-dialog
    title="历史记录"
    :visible.sync="visible"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeTab">
      <el-tab-pane label="删除历史" name="delete">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="deleteSearch.carNo"
            placeholder="车牌号"
            style="width: 150px"
            @keyup.enter.native="loadDeleteHistory"
          />
          <el-date-picker
            v-model="deleteSearch.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            style="width: 240px"
          />
          <el-button @click="loadDeleteHistory">搜索</el-button>
        </div>
        
        <!-- 表格 -->
        <el-table :data="deleteList" v-loading="deleteLoading">
          <el-table-column prop="carid" label="车牌号" />
          <el-table-column prop="user_name" label="姓名" />
          <el-table-column prop="dept" label="部门" />
          <el-table-column prop="brand" label="品牌" />
          <el-table-column prop="deleted_at" label="删除时间" />
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          layout="total, prev, pager, next"
          :total="deleteTotal"
          :page-size="deleteQuery.pageSize"
          :current-page="deleteQuery.currentPage"
          @current-change="handleDeletePageChange"
        />
      </el-tab-pane>
      
      <el-tab-pane label="车牌号变更" name="carno">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="carnoSearch.carNo"
            placeholder="车牌号"
            style="width: 150px"
            @keyup.enter.native="loadCarNoHistory"
          />
          <el-date-picker
            v-model="carnoSearch.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            style="width: 240px"
          />
          <el-button @click="loadCarNoHistory">搜索</el-button>
        </div>
        
        <!-- 表格 -->
        <el-table :data="carnoList" v-loading="carnoLoading">
          <el-table-column prop="old_car_no" label="原车牌号" />
          <el-table-column prop="new_car_no" label="新车牌号" />
          <el-table-column prop="changed_at" label="变更时间" />
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          layout="total, prev, pager, next"
          :total="carnoTotal"
          :page-size="carnoQuery.pageSize"
          :current-page="carnoQuery.currentPage"
          @current-change="handleCarNoPageChange"
        />
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
</template>

<script>
export default {
  name: 'CarHistory',
  data() {
    return {
      visible: false,
      activeTab: 'delete',
      deleteList: [],
      deleteTotal: 0,
      deleteLoading: false,
      deleteSearch: {
        carNo: '',
        dateRange: []
      },
      deleteQuery: {
        currentPage: 1,
        pageSize: 20
      },
      carnoList: [],
      carnoTotal: 0,
      carnoLoading: false,
      carnoSearch: {
        carNo: '',
        dateRange: []
      },
      carnoQuery: {
        currentPage: 1,
        pageSize: 20
      }
    }
  },
  methods: {
    open() {
      this.visible = true
      this.loadDeleteHistory()
    },
    loadDeleteHistory() {
      this.deleteLoading = true
      this.post({
        url: 'car/history',
        data: {
          currentPage: this.deleteQuery.currentPage,
          pageSize: this.deleteQuery.pageSize,
          carNo: this.deleteSearch.carNo,
          startDate: this.deleteSearch.dateRange?.[0] || '',
          endDate: this.deleteSearch.dateRange?.[1] || ''
        }
      }).then(res => {
        this.deleteList = res.records || []
        this.deleteTotal = res.total || 0
      }).finally(() => {
        this.deleteLoading = false
      })
    },
    handleDeletePageChange(page) {
      this.deleteQuery.currentPage = page
      this.loadDeleteHistory()
    },
    loadCarNoHistory() {
      this.carnoLoading = true
      this.post({
        url: 'car/car_no_history',
        data: {
          currentPage: this.carnoQuery.currentPage,
          pageSize: this.carnoQuery.pageSize,
          carNo: this.carnoSearch.carNo,
          startDate: this.carnoSearch.dateRange?.[0] || '',
          endDate: this.carnoSearch.dateRange?.[1] || ''
        }
      }).then(res => {
        this.carnoList = res.records || []
        this.carnoTotal = res.total || 0
      }).finally(() => {
        this.carnoLoading = false
      })
    },
    handleCarNoPageChange(page) {
      this.carnoQuery.currentPage = page
      this.loadCarNoHistory()
    }
  }
}
</script>

<style lang="scss" scoped>
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}
</style>
```

**Step 2: 提交**

```bash
git add frontEnd/src/components/Container/car/CarHistory.vue
git commit -m "feat(car): 添加 CarHistory 历史记录组件"
```

---

## Task 8: 在 CarList.vue 集成历史入口

**File:** Modify: `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 引入组件**

在 script 中 import CarHistory 并注册

**Step 2: 添加历史按钮**

在搜索栏合适位置添加历史图标按钮

**Step 3: 提交**

```bash
git add frontEnd/src/components/Container/car/CarList.vue
git commit -m "feat(car): 在 CarList 集成历史记录入口"
```

---

## Task 9: 整体测试

1. 启动后端
2. 启动前端
3. 测试删除车辆，查看历史
4. 测试修改车牌号，查看变更历史
