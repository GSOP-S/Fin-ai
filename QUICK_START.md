# ⚡ Railway + Vercel 快速部署指南

## 📋 前置准备

- ✅ GitHub 账号
- ✅ Railway 账号（用 GitHub 登录）
- ✅ Vercel 账号（用 GitHub 登录）

---

## 🚀 5 步完成部署

### 步骤 1：创建 Railway MySQL 数据库（2 分钟）

1. 访问 https://railway.app/
2. 登录 → **New Project** → **Provision MySQL**
3. 点击 MySQL 服务 → **Variables** 标签页
4. 复制以下信息（待会要用）：
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

---

### 步骤 2：配置本地环境（3 分钟）

#### 方法 A：使用配置助手（推荐）

```bash
python setup_railway.py
```

按提示输入 Railway 的连接信息即可。

#### 方法 B：手动创建

复制 `.env.example` 为 `.env`，填入 Railway 连接信息：

```env
MYSQL_HOST=你的Railway主机地址
MYSQL_USER=root
MYSQL_PASSWORD=你的Railway密码
MYSQL_DATABASE=railway
MYSQL_PORT=你的Railway端口
```

---

### 步骤 3：初始化数据库（1 分钟）

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py
```

看到 ✅ 表示成功！

---

### 步骤 4：本地测试（1 分钟）

```bash
# 启动后端
python app.py

# 新终端启动前端
npm install
npm run dev
```

访问 http://localhost:3000 测试登录：
- 用户名：`UTSZ`
- 密码：`admin`

---

### 步骤 5：部署到 Vercel（5 分钟）

#### 5.1 推送代码

```bash
git add .
git commit -m "config: setup Railway MySQL"
git push origin main
```

#### 5.2 连接 Vercel

1. 访问 https://vercel.com/
2. **New Project** → 选择你的 GitHub 仓库
3. 点击 **Import**

#### 5.3 配置环境变量

在 Vercel 项目设置中添加（**Settings** → **Environment Variables**）：

```
SECRET_KEY=【从本地.env复制】
FLASK_ENV=production
MYSQL_HOST=【Railway的MYSQLHOST】
MYSQL_USER=【Railway的MYSQLUSER】
MYSQL_PASSWORD=【Railway的MYSQLPASSWORD】
MYSQL_DATABASE=railway
MYSQL_PORT=【Railway的MYSQLPORT】
VITE_API_BASE_URL=/api
```

**可选**（如果使用 AI 功能）：
```
OPENAI_API_KEY=你的OpenAI密钥
```

#### 5.4 部署

点击 **Deploy** 按钮，等待 2-5 分钟。

---

## ✅ 验证部署

### 检查后端

访问：`https://你的域名.vercel.app/api/health`

应该返回：
```json
{
  "status": "ok",
  "version": "2.1.0",
  "platform": "Vercel Serverless"
}
```

### 检查前端

访问：`https://你的域名.vercel.app`

应该看到登录页面。

---

## 🎯 完成！

现在你的应用已经部署到云端，可以分享给任何人使用了！

**访问地址**：`https://你的项目名.vercel.app`

---

## 📊 管理你的应用

### Railway 控制台
- **Data**：查看数据库表和数据
- **Metrics**：监控数据库性能
- **Query**：执行 SQL 查询
- **Backups**：备份数据库

### Vercel 控制台
- **Deployments**：查看部署历史
- **Functions**：查看 API 日志
- **Analytics**：查看访问统计
- **Domains**：配置自定义域名

---

## 🔧 常见问题

### 部署失败？

1. 检查 Vercel 环境变量是否都配置了
2. 查看 Deployment Logs 中的错误信息
3. 确认 Railway 数据库可以访问

### API 返回 500 错误？

1. 检查数据库连接信息是否正确
2. 在 Railway 控制台确认数据库正常运行
3. 查看 Vercel Functions 日志

### 前端无法访问后端？

1. 确认 `VITE_API_BASE_URL=/api` 已设置
2. 检查浏览器控制台是否有 CORS 错误
3. 重新部署 Vercel

---

## 💡 下一步

- 📱 配置自定义域名
- 🔐 添加更多用户和数据
- 📊 监控应用性能
- 🚀 持续开发新功能

**详细文档**：
- Railway 配置：`RAILWAY_MYSQL_SETUP.md`
- Vercel 部署：`VERCEL_DEPLOYMENT_GUIDE.md`

---

需要帮助？查看详细文档或提交 Issue！🎉

