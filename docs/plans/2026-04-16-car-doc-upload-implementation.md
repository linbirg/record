# Car Document Upload Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现 CarList 证件弹窗内的上传功能，支持序号/预设/自定义证件名称命名

**Architecture:** 
- 前端：CarList.vue 证件弹窗内添加 el-upload + 证件名称选择器
- 后端：car/pic/upload 接口支持自定义 filename 参数

**Tech Stack:** Vue 2, element-ui, aiohttp, MySQL

---

## Task 1: 后端 - 修改 car/pic/upload 接口支持自定义文件名

**Files:**
- Modify: `yail/www/handlers/car/index.py:176-193`

**Step 1: 阅读当前接口实现**

查看 `car/pic/upload` 接口当前如何处理文件名

**Step 2: 修改接口支持 filename 参数**

```python
@post("/car/pic/upload")
async def upload(no, filename=None):
    if filename:
        name = filename
    else:
        name = formData.file.filename
    fullpath = "/".join([PIC_DIR, name])
    # ... 后续逻辑不变
```

**Step 3: 验证接口修改**

启动后端，请求上传接口测试 filename 参数是否生效

---

## Task 2: 前端 - CarList.vue 添加证件名称选择器组件

**Files:**
- Modify: `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 添加证件名称数据**

```javascript
data() {
  return {
    // 现有数据...
    docName: '证件01',
    customDocName: '',
  }
}
```

**Step 2: 添加证件名称选择方法**

```javascript
methods: {
  // 现有方法...
  
  handleUploadFile(item) {
    const file = item.file;
    const docName = this.docName === 'custom' ? this.customDocName : this.docName;
    const fileName = `${this.currentCar.name}_${this.getDateString()}_${docName}.jpg`;
    
    let formData = new FormData();
    formData.append('file', file);
    formData.append('no', this.currentCar.no);
    formData.append('filename', fileName);
    
    this.post({ url: 'car/pic/upload', data: formData })
      .then(() => {
        this.$message.success('上传成功');
        this.docName = '证件01';
        this.customDocName = '';
        this.loadDocImages(this.currentCar.no);
      })
      .catch(() => {
        this.$message.error('上传失败');
      });
  },
  
  getDateString() {
    return new Date().toISOString().slice(0, 10).replace(/-/g, '');
  },
}
```

**Step 3: 替换证件弹窗内容**

证件弹窗结构：
- 无证件时：el-upload + 证件名称选择器
- 有证件时：证件网格 + 底部添加按钮 + 证件名称选择器

**Step 4: 验证前端修改**

访问 CarList，点击证件按钮，检查弹窗是否正常显示

---

## Task 3: 前端 - 完善证件弹窗 UI

**Files:**
- Modify: `frontEnd/src/components/Container/car/CarList.vue`

**Step 1: 样式调整**

按照 webflow/DESIGN.md 规范：
- 按钮色：#146ef5
- 边框：1px solid #d8d8d8
- 圆角：4px-8px

**Step 2: 验证 UI**

- 无证件状态显示正确
- 有证件时底部添加按钮正常
- 证件名称选择器交互正常

---

## Task 4: 端到端测试

**Step 1: 测试无证件上传**

1. 选择无证件车辆
2. 点击证件按钮
3. 选择文件
4. 选择证件名称（默认证件01）
5. 上传
6. 验证文件名格式正确

**Step 2: 测试有证件追加**

1. 选择已有证件车辆
2. 点击证件按钮
3. 点击底部添加按钮
4. 选择文件
5. 选择"行驶证"
6. 上传
7. 验证图片列表增加

**Step 3: 测试自定义名称**

1. 上传时选择自定义
2. 输入自定义名称
3. 验证文件名包含自定义名称

---

## Task 5: 提交代码

```bash
git add yail/www/handlers/car/index.py frontEnd/src/components/Container/car/CarList.vue
git commit -m "feat: 实现CarList证件弹窗上传功能"
```
