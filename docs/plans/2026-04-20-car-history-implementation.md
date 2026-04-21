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

from . import field_desc as fd
from .base import AutoIdModel


class CarInfoHistory(AutoIdModel):
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
    # 注意：字段名是 deleted_at，不是 created_at
    deleted_at = fd.CreatedAtField(name="deleted_at")


class CarNoHistory(AutoIdModel):
    __table__ = "t_car_no_history"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    car_id = fd.IntField(name="car_id")
    user_name = fd.UserNameField()  # 记录变更时的车主姓名
    old_car_no = fd.CarNoField()
    new_car_no = fd.CarNoField()
    # 注意：字段名是 changed_at，不是 created_at
    changed_at = fd.CreatedAtField(name="changed_at")
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
    from www.dao.car_history import CarInfoHistory
    import datetime

    history = CarInfoHistory()
    history.original_id = self.no
    history.user_name = self.name
    history.dept = self.dept
    history.carid = self.carNo
    history.brand = self.brand
    history.car_license = self.carLicense
    history.license = self.license
    history.abbr = self.abbr
    # 显式设置 deleted_at，避免字段名不匹配导致插入失败
    history.deleted_at = datetime.datetime.now().isoformat()
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
    logger.LOG_INFO("[car/delete] no=%s", no)
    car = await CarInfo.find_one(no=no)
    if not car:
        logger.LOG_WARNING("[car/delete] car not found, no=%s", no)
        return Message("ok!")
    
    logger.LOG_INFO("[car/delete] saving to history: name=%s, carNo=%s", car.name, car.carNo)
    await car.save_to_history()
    logger.LOG_INFO("[car/delete] history saved, now deleting car")
    
    pics = await CarPics.find(carID=car.no)
    for p in pics:
        pic_path = "/".join([PIC_DIR, p.path])
        if os.path.exists(pic_path):
            os.remove(pic_path)
        await p.delete()
    
    await car.delete()
    logger.LOG_INFO("[car/delete] car deleted successfully, no=%s", no)
    return Message("ok!")
```

**Step 2: 提交**

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
    
    logger.LOG_INFO("test! carInfo.name=%s", carInfo.name)
    car = await CarInfo.find_one(no=carInfo.no)
    
    # 记录车牌号变更
    if car.carNo != carInfo.carNo:
        history = CarNoHistory()
        history.car_id = car.no
        history.user_name = car.name  # 记录变更时的车主姓名
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

**注意：** 
- 使用 `Model.select()` 方法执行 SELECT 查询（返回字典列表），而不是 `execute()`（返回受影响的行数）。
- **重要：** 获取请求数据应使用 `request.__data__`，而不是 `await request.post()`。因为 `www.filters.filters` 中的 `parse_data` 中间件已经将 JSON 请求体解析并存储在 `request.__data__` 中。

**Step 1: 添加 /car/history 接口**

```python
@post("/car/history")
@ResponseBody
async def get_history(request):
    from www.dao.car_history import CarInfoHistory
    
    data = request.__data__  # 使用 filter 已解析的数据，不要用 await request.post()
    current_page = int(data.get("currentPage", 1))
    page_size = int(data.get("pageSize", 20))
    keyword = (data.get("keyword", "") or "").strip()
    start_date = (data.get("startDate", "") or "").strip()
    end_date = (data.get("endDate", "") or "").strip()
    
    where = "1=1"
    params = []
    if keyword:
        # 支持车牌号或姓名搜索
        where += " AND (user_name LIKE ? OR carid LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if start_date:
        where += " AND deleted_at >= ?"
        params.append(start_date)
    if end_date:
        where += " AND deleted_at <= ?"
        params.append(end_date)
    
    count_sql = f"SELECT COUNT(*) FROM t_car_info_history WHERE {where}"
    count_result = await CarInfoHistory.select(count_sql, params)
    total = count_result[0]["COUNT(*)"] if count_result else 0
    
    offset = (current_page - 1) * page_size
    sql = f"SELECT * FROM t_car_info_history WHERE {where} ORDER BY deleted_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    records = await CarInfoHistory.select(sql, params)
    
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
    
    data = request.__data__  # 使用 filter 已解析的数据
    current_page = int(data.get("currentPage", 1))
    page_size = int(data.get("pageSize", 20))
    keyword = (data.get("keyword", "") or "").strip()
    start_date = (data.get("startDate", "") or "").strip()
    end_date = (data.get("endDate", "") or "").strip()
    
    where = "1=1"
    params = []
    if keyword:
        where += " AND (user_name LIKE ? OR old_car_no LIKE ? OR new_car_no LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    if start_date:
        where += " AND changed_at >= ?"
        params.append(start_date)
    if end_date:
        where += " AND changed_at <= ?"
        params.append(end_date)
    
    count_sql = f"SELECT COUNT(*) FROM t_car_no_history WHERE {where}"
    count_result = await CarNoHistory.select(count_sql, params)
    total = count_result[0]["COUNT(*)"] if count_result else 0
    
    offset = (current_page - 1) * page_size
    sql = f"SELECT * FROM t_car_no_history WHERE {where} ORDER BY changed_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    records = await CarNoHistory.select(sql, params)
    
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
        <!-- 搜索栏：单一输入框，支持车牌号或姓名搜索，按回车搜索 -->
        <div class="search-bar">
          <el-input
            v-model="deleteSearch.keyword"
            placeholder="车牌号或姓名搜索"
            style="width: 200px"
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
          <el-table-column prop="deleted_at" label="删除日期" :formatter="formatDate" />
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
        <!-- 搜索栏：单一输入框，按回车搜索 -->
        <div class="search-bar">
          <el-input
            v-model="carnoSearch.keyword"
            placeholder="车牌号搜索"
            style="width: 200px"
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
          <el-table-column prop="changed_at" label="变更日期" :formatter="formatDate" />
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
import { mapActions } from 'vuex'

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
        keyword: '',
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
        keyword: '',
        dateRange: []
      },
      carnoQuery: {
        currentPage: 1,
        pageSize: 20
      }
    }
  },
  methods: {
    ...mapActions(['post']),
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
          keyword: this.deleteSearch.keyword,
          startDate: (this.deleteSearch.dateRange && this.deleteSearch.dateRange[0]) || '',
          endDate: (this.deleteSearch.dateRange && this.deleteSearch.dateRange[1]) || ''
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
          keyword: this.carnoSearch.keyword,
          startDate: (this.carnoSearch.dateRange && this.carnoSearch.dateRange[0]) || '',
          endDate: (this.carnoSearch.dateRange && this.carnoSearch.dateRange[1]) || ''
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
    },
    formatDate(row, column, cellValue) {
      if (!cellValue) return ''
      return cellValue.split(' ')[0]
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

**Step 2: 添加右侧按钮组**

在搜索栏右侧添加 `.button-group` 包裹的按钮组（批量导入、新增+、历史记录），三个按钮靠右并齐：

```vue
<div class="button-group">
  <button v-if="batchImportEnabled" class="add-btn" @click="openImportDialog">
    <!-- 批量导入图标 -->
  </button>
  <button class="icon-btn" @click="showAddDialog" title="新增车辆">
    <!-- + 号图标 -->
  </button>
  <button class="icon-btn" @click="openHistoryDialog" title="历史记录">
    <!-- 时钟图标 -->
  </button>
</div>
```

对应的 CSS：
```scss
.button-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
```

**Step 3: 添加 openHistoryDialog 方法**

```javascript
openHistoryDialog() {
  this.$refs.carHistory.open()
}
```

**Step 4: 提交**

```bash
git add frontEnd/src/components/Container/car/CarList.vue
git commit -m "feat(car): 在 CarList 集成历史记录入口"
```

---

## Task 9: 整体测试

1. 启动后端
2. 启动前端
3. 测试删除车辆，查看历史（含图片）
4. 测试修改车牌号，查看变更历史（验证显示姓名）
5. 测试图片 hover popover 和点击预览

---

## Task 10: 新增历史图片表迁移

**File:** Create: `yail/tools/migrate_sqlite/7_car_history_pics.py`

```python
import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_info_history_pics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER,
        path TEXT,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration 7: car_history_pics table created successfully")
```

**运行迁移：**
```bash
cd yail
python tools/migrate_sqlite/7_car_history_pics.py
```

---

## Task 11: 新增 CarInfoHistoryPics DAO

**File:** Modify: `yail/www/dao/car_history.py`

在文件末尾添加：
```python
class CarInfoHistoryPics(AutoIdModel):
    __table__ = "t_car_info_history_pics"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    history_id = fd.IntField(name="history_id")
    path = fd.PicPathField()
    created_at = fd.CreatedAtField()
```

---

## Task 12: 修改 save_to_history 保存图片

**File:** Modify: `yail/www/dao/car_info.py`

```python
async def save_to_history(self):
    """保存当前记录到历史表（含图片）"""
    from www.dao.car_history import CarInfoHistory, CarInfoHistoryPics
    from www.dao.car_pics import CarPics
    import datetime

    history = CarInfoHistory()
    history.original_id = self.no
    history.user_name = self.name
    history.dept = self.dept
    history.carid = self.carNo
    history.brand = self.brand
    history.car_license = self.carLicense
    history.license = self.license
    history.abbr = self.abbr
    history.deleted_at = datetime.datetime.now().isoformat()
    await history.save()

    pics = await CarPics.find(carID=self.no)
    for pic in pics:
        history_pic = CarInfoHistoryPics()
        history_pic.history_id = history.id
        history_pic.path = pic.path
        history_pic.created_at = pic.created_at
        await history_pic.save()
```

---

## Task 13: 修改 /car/history 返回图片信息

**File:** Modify: `yail/www/handlers/car/index.py`

在 `get_history` 函数中，查询历史记录后，为每条记录添加 pics 字段：
```python
from www.dao.car_history import CarInfoHistory, CarInfoHistoryPics

# ... 查询 records 后 ...

for record in records:
    pics_sql = f"SELECT path FROM t_car_info_history_pics WHERE history_id = {record['id']}"
    pics_result = await CarInfoHistoryPics.select(pics_sql)
    record['pics'] = [p['path'] for p in pics_result] if pics_result else []
```

---

## Task 14: 车牌号变更记录增加姓名字段

**问题：** 车牌号变更历史记录中缺少车主姓名

**Step 1: 创建迁移脚本**

**File:** Create: `yail/tools/migrate_sqlite/8_car_no_history_name.py`

```python
import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE t_car_no_history ADD COLUMN user_name TEXT')
    conn.commit()
    conn.close()
    print("Migration 8: added user_name column to t_car_no_history")

def down():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE t_car_no_history DROP COLUMN user_name')
    conn.commit()
    conn.close()
    print("Migration 8: dropped user_name column from t_car_no_history")
```

**Step 2: 修改 CarNoHistory DAO**

```python
class CarNoHistory(AutoIdModel):
    __table__ = "t_car_no_history"

    id = fd.IntField(name="id", primary_key=True, auto_increment=True)
    car_id = fd.IntField(name="car_id")
    user_name = fd.UserNameField()  # 新增
    old_car_no = fd.CarNoField()
    new_car_no = fd.CarNoField()
    changed_at = fd.CreatedAtField(name="changed_at")
```

**Step 3: 修改 /car/update 中的记录逻辑**

```python
if car.carNo != carInfo.carNo:
    history = CarNoHistory()
    history.car_id = car.no
    history.user_name = car.name  # 记录变更时的车主姓名
    history.old_car_no = car.carNo
    history.new_car_no = carInfo.carNo
    await history.save()
```

**Step 4: 修改前端车牌号变更列表**

在 `CarHistory.vue` 的车牌号变更 Tab 中：
- 增加"姓名"列
- 搜索框 placeholder 改为"姓名或车牌号搜索"

```vue
<el-table-column prop="user_name" label="姓名" />
```

**搜索支持：** `/car/car_no_history` 接口的 keyword 参数支持按 `user_name`、`old_car_no`、`new_car_no` 模糊搜索。

**Step 5: 提交**

```bash
git add yail/tools/migrate_sqlite/8_car_no_history_name.py
git add yail/www/dao/car_history.py
git add yail/www/handlers/car/index.py
git add frontEnd/src/components/Container/car/CarHistory.vue
git commit -m "feat(car): 车牌号变更记录增加姓名字段"
```

---

## Task 15: 前端 CarHistory.vue 展示图片

**File:** Modify: `frontEnd/src/components/Container/car/CarHistory.vue`

**主要改动：**
1. 表格增加"图片"列（最后一列）
2. 使用 `<el-popover>` 实现 hover 显示缩略图
3. 缩略图最多显示 4 张，多余显示 +N
4. 点击缩略图弹出 `<el-dialog>` 预览大图
5. 无图片显示 "-"

```vue
<el-table-column label="图片" width="80" align="center">
  <template slot-scope="scope">
    <span v-if="scope.row.pics && scope.row.pics.length > 0">
      <el-popover placement="top" trigger="hover">
        <div class="pic-popover">
          <div class="pic-list">
            <img v-for="(pic, idx) in scope.row.pics.slice(0, 4)"
                 :key="idx"
                 :src="getPicUrl(pic)"
                 class="pic-thumb"
                 @click="previewPic(getPicUrl(pic))" />
            <span v-if="scope.row.pics.length > 4" class="pic-more">
              +{{ scope.row.pics.length - 4 }}
            </span>
          </div>
        </div>
        <span slot="reference" class="pic-badge">
          📷 {{ scope.row.pics.length }}
        </span>
      </el-popover>
    </span>
    <span v-else class="pic-none">-</span>
  </template>
</el-table-column>
```

---

## 已知问题和解决方案

### 问题1: ORM 字段名与数据库列名不匹配

**现象：** `sqlite3.OperationalError: table t_car_info_history has no column named created_at`

**原因：** `CreatedAtField()` 默认列名为 `created_at`，但数据库表中是 `deleted_at`

**解决：** 使用 `fd.CreatedAtField(name="deleted_at")` 明确指定列名

### 问题2: deleted_at 字段为 NULL

**原因：** ORM 插入时没有显式设置 deleted_at 字段值

**解决：** 在 `save_to_history` 方法中显式设置 `deleted_at = datetime.datetime.now().isoformat()`

### 问题3: execute() 方法返回整数而非 cursor

**原因：** `Model.execute()` 用于 DML 操作返回 affected rows，不适合 SELECT 查询

**解决：** 使用 `Model.select()` 方法执行 SELECT 查询，它返回字典列表

### 问题4: 热重载导致数据不一致

**现象：** 删除操作进行中时，热重载杀死了进程

**原因：** pymonitor 监控文件变化触发重启

**解决：** 确保删除和保存历史操作尽快完成，避免在事务中间被中断

### 问题5: request.post() 无法获取 JSON 请求体数据

**现象：** 搜索参数 `keyword='E'` 被传递，但 handler 中 `data.get("keyword")` 返回空值

**原因：** `www.filters.filters` 中的 `parse_data` 中间件已经将 JSON 请求体解析并存储在 `request.__data__` 中，此时如果再用 `await request.post()` 获取数据会得到空的 `MultiDictProxy()`

**解决：** 使用 `data = request.__data__` 获取已解析的请求数据，不要使用 `await request.post()`