# 📱 **微信OCR全面介绍与Python调用方案**

微信OCR主要分为两种形式：**微信开放平台云端OCR API**和**微信客户端本地OCR引擎**。下面为您详细介绍这两种方案。

## 🔍 **微信OCR功能概览**

### **1. 云端OCR API（微信开放平台）**
这是微信官方提供的云端OCR服务，需要通过API调用，支持多种证件和文档类型。

### **2. 本地OCR引擎（微信客户端内置）**
微信客户端自带OCR功能，通过本地引擎实现，无需网络即可识别。

## ☁️ **方案一：微信开放平台云端OCR API**

### **支持的功能类型**
根据微信开放文档，云端OCR API支持以下识别类型：
- **通用印刷体识别** (`/cv/ocr/comm`) - 通用印刷体
- **行驶证识别** (`/cv/ocr/driving`) - 机动车行驶证
- **银行卡识别** (`/cv/ocr/bankcard`) - 银行卡卡面信息
- **营业执照识别** (`/cv/ocr/bizlicense`) - 营业执照
- **驾驶证识别** (`/cv/ocr/drivinglicense`) - 驾驶证
- **身份证识别** (`/cv/ocr/idcard`) - 身份证正反面
- **车牌识别** - 车辆号牌

### **免费额度**
- 每天免费使用**100次**
- 文件大小限制：小于2MB

### **Python调用方案**

#### **步骤1：获取Access Token**
```python
import requests
import json

def get_wechat_access_token(appid, secret):
    """
    获取微信Access Token
    有效期：2小时
    """
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    
    response = requests.get(url, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        if 'access_token' in result:
            return result['access_token']
        else:
            raise Exception(f"获取token失败: {result}")
    else:
        raise Exception(f"请求失败: {response.status_code}")

# 使用示例
appid = "你的AppID"
secret = "你的AppSecret"
access_token = get_wechat_access_token(appid, secret)
print(f"Access Token: {access_token}")
```

#### **步骤2：调用通用OCR接口**
```python
def wechat_ocr_comm(image_path, access_token):
    """
    调用微信通用OCR接口
    """
    ocr_url = f"https://api.weixin.qq.com/cv/ocr/comm?access_token={access_token}"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        headers = {'Content-Type': 'multipart/form-data'}
        
        response = requests.post(ocr_url, files=files, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OCR识别失败: {response.status_code}")

# 使用示例
result = wechat_ocr_comm("document.jpg", access_token)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

#### **步骤3：调用专用证件识别接口**
```python
def wechat_ocr_special(image_path, access_token, ocr_type):
    """
    调用微信专用OCR接口
    ocr_type: 
        1: 身份证
        2: 银行卡  
        3: 行驶证
        4: 驾驶证
        7: 营业执照
        8: 通用OCR
        10: 车牌识别
    """
    # 根据类型选择接口
    ocr_apis = {
        1: "idcard",
        2: "bankcard", 
        3: "driving",
        4: "drivinglicense",
        7: "bizlicense",
        8: "comm",
        10: "plate"
    }
    
    if ocr_type not in ocr_apis:
        raise ValueError("不支持的OCR类型")
    
    api_name = ocr_apis[ocr_type]
    ocr_url = f"https://api.weixin.qq.com/cv/ocr/{api_name}?access_token={access_token}"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(ocr_url, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"识别失败: {response.status_code}")

# 使用示例：识别行驶证
result = wechat_ocr_special("driving_license.jpg", access_token, ocr_type=3)
```

#### **步骤4：完整封装类**
```python
import base64
from typing import Optional, Dict, Any

class WeChatOCRClient:
    """微信OCR客户端封装类"""
    
    def __init__(self, appid: str, secret: str):
        self.appid = appid
        self.secret = secret
        self.access_token = None
        self.token_expire_time = None
    
    def get_token(self) -> str:
        """获取或刷新Access Token"""
        import time
        
        if self.access_token and self.token_expire_time and time.time() < self.token_expire_time:
            return self.access_token
        
        token = get_wechat_access_token(self.appid, self.secret)
        self.access_token = token
        self.token_expire_time = time.time() + 7200  # 2小时有效期
        
        return token
    
    def recognize(self, image_path: str, ocr_type: int = 8) -> Dict[str, Any]:
        """识别图像"""
        token = self.get_token()
        
        # 构建请求数据
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 使用data_type=2表示base64字符串
        payload = {
            "img_url": "",  # 留空，使用img_data
            "img_data": image_data,
            "data_type": 2,
            "ocr_type": ocr_type,
            "client_msg_id": f"req_{int(time.time())}"  # 随机ID
        }
        
        # 根据类型选择接口
        ocr_apis = {
            1: "idcard",
            2: "bankcard",
            3: "driving",
            4: "drivinglicense",
            7: "bizlicense",
            8: "comm",
            10: "plate"
        }
        
        api_name = ocr_apis.get(ocr_type, "comm")
        url = f"https://api.weixin.qq.com/cv/ocr/{api_name}?access_token={token}"
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"识别失败: {response.text}")
    
    def batch_recognize(self, image_paths: list, ocr_type: int = 8) -> list:
        """批量识别"""
        results = []
        for path in image_paths:
            try:
                result = self.recognize(path, ocr_type)
                results.append({
                    "file": path,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "file": path,
                    "success": False,
                    "error": str(e)
                })
        return results

# 使用示例
client = WeChatOCRClient(appid="your_appid", secret="your_secret")

# 识别通用文本
result = client.recognize("document.jpg", ocr_type=8)

# 识别身份证
id_card_result = client.recognize("id_card.jpg", ocr_type=1)

# 批量识别
batch_results = client.batch_recognize(["doc1.jpg", "doc2.jpg", "doc3.jpg"])
```

## 💻 **方案二：微信客户端本地OCR引擎**

### **原理介绍**
微信客户端内置了OCR引擎，可以通过Python调用其本地接口实现识别。这种方式**无需网络连接**，直接在本地运行。

### **环境要求**
- **操作系统**：Windows（目前主要支持）
- **微信版本**：已安装最新版微信
- **Python环境**：推荐最新版本

### **安装与配置**

#### **1. 安装Python库**
```bash
pip install wechat-ocr
```

#### **2. 查找微信OCR路径**
需要找到两个关键路径：
1. **微信安装目录**：如 `C:\Program Files\Tencent\WeChat\[3.9.12.17]`
2. **OCR引擎路径**：如 `C:\Users\用户名\AppData\Roaming\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe`

#### **3. Python调用示例**
```python
import os
import json
from wechat_ocr import WeChatOCR

class LocalWeChatOCR:
    """本地微信OCR调用类"""
    
    def __init__(self, wechat_dir=None, ocr_exe_path=None):
        """
        初始化
        wechat_dir: 微信安装目录
        ocr_exe_path: OCR引擎可执行文件路径
        """
        self.wechat_dir = wechat_dir or self._find_wechat_dir()
        self.ocr_exe_path = ocr_exe_path or self._find_ocr_exe()
        
        if not os.path.exists(self.ocr_exe_path):
            raise FileNotFoundError(f"未找到OCR引擎: {self.ocr_exe_path}")
        
        # 初始化OCR管理器
        self.ocr_manager = WeChatOCR(
            wechat_dir=self.wechat_dir,
            ocr_exe_path=self.ocr_exe_path
        )
    
    def _find_wechat_dir(self):
        """自动查找微信安装目录"""
        common_paths = [
            r"C:\Program Files\Tencent\WeChat",
            r"C:\Program Files (x86)\Tencent\WeChat",
            os.path.expanduser(r"~\AppData\Local\Programs\Tencent\WeChat")
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                # 查找版本号目录
                for item in os.listdir(path):
                    if item.startswith("[") and item.endswith("]"):
                        return os.path.join(path, item)
        
        raise FileNotFoundError("未找到微信安装目录")
    
    def _find_ocr_exe(self):
        """自动查找OCR引擎"""
        base_path = os.path.expanduser(r"~\AppData\Roaming\Tencent\WeChat\XPlugin\Plugins\WeChatOCR")
        
        if os.path.exists(base_path):
            # 查找最新版本
            versions = []
            for item in os.listdir(base_path):
                if item.isdigit():
                    exe_path = os.path.join(base_path, item, "extracted", "WeChatOCR.exe")
                    if os.path.exists(exe_path):
                        versions.append((int(item), exe_path))
            
            if versions:
                # 使用版本号最大的
                versions.sort(reverse=True)
                return versions[0][1]
        
        raise FileNotFoundError("未找到OCR引擎")
    
    def recognize(self, image_path, output_json=True):
        """
        识别图像
        image_path: 图像文件路径
        output_json: 是否输出JSON文件
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        # 调用OCR识别
        result = self.ocr_manager.recognize(image_path)
        
        # 如果需要，保存JSON文件
        if output_json:
            json_path = os.path.splitext(image_path)[0] + ".json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {json_path}")
        
        return result
    
    def recognize_text(self, image_path):
        """仅提取文本内容"""
        result = self.recognize(image_path, output_json=False)
        
        # 提取所有文本
        texts = []
        if 'items' in result:
            for item in result['items']:
                if 'text' in item:
                    texts.append(item['text'])
        
        return "\n".join(texts)
    
    def recognize_with_location(self, image_path):
        """识别文本及位置信息"""
        result = self.recognize(image_path, output_json=False)
        
        formatted_result = []
        if 'items' in result:
            for item in result['items']:
                if 'text' in item and 'location' in item:
                    formatted_result.append({
                        'text': item['text'],
                        'confidence': item.get('confidence', 0),
                        'location': item['location']
                    })
        
        return formatted_result

# 使用示例
def main():
    # 方法1：自动查找路径
    ocr = LocalWeChatOCR()
    
    # 方法2：手动指定路径
    # wechat_dir = r"C:\Program Files\Tencent\WeChat\[3.9.12.17]"
    # ocr_exe_path = r"C:\Users\用户名\AppData\Roaming\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe"
    # ocr = LocalWeChatOCR(wechat_dir, ocr_exe_path)
    
    # 识别图像
    image_path = "test_document.jpg"
    
    # 获取完整结果（包含位置信息）
    full_result = ocr.recognize(image_path)
    print("完整识别结果:", json.dumps(full_result, indent=2, ensure_ascii=False))
    
    # 仅获取文本
    text_only = ocr.recognize_text(image_path)
    print("提取的文本:\n", text_only)
    
    # 获取带位置信息的结果
    with_location = ocr.recognize_with_location(image_path)
    for item in with_location:
        print(f"文本: {item['text']}, 置信度: {item['confidence']:.2f}")

if __name__ == "__main__":
    main()
```

#### **4. 高级功能：表格识别与转换**
```python
def parse_table_from_ocr(ocr_result):
    """
    从OCR结果解析表格结构
    微信OCR返回的数据包含cells数组，每个单元格包含：
    - location: 坐标信息
    - words: 识别文本
    - confidence: 置信度
    """
    if 'cells' not in ocr_result:
        return []
    
    # 按行排序单元格（根据top坐标）
    cells = sorted(ocr_result['cells'], key=lambda x: x['location']['top'])
    
    rows = []
    current_row = []
    prev_top = None
    
    for cell in cells:
        top = cell['location']['top']
        
        if prev_top is None or abs(top - prev_top) < 10:
            # 同一行
            current_row.append(cell['words'])
        else:
            # 新行
            if current_row:
                rows.append(current_row)
            current_row = [cell['words']]
        
        prev_top = top
    
    # 添加最后一行
    if current_row:
        rows.append(current_row)
    
    return rows

def table_to_excel(ocr_result, output_path):
    """将OCR表格结果转换为Excel"""
    from openpyxl import Workbook
    
    table_data = parse_table_from_ocr(ocr_result)
    
    wb = Workbook()
    ws = wb.active
    
    for row_idx, row_data in enumerate(table_data, start=1):
        for col_idx, cell_value in enumerate(row_data, start=1):
            ws.cell(row=row_idx, column=col_idx, value=cell_value)
    
    wb.save(output_path)
    print(f"Excel文件已保存: {output_path}")
    
    return output_path

# 使用示例
ocr = LocalWeChatOCR()
result = ocr.recognize("table_image.jpg", output_json=False)
excel_file = table_to_excel(result, "output_table.xlsx")
```

## 📊 **两种方案对比**

| **对比维度** | **云端OCR API** | **本地OCR引擎** |
|------------|---------------|---------------|
| **网络要求** | 必须联网 | 无需网络 |
| **速度** | 依赖网络速度 | 本地处理，速度快 |
| **免费额度** | 每天100次免费 | 无限制免费 |
| **功能范围** | 支持多种证件类型 | 通用文本识别为主 |
| **部署复杂度** | 简单（API调用） | 中等（需安装微信） |
| **平台支持** | 跨平台 | 主要支持Windows |
| **数据安全** | 数据上传云端 | 数据本地处理 |
| **更新维护** | 微信官方维护 | 依赖微信客户端更新 |

## 💡 **选择建议**

### **推荐使用云端OCR API的场景**
1. **需要识别特定证件**（身份证、行驶证、银行卡等）
2. **跨平台应用**（Linux、macOS、移动端）
3. **对数据安全要求不高**的公开信息识别
4. **日调用量≤100次**的免费用户

### **推荐使用本地OCR引擎的场景**
1. **对数据隐私要求高**（敏感文档）
2. **网络环境不稳定或无法联网**
3. **需要高频次、大批量识别**
4. **Windows桌面应用集成**
5. **实时性要求高**的应用

## ⚠️ **注意事项**

### **云端API注意事项**
1. **Access Token有效期2小时**，需要定期刷新
2. **文件大小限制2MB**，大文件需要压缩
3. **每日免费额度100次**，超出可能收费
4. **需要微信公众号/小程序资质**才能获取AppID和Secret

### **本地引擎注意事项**
1. **依赖微信客户端**，必须安装微信
2. **主要支持Windows**，其他平台支持有限
3. **OCR引擎路径可能变化**，需要动态查找
4. **功能相对基础**，不如云端API丰富

## 🔧 **故障排除**

### **云端API常见问题**
```python
# 1. Token获取失败
# 检查AppID和Secret是否正确
# 检查网络连接

# 2. 识别失败
# 检查文件大小是否超过2MB
# 检查图像格式是否支持（JPG、PNG等）
# 检查access_token是否过期
```

### **本地引擎常见问题**
```python
# 1. 找不到OCR引擎
# 检查微信是否已安装并更新到最新版
# 手动指定OCR引擎路径

# 2. 识别结果为空
# 检查图像质量（清晰度、对比度）
# 尝试调整图像预处理（二值化、去噪等）
```

## 📚 **学习资源**

1. **微信开放文档**：https://developers.weixin.qq.com/doc/offiaccount/Intelligent_Interface/OCR.html
2. **腾讯云服务市场**：https://fuwu.weixin.qq.com/service/detail/000ce4cec24ca026d37900ed551415
3. **GitHub项目**：搜索 `wechat-ocr` 获取最新Python库

**总结**：微信OCR提供了云端和本地两种解决方案，各有优劣。云端API功能丰富、跨平台，适合证件识别和轻量应用；本地引擎隐私性好、无网络要求，适合高频次、敏感数据的Windows应用。根据您的具体需求选择合适的方案即可。