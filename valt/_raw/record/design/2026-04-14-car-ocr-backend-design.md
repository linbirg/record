# OCR 后端接口设计

## 1. 概述

将 OCR（光学字符识别）功能从前端移至后端，统一由后端调用 MiniMax Vision API，保护 API Key 安全。

### 当前问题

- 前端直接调用 MiniMax Vision API，API Key 暴露在浏览器代码中
- 需要在每个前端页面传递 `ocrApiKey` prop
- 安全风险：API Key 可被直接查看和滥用

### 解决方案

- 后端提供 `/car/ocr` 接口，统一调用 MiniMax Vision API
- 前端只需传递图片 base64 和识别类型
- API Key 由后端配置文件管理，不暴露给前端

## 2. 技术方案

### 2.1 配置复用

**文件：** `conf/dev.py`

| 配置项 | 值 |
|--------|-----|
| `OPENAI_API_KEY` | MiniMax API Key（已有） |
| `OPENAI_BASE_URL` | `https://api.minimax.chat/v1`（已有） |
| `OPENAI_MODEL` | `MiniMax-M2.7`（复用作为 Vision 模型） |

### 2.2 API 调用格式

```python
response = await client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64}"}}
        ]
    }]
)
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

| type | 说明 |
|------|------|
| driving | `{"carNo": "京A12345", "brand": "宝马", "model": "X5", "regDate": "2020-01-01"}` |
| driver | `{"name": "张三"}` |

**错误响应：**

| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误（无效的 type） |
| 500 | MiniMax API 调用失败 |

### 3.3 Prompt 设计

| type | Prompt |
|------|--------|
| driving | "请从这张行驶证图片中提取信息，返回JSON格式：车牌号(carNo)、车辆品牌(brand)、车辆型号(model)、注册日期(regDate)。只返回JSON，不要其他文字。" |
| driver | "请从这张驾驶证图片中提取信息，返回JSON格式：姓名(name)。只返回JSON，不要其他文字。" |

## 4. 实现步骤

### Step 1: 修改 `yail/www/handlers/car/index.py`

**新增依赖：**
```python
from openai import AsyncOpenAI
import re
import json
```

**新增函数：**
```python
_vision_client = None

def get_vision_client():
    global _vision_client
    if _vision_client is None:
        _vision_client = AsyncOpenAI(
            api_key=conf.OPENAI_API_KEY,
            base_url=conf.OPENAI_BASE_URL,
        )
    return _vision_client

async def call_vision(image_base64: str, prompt: str) -> str:
    """调用 MiniMax Vision API"""
    client = get_vision_client()
    response = await client.chat.completions.create(
        model=conf.OPENAI_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }]
    )
    return response.choices[0].message.content
```

**新增端点：**
```python
@post("/car/ocr")
@ResponseBody
async def ocr(image: str, type: str):
    """OCR 识别接口"""
    prompts = {
        "driving": "请从这张行驶证图片中提取信息，返回JSON格式：车牌号(carNo)、车辆品牌(brand)、车辆型号(model)、注册日期(regDate)。只返回JSON，不要其他文字。",
        "driver": "请从这张驾驶证图片中提取信息，返回JSON格式：姓名(name)。只返回JSON，不要其他文字。"
    }
    
    if type not in prompts:
        raise aiohttp.HTTPError(400, "Invalid type")
    
    content = await call_vision(image, prompts[type])
    
    # 解析 JSON 返回
    json_str = re.sub(r'```json\n?|```\n?', '', content).strip()
    return json.loads(json_str)
```

### Step 2: 修改 `frontEnd/src/components/Container/car/Step1Upload.vue`

**修改 `ocrImage` 方法：**
```javascript
async ocrImage(base64, type) {
  const response = await this.$http.post('/car/ocr', {
    image: base64,
    type
  });
  return response.data;
}
```

**移除：**
- `API_URL` 常量
- MiniMax API headers
- 直接 fetch 调用
- `ocrApiKey` prop

## 5. 文件变更清单

| 文件 | 操作 |
|------|------|
| `yail/www/handlers/car/index.py` | 新增 Vision 客户端、OCR 函数、/car/ocr 端点 |
| `frontEnd/src/components/Container/car/Step1Upload.vue` | 简化 ocrImage 调用后端接口 |

## 6. 测试用例

| 用例 | 输入 | 预期输出 |
|------|------|----------|
| 行驶证识别 | 行驶证 base64, type="driving" | `{"carNo": "...", "brand": "...", "model": "...", "regDate": "..."}` |
| 驾驶证识别 | 驾驶证 base64, type="driver" | `{"name": "..."}` |
| 无效 type | 任意 base64, type="invalid" | 400 错误 |
| API 失败 | 无效 base64 | 500 错误 |