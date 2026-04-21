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
| user_name | TEXT | 姓名（变更时的车主姓名） |
| old_car_no | TEXT | 原车牌号 |
| new_car_no | TEXT | 新车牌号 |
| changed_at | TEXT | 变更时间 |

### 表3: t_car_info_history_pics（删除历史图片）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| history_id | INTEGER | 关联 t_car_info_history.id |
| path | TEXT | 图片路径 |
| created_at | TEXT | 原图片创建时间 |

**说明：** 删除车辆时，同步保存该车辆的图片记录到历史图片表。早期删除的记录（无图片）pics 返回空数组。

## 后端改动

### 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/car/history` | POST | 分页查询删除历史（支持关键词、车牌号、日期筛选） |
| `/car/car_no_history` | POST | 分页查询车牌号变更历史（支持关键词、日期筛选） |

### 修改接口

| 接口 | 改动 |
|------|------|
| `/car/delete` | 硬删除改为插入历史表后再删除 |
| `/car/update` | 车牌号变更时记录到 t_car_no_history |

### 注意事项

**获取请求数据：** 使用 `request.__data__` 获取已解析的 JSON 数据，不要使用 `await request.post()`。因为 `www.filters.filters` 中的 `parse_data` 中间件已经将 JSON 请求体解析并存储在 `request.__data__` 中。

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
      "deletedAt": "2026-04-20 10:00:00",
      "pics": ["path1.jpg", "path2.jpg"]
    }
  ],
  "total": 100,
  "currentPage": 1,
  "pageSize": 20
}
```

**注意：** `pics` 字段为图片路径数组，早期删除的记录返回空数组 `[]`。

**车牌号变更 `/car/car_no_history`：**
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "carId": 10,
      "userName": "张三",
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
- 右侧操作按钮区域（`.button-group`）：批量导入、新增(+)、历史记录，三个按钮并排靠右对齐

### CarHistory.vue（新增）
- Tab 切换：删除历史 / 车牌号变更
- 搜索框：单一输入框，支持车牌号或姓名搜索（按回车触发搜索），与 CarList.vue 搜索体验一致
- 日期范围选择器
- 分页表格展示
- 日期显示：只显示到日期（不含时间）
- 图片列：
  - 无图片：显示 "-"
  - 有图片：显示 📷 N（hover 时弹出 popover 展示缩略图，最多显示 4 张，多余显示 +N）
  - 点击缩略图：弹出 el-dialog 预览大图
  - 图片路径：`/static/car/{path}`

## 交互流程

```
CarList.vue
  → 点击「历史记录」图标
  → 弹出 CarHistory.vue 弹窗
  → Tab1: 删除历史列表
     - 搜索框：输入车牌号或姓名（按回车搜索）
     - 日期范围：按删除时间筛选
     - 分页展示
     - 图片列：hover 显示缩略图，点击预览大图
  → Tab2: 车牌号变更列表
     - 搜索框：输入姓名或车牌号（支持老车牌/新车牌，按回车搜索）
     - 日期范围：按变更时间筛选
     - 分页展示
```

## API 请求格式

**删除历史 `/car/history`：**
```json
{
  "currentPage": 1,
  "pageSize": 20,
  "keyword": "张三",       // 支持车牌号或姓名搜索
  "startDate": "2026-04-01",
  "endDate": "2026-04-30"
}
```

**车牌号变更 `/car/car_no_history`：**
```json
{
  "currentPage": 1,
  "pageSize": 20,
  "keyword": "张三",        // 支持姓名、老车牌号、新车牌号搜索
  "startDate": "2026-04-01",
  "endDate": "2026-04-30"
}
```

## 界面设计（遵循 webflow 规范）

- 主色调：#146ef5
- 按钮样式：与页面风格一致
- Tab 样式：el-tabs
- 表格样式：el-table
- 分页样式：el-pagination
