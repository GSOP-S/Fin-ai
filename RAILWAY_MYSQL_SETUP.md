# 🚂 Railway MySQL 配置指南

## 第一步：注册并创建 Railway MySQL 数据库

### 1. 注册 Railway 账号

1. 访问：https://railway.app/
2. 点击 **"Start a New Project"** 或 **"Login"**
3. 选择 **"Login with GitHub"**（推荐）
4. 授权 GitHub 访问

### 2. 创建 MySQL 数据库

1. 登录后，点击 **"New Project"**
2. 选择 **"Provision MySQL"**
3. 等待几秒，MySQL 实例创建完成 ✅

### 3. 获取数据库连接信息

点击创建好的 MySQL 服务，在 **"Variables"** 或 **"Connect"** 标签页找到：

```
MYSQLHOST=containers-us-west-xxx.railway.app
MYSQLPORT=6543
MYSQLUSER=root
MYSQLPASSWORD=xxxxxxxxxxxxxxxxx
MYSQLDATABASE=railway
```

---

## 第二步：配置本地环境变量

### 方法 1：手动创建 .env 文件

在项目根目录创建 `.env` 文件（如果已存在则修改）：

```env
# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# Railway MySQL 数据库配置
MYSQL_HOST=containers-us-west-xxx.railway.app
MYSQL_USER=root
MYSQL_PASSWORD=你从Railway获取的密码
MYSQL_DATABASE=railway
MYSQL_PORT=6543

# OpenAI API 配置（可选）
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4-turbo-preview

# 前端配置
VITE_API_BASE_URL=http://localhost:5000
```

⚠️ **重要**：
- 将 Railway 提供的值填入对应位置
- `MYSQL_DATABASE` 默认是 `railway`（不是 `Fin`）
- 保存文件

---

## 第三步：初始化数据库

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 修改初始化脚本（临时）

因为 Railway 默认数据库名是 `railway`，需要临时修改 `init_db.py`：

**找到第 26 行**：
```python
# 原来的
cursor.execute('CREATE DATABASE IF NOT EXISTS Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
cursor.execute('USE Fin')
```

**改为**：
```python
# 使用 Railway 的默认数据库
cursor.execute('USE railway')
# 如果想创建 Fin 数据库，可以先创建再使用
# cursor.execute('CREATE DATABASE IF NOT EXISTS Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
# cursor.execute('USE Fin')
```

### 3. 运行初始化脚本

```bash
python init_db.py
```

**预期输出**：
```
创建Bills表...
✓ Bills表创建成功
创建TransferHistory表...
✓ TransferHistory表创建成功
插入示例账单数据...
✓ 示例账单数据插入完成
...
✅ 数据库初始化完成！
```

### 4. 验证数据库

可以回到 Railway 控制台：
- 点击 MySQL 服务
- 选择 **"Data"** 标签页
- 查看创建的表和数据

---

## 第四步：配置 Vercel 环境变量

### 1. 进入 Vercel 项目设置

1. 登录 Vercel：https://vercel.com/
2. 选择你的项目
3. 进入 **Settings** → **Environment Variables**

### 2. 添加以下环境变量

**逐个添加**（点击 "Add" 按钮）：

| Key | Value | Environment |
|-----|-------|-------------|
| `SECRET_KEY` | 你生成的密钥 | Production, Preview, Development |
| `FLASK_ENV` | `production` | Production, Preview |
| `MYSQL_HOST` | Railway 的 `MYSQLHOST` | Production, Preview, Development |
| `MYSQL_USER` | Railway 的 `MYSQLUSER` | Production, Preview, Development |
| `MYSQL_PASSWORD` | Railway 的 `MYSQLPASSWORD` | Production, Preview, Development |
| `MYSQL_DATABASE` | `railway` | Production, Preview, Development |
| `MYSQL_PORT` | Railway 的 `MYSQLPORT` | Production, Preview, Development |
| `OPENAI_API_KEY` | 你的 OpenAI Key（可选） | Production, Preview, Development |
| `VITE_API_BASE_URL` | `/api` | Production, Preview, Development |

### 3. 生成 SECRET_KEY

在本地运行：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制输出的随机字符串作为 `SECRET_KEY`。

---

## 第五步：测试本地连接

### 1. 启动后端

```bash
python app.py
```

### 2. 测试 API

访问：http://localhost:5000/health

**预期响应**：
```json
{
  "status": "ok",
  "version": "2.1.0",
  "environment": "development"
}
```

### 3. 测试数据库查询

访问：http://localhost:5000/api/bills?user_id=UTSZ

**预期响应**：返回账单数据

---

## 第六步：部署到 Vercel

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "config: configure Railway MySQL"
git push origin main
```

### 2. Vercel 自动部署

- Vercel 会自动检测到新的 commit
- 自动开始构建和部署
- 等待 2-5 分钟

### 3. 验证部署

访问：`https://你的域名.vercel.app/api/health`

**预期响应**：
```json
{
  "status": "ok",
  "version": "2.1.0",
  "environment": "production",
  "platform": "Vercel Serverless"
}
```

---

## 🔧 常见问题

### Q1: Railway 数据库连接超时

**解决方案**：
- Railway MySQL 默认允许所有 IP 访问，不需要额外配置
- 检查防火墙是否阻止了连接
- 确认 `MYSQL_HOST` 和 `MYSQL_PORT` 正确

### Q2: 本地可以连接，Vercel 无法连接

**解决方案**：
- 检查 Vercel 环境变量是否正确设置
- 确认所有环境变量的 Environment 都勾选了 Production
- 重新部署：Deployments → Redeploy

### Q3: 数据库名称问题

Railway 默认数据库名是 `railway`，你可以：

**选项 1**：直接使用 `railway`
- 修改 `.env` 中的 `MYSQL_DATABASE=railway`
- 修改 `init_db.py` 使用 `railway` 数据库

**选项 2**：创建 `Fin` 数据库
- 在 Railway 控制台的 Query 页面运行：
  ```sql
  CREATE DATABASE Fin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
- 然后在 `.env` 中使用 `MYSQL_DATABASE=Fin`

### Q4: 需要修改代码吗？

**不需要！** Railway MySQL 完全兼容你的代码：
- ✅ 支持所有 SQL 语句
- ✅ 支持外键约束
- ✅ 支持 JSON 字段
- ✅ 支持 utf8mb4 字符集

---

## 📊 Railway 免费额度

- **数据存储**：512 MB（足够小型项目）
- **带宽**：100 GB/月
- **免费额度**：$5/月
- **超出后**：按使用量付费

对于测试和小型项目完全够用！

---

## 🎯 下一步

配置完成后，你可以：
1. ✅ 在本地开发，数据存储在云端
2. ✅ 部署到 Vercel，共享给用户
3. ✅ 随时在 Railway 控制台查看数据
4. ✅ 使用 Railway 提供的数据库备份功能

---

## 💡 提示

### Railway 控制台功能

- **Variables**：查看连接信息
- **Data**：浏览数据库表和数据
- **Metrics**：查看性能指标
- **Query**：执行 SQL 查询
- **Logs**：查看数据库日志

### 安全建议

- 🔒 不要将 `.env` 文件提交到 Git
- 🔒 定期更改数据库密码
- 🔒 使用强密码作为 SECRET_KEY
- 🔒 定期备份数据库

---

## ✅ 配置检查清单

部署前确认：
- ☑️ Railway MySQL 已创建
- ☑️ 本地 `.env` 文件已配置
- ☑️ 数据库已初始化（运行 init_db.py）
- ☑️ 本地测试通过
- ☑️ Vercel 环境变量已配置
- ☑️ 代码已推送到 GitHub
- ☑️ Vercel 部署成功

完成以上步骤，你的应用就可以在云端运行了！🎉

