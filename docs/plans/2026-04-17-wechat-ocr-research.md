# 微信本地 OCR 行驶证识别可行性研究报告

## 研究背景

基于 swigger/wechat-ocr 和 QQImpl 项目，研究在 Windows 环境下使用微信本地 OCR 识别行驶证的可行性。

## 已知信息

| 项目 | 值 |
|------|-----|
| **微信版本** | 4.1.7.59 |
| **微信路径** | `C:\Program Files (x86)\Tencent\Weixin\4.1.7.59` |
| **OCR 文件** | `WeChatOcr.bin` (49 MB) |
| **通信库** | `mmmojo_64.dll` (2.4 MB) |

## 关键发现

### WeChatOcr.bin 分析

```
文件头: 504b0304 (PKZIP 签名)
大小: 51,742,491 bytes (~49 MB)
结论: ZIP 压缩包，不是可执行文件
```

### 目录文件列表

| 文件 | 大小 | 说明 |
|------|------|------|
| WeChatOcr.bin | 49 MB | OCR 模型/数据 |
| WeChatPlayer.bin | 53 MB | 播放器模块 |
| WeChatUtility.bin | 27 MB | 工具模块 |
| **mmmojo_64.dll** | 2.4 MB | **Mojo IPC 通信库** |
| ConfSdk.dll | 1.1 MB | 配置 SDK |
| owl.dll | 1.3 MB | 未知组件 |
| ... | ... | ... |

### 微信 OCR 架构（基于 QQImpl）

```
微信主程序
    ↓ Mojo IPC
mmmojo_64.dll (MMMojo - Google Mojo IPC 封装)
    ↓ protobuf 通信
WeChatOcr.bin (OCR 引擎)
```

**通信机制：**
- 微信通过 `mmmojo_64.dll` 启动组件并通信
- 通信格式：`request_id + protobuf data + MMMojoInfoMethod`
- 使用 Google Mojo IPC 机制

## 现有方案对比

| 方案 | 项目 | 支持的 OCR 格式 | 状态 |
|------|------|-----------------|------|
| **A** | kanadeblisst00/wechat_ocr | WeChatOCR.exe | ❌ 需要旧版路径 |
| **B** | swigger/wechat-ocr | WeChatOCR.exe / wxocr.dll | ❓ 4.1.7.59 未测试 |
| **C** | 直接调用 WeChatOcr.bin | 需要逆向 | ❌ 复杂度高 |

## 方案 B: 尝试 swigger/wechat-ocr

swigger/wechat-ocr 的 Python 绑定期望：
1. `WeChatOCR.exe` 或 `wxocr.dll` 作为 OCR 引擎
2. 微信安装目录作为运行时路径

### 可能的问题

你的微信 4.1.7.59 使用的是 `WeChatOcr.bin`，而不是 `WeChatOCR.exe`。

**版本对应关系（推测）：**
- 微信 3.x: `WeChatOCR.exe`
- 微信 4.0: `wxocr.dll`
- 微信 4.1.x: `WeChatOcr.bin` (新格式)

### 需要测试

1. 下载 swigger/wechat-ocr 的预编译 wcocr.dll
2. 尝试用 wcocr.dll 配合你的微信 4.1.7.59

## 下一步行动

### 方案 1: 尝试 swigger/wechat-ocr (推荐)

```bash
# 1. 下载 swigger/wechat-ocr release
# https://github.com/swigger/wechat-ocr/releases

# 2. 尝试使用 wcocr.dll
```

### 方案 2: 修改 kanadeblisst00/wechat_ocr

```python
# 该项目是纯 Python 实现
# 可能需要修改以支持 WeChatOcr.bin

# 关键代码位置:
# wechat_ocr/ocr/_manager.py
```

### 方案 3: 从 WeChatOcr.bin 解压

```bash
# WeChatOcr.bin 是 ZIP 文件
# 可以尝试解压查看内容
unzip WeChatOcr.bin -d WeChatOcr_extracted/
```

## 风险评估

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| WeChat 4.1.x 不兼容 | 高 | 高 | 等待项目更新或自行适配 |
| 需要编译 C++ 代码 | 中 | 中 | 使用预编译版本 |
| 接口变化 | 高 | 高 | 逆向分析新格式 |

## 结论

**当前状态：** 可行性待验证

**原因：**
1. WeChatOcr.bin 是 ZIP 格式，不是直接可执行文件
2. 需要通过 mmmojo_64.dll 进行 IPC 通信
3. 现有开源项目可能不支持微信 4.1.x 版本

**建议：**
1. 先尝试下载 swigger/wechat-ocr 预编译版本测试
2. 如果失败，需要自行适配或等待项目更新

## 参考资料

- [EEEEhex/QQImpl](https://github.com/EEEEhex/QQImpl) - 逆向 QQNT Mojo IPC
- [swigger/wechat-ocr](https://github.com/swigger/wechat-ocr) - 微信 OCR 调用
- [kanadeblisst00/wechat_ocr](https://github.com/kanadeblisst00/wechat_ocr) - 纯 Python 实现
