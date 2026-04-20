# 批量导入按钮配置开关

## 需求

在车辆列表页面增加配置开关，可隐藏/显示「批量导入」按钮。

## 实现方案

### 1. 后端配置 `yail/conf/dev.py`

```python
# === 功能开关 ===
ENABLE_BATCH_IMPORT = True  # 批量导入Word功能开关
```

### 2. 后端 API `yail/www/handlers/system.py`

新增 `/system/config` 接口统一返回系统配置：

```python
@post("/system/config")
@ResponseBody
async def get_system_config(request):
    from conf.dev import ENABLE_BATCH_IMPORT
    return {
        "enableBatchImport": ENABLE_BATCH_IMPORT
    }
```

### 3. 前端 `frontEnd/src/components/Container/car/CarList.vue`

- data 中添加 `batchImportEnabled: false`
- created 或 mounted 中调用 `/system/config` 获取配置
- 模板中按钮使用 `v-if="batchImportEnabled"` 条件渲染

## 数据流程

```
CarList.vue mounted
  → GET /system/config
  → { enableBatchImport: true/false }
  → batchImportEnabled
  → v-if="batchImportEnabled" 控制按钮显示
```
