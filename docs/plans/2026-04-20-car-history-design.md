# 车辆历史记录功能设计

## 需求

记录删除的车辆信息和车牌号变更情况，便于追溯管理。

## 数据表设计

### 表1: t_car_info_history（删除历史）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| original_id | INTEGER | 原车辆ID（关联 t_car_info.id） |
| user_name | TEXT | 姓名 |
| dept | TEXT | 部门 |
| carid | TEXT | 车牌号（删除时） |
| brand | TEXT | 品牌 |
| car_license | TEXT | 行驶证 |
| license | TEXT | 驾驶证 |
| abbr | TEXT | 备注 |
| deleted_at | TEXT | 删除时间 |

### 表2: t_car_no_history（车牌号变更）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| car_id | INTEGER | 车辆ID（关联 t_car_info.id） |
| old_car_no | TEXT | 原车牌号 |
| new_car_no | TEXT | 新车牌号 |
| changed_at | TEXT | 变更时间 |

## 后端改动

### 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/car/history` | POST | 分页查询删除历史（支持车牌号、日期筛选） |
| `/car/car_no_history` | POST | 分页查询车牌号变更历史 |

### 修改接口

| 接口 | 改动 |
|------|------|
| `/car/delete` | 硬删除改为插入历史表后再删除 |
| `/car/update` | 车牌号变更时记录到 t_car_no_history |

### API 响应格式

**删除历史 `/car/history`：**
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "originalId": 10,
      "userName": "张三",
      "dept": "技术部",
      "carid": "京A12345",
      "brand": "宝马",
      "carLicense": "京A12345",
      "license": "123456789",
      "abbr": "",
      "deletedAt": "2026-04-20 10:00:00"
    }
  ],
  "total": 100,
  "currentPage": 1,
  "pageSize": 20
}
```

**车牌号变更 `/car/car_no_history`：**
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "carId": 10,
      "oldCarNo": "京A11111",
      "newCarNo": "京A22222",
      "changedAt": "2026-04-20 10:00:00"
    }
  ],
  "total": 50,
  "currentPage": 1,
  "pageSize": 20
}
```

## 前端改动

### CarList.vue
- 添加「历史记录」图标入口按钮（webflow 规范，较小不显眼）

### CarHistory.vue（新增）
- Tab 切换：删除历史 / 车牌号变更
- 搜索框：按车牌号筛选
- 日期范围选择器
- 分页表格展示

## 交互流程

```
CarList.vue
  → 点击「历史记录」图标
  → 弹出 CarHistory.vue 弹窗
  → Tab1: 删除历史列表
     - 搜索框：按车牌号筛选
     - 日期范围：按删除时间筛选
     - 分页展示
  → Tab2: 车牌号变更列表
     - 搜索框：按车牌号筛选
     - 日期范围：按变更时间筛选
     - 分页展示
```

## 界面设计（遵循 webflow 规范）

- 主色调：#146ef5
- 按钮样式：与页面风格一致
- Tab 样式：el-tabs
- 表格样式：el-table
- 分页样式：el-pagination
