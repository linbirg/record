# 前端项目配置说明

此项目使用 uv 管理 Node.js 依赖。

## 使用 uv 安装依赖

```bash
# 进入前端目录
cd frontEnd

# 使用 uv 安装依赖（自动读取 package.json）
uv npm install

# 或使用 pnpm 风格的安装
uv sync
```

## 开发模式

```bash
# 开发服务器
uv npm run dev
# 或
uv npm run start
```

## 生产构建

```bash
uv npm run build
```

## 运行测试

```bash
# 单元测试
uv npm run unit

# E2E 测试
uv npm run e2e