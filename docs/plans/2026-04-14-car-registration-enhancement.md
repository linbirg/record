# 车辆登记功能增强实现计划

## 1. 概述

对车辆登记功能进行三项增强：
1. 注册日期默认当前日期
2. 完成登记后自动刷新列表
3. 提交时保存证件照片（驾驶证不识别只留档）

## 2. 流程

```
Step1: 上传证件 → /car/ocr 识别行驶证（获取 name）
Step2: 用户确认信息
Step3: /car/add 提交车辆信息 + 保存证件图片 → 完成跳转
```

## 3. 证件命名规则

| 证件 | 命名 |
|------|------|
| 行驶证 | `{Name}_{timestamp}_行驶证.jpg` |
| 驾驶证 | `{Name}_{timestamp}_驾驶证.jpg` |

## 4. 图片与车辆关联机制

**数据库表结构**：
- `t_car_info`: 车辆信息表，主键 `id`
- `t_car_pics`: 车辆图片表，外键 `car_id` → `t_car_info.id`

**关联流程**：
```
car.save() 执行后，car.no 自动获得 lastrowid
→ 使用 car.no 创建 CarPics(carID=car.no, path=filename)
```

## 5. 实现清单

### 5.1 注册日期默认当前日期

**文件**: `frontEnd/src/components/Container/car/Step2Confirm.vue`

```javascript
// data() 中 form 对象
regDate: new Date().toISOString().split('T')[0],  // 默认今天 YYYY-MM-DD
```

### 5.2 完成登记跳转列表时自动刷新

**文件**: `frontEnd/src/components/Container/car/CarList.vue`

```vue
<CarRegistration 
  v-if="registrationDialogVisible"
  @close="registrationDialogVisible = false; fetchCarList();"
/>
```

### 5.3 提交时保存证件照片

#### 后端 - `/car/add` 端点

**文件**: `yail/www/handlers/car/index.py`

**新增导入**:
```python
import base64
import time
```

**修改 `add` 函数**:
```python
@post("/car/add")
@ResponseBody
@RequestBody("carInfo", kls=VoCarInfo)
async def add(carInfo):
    # 保存行驶证
    if carInfo.drivingLicense:
        timestamp = int(time.time())
        driving_filename = f"{carInfo.name}_{timestamp}_行驶证.jpg"
        driving_path = "/".join([PIC_DIR, driving_filename])
        with open(driving_path, "wb") as f:
            f.write(base64.b64decode(carInfo.drivingLicense))
    
    # 保存驾驶证
    if carInfo.driverLicense:
        timestamp = int(time.time())
        driver_filename = f"{carInfo.name}_{timestamp}_驾驶证.jpg"
        driver_path = "/".join([PIC_DIR, driver_filename])
        with open(driver_path, "wb") as f:
            f.write(base64.b64decode(carInfo.driverLicense))
    
    # 保存车辆信息
    car = CarInfo()
    car.name = carInfo.name
    car.dept = carInfo.dept
    car.carNo = carInfo.carNo
    car.brand = carInfo.brand
    car.license = carInfo.license
    car.carLicense = carInfo.carLicense
    car.abbr = carInfo.abbr
    
    await car.save()
    
    # 保存图片记录并关联到车辆
    if carInfo.drivingLicense:
        pic1 = CarPics(carID=car.no, path=driving_filename)
        await pic1.save()
    if carInfo.driverLicense:
        pic2 = CarPics(carID=car.no, path=driver_filename)
        await pic2.save()
    
    msg = Message("ok!")
    msg.data = {"no": car.no}
    return msg
```

#### 前端 - `CarRegistration.vue`

```javascript
async onStep2Submit(formData) {
  try {
    const requestData = {
      ...formData,
      drivingLicense: this.step1Data.drivingLicense || null,
      driverLicense: this.step1Data.driverLicense || null
    };
    
    await this.post({
      url: 'car/add',
      data: requestData
    });
    
    this.submittedCar = {
      name: formData.name,
      carNo: formData.carNo
    };
    
    this.currentStep = 3;
  } catch (error) {
    console.error('提交失败:', error);
    this.$message.error('添加失败，请稍后重试');
  }
}
```

## 6. 文件变更清单

| 文件 | 修改内容 |
|------|----------|
| `yail/www/handlers/car/index.py` | `/car/add` 添加图片保存逻辑，添加 base64, time 导入 |
| `frontEnd/src/components/Container/car/Step2Confirm.vue` | regDate 默认当天日期 |
| `frontEnd/src/components/Container/car/CarRegistration.vue` | 提交时传递图片数据 |
| `frontEnd/src/components/Container/car/CarList.vue` | 关闭弹窗后刷新列表 |

## 7. 相关文档

- 知识库：`D:\project\linbirg\obsidian\_raw\record\design\2026-04-14-car-ocr-backend-design.md`