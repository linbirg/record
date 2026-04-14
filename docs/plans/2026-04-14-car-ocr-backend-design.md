# OCR 后端接口设计

## 1. 概述

将 OCR（光学字符识别）功能从前端移至后端，统一由后端调用 MiniMax VLM API，保护 API Key 安全。

### 当前问题

- 前端直接调用 MiniMax Vision API，API Key 暴露在浏览器代码中
- 需要在每个前端页面传递 `ocrApiKey` prop
- 安全风险：API Key 可被直接查看和滥用

### 解决方案

- 后端提供 `/car/ocr` 接口，统一调用 MiniMax VLM API
- 前端只需传递图片 base64 和识别类型
- API Key 由后端配置文件管理，不暴露给前端

## 2. 技术方案

### 2.1 配置

**文件：** `conf/dev.py`

| 配置项 | 值 |
|--------|-----|
| `OPENAI_API_KEY` | MiniMax API Key |

### 2.2 VLM API 调用

使用 MiniMax MCP VLM API 端点：

**端点：** `POST https://api.minimaxi.com/v1/coding_plan/vlm`

**Headers：**
```
Authorization: Bearer {OPENAI_API_KEY}
Content-Type: application/json
MM-API-Source: Minimax-MCP
```

**请求格式：**
```json
{
  "prompt": "从行驶证图片中提取：姓名、车牌号、车辆品牌、型号、注册日期。只返回JSON格式：{\"Name\":\"\",\"carNo\":\"\",\"brand\":\"\",\"model\":\"\",\"regDate\":\"\"}",
  "image_url": "data:image/jpeg;base64,{base64}"
}
```

### 2.3 图片格式

- Base64 加上前缀：`data:image/jpeg;base64,{base64}`
- 图片格式统一为 JPEG

## 3. 接口设计

### 3.1 请求接口

**端点：** `POST /car/ocr`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | string | 是 | Base64 图片内容（不含前缀） |
| type | string | 是 | 识别类型：`driving`（行驶证）或 `driver`（驾驶证） |

**请求示例：**
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",
  "type": "driving"
}
```

### 3.2 响应接口

**成功响应：**

| type | 响应 |
|------|------|
| driving | `{"name": "施明霞", "carNo": "沪AFN7295", "brand": "比亚迪牌", "model": "BYD7152WTSHEVC2", "regDate": "2022-12-03"}` |
| driver | `{"name": "张三"}` |

**错误响应：**

| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误（无效的 type） |
| 500 | MiniMax API 调用失败 |

### 3.3 Prompt 设计

| type | Prompt |
|------|--------|
| driving | `从行驶证图片中提取：姓名、车牌号、车辆品牌、型号、注册日期。只返回JSON格式：{\"Name\":\"\",\"carNo\":\"\",\"brand\":\"\",\"model\":\"\",\"regDate\":\"\"}` |
| driver | `从驾驶证图片中提取：姓名。只返回JSON格式：{\"Name\":\"\"}` |

## 4. 实现

### 4.1 后端实现 `yail/www/handlers/car/index.py`

```python
VLM_API_HOST = "https://api.minimaxi.com"

async def call_vision(image_base64: str, prompt: str) -> str:
    import aiohttp
    
    image_url = f"data:image/jpeg;base64,{image_base64}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{VLM_API_HOST}/v1/coding_plan/vlm",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
                "MM-API-Source": "Minimax-MCP"
            },
            json={
                "prompt": prompt,
                "image_url": image_url
            }
        ) as resp:
            data = await resp.json()
            if data.get("base_resp", {}).get("status_code") != 0:
                raise aiohttp.HTTPError(500, data.get("base_resp", {}).get("status_msg", "VLM API error"))
            return data.get("content", "")


@post("/car/ocr")
@ResponseBody
async def ocr(image: str, type: str):
    prompts = {
        "driving": "从行驶证图片中提取：姓名、车牌号、车辆品牌、型号、注册日期。只返回JSON格式：{\"Name\":\"\",\"carNo\":\"\",\"brand\":\"\",\"model\":\"\",\"regDate\":\"\"}",
        "driver": "从驾驶证图片中提取：姓名。只返回JSON格式：{\"Name\":\"\"}"
    }
    
    if type not in prompts:
        raise aiohttp.HTTPError(400, "Invalid type")
    
    content = await call_vision(image, prompts[type])
    
    json_str = re.sub(r'```json\n?|```\n?', '', content).strip()
    return json.loads(json_str)
```

### 4.2 前端实现 `frontEnd/src/components/Container/car/Step1Upload.vue`

```javascript
async ocrImage(base64, type) {
  const response = await this.$http.post('/car/ocr', {
    image: base64,
    type
  });
  return response.data;
}
```

### 4.3 前端 OCR 结果处理 `Step2Confirm.vue`

```javascript
watch: {
  ocrResults: {
    immediate: true,
    handler(results) {
      if (results.driving) {
        const d = results.driving;
        if (d.carNo) this.form.carNo = d.carNo;
        if (d.brand) this.form.brand = d.brand;
        if (d.model) this.form.model = d.model;
        if (d.regDate) this.form.regDate = d.regDate;
        if (d.name) this.form.name = d.name;  // 从行驶证获取车主姓名
      }
      if (!this.form.name && results.driver && results.driver.name) {
        this.form.name = results.driver.name;  // fallback 到驾驶证
      }
    }
  }
}
```

## 5. 文件变更清单

| 文件 | 操作 |
|------|------|
| `yail/www/handlers/car/index.py` | 新增 VLM API 调用函数、/car/ocr 端点 |
| `frontEnd/src/components/Container/car/Step1Upload.vue` | 简化 ocrImage 调用后端接口 |
| `frontEnd/src/components/Container/car/Step2Confirm.vue` | 修复 name 字段读取逻辑 |
| `frontEnd/src/components/Container/car/CarRegistration.vue` | 移除 ocrApiKey prop |
| `frontEnd/src/components/Container/car/CarList.vue` | 移除 ocrApiKey 相关代码 |

## 6. 测试结果

### 行驶证识别测试

**输入：** 行驶证图片 base64

**输出：**
```json
{
  "name": "施明霞",
  "carNo": "沪AFN7295",
  "brand": "比亚迪牌",
  "model": "BYD7152WTSHEVC2",
  "regDate": "2022-12-03"
}
```

## 7. 相关文档

- 知识库：`D:\project\linbirg\obsidian\_raw\record\design\2026-04-14-car-ocr-backend-design.md`
- MiniMax VLM API：`Python集成MiniMax图像理解功能完整指南.md`