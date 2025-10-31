# 📦 Fin-AI Vercel 部署指南

本指南将帮助你将 Fin-AI 项目部署到 Vercel 平台。

## 🚀 部署前准备

### 1. 准备云数据库

Vercel 是无服务器平台，不支持本地 MySQL。你需要准备一个云数据库：

**推荐选择：**
- **PlanetScale** - MySQL 兼容，免费套餐（推荐）
- **Railway** - 支持 MySQL，有免费额度
- **Supabase** - PostgreSQL（需要修改代码适配）
- **阿里云 RDS** / **腾讯云数据库** - 适合中国用户

### 2. 获取数据库连接信息

从云数据库提供商获取以下信息：
```
MYSQL_HOST=your-db-host.com
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=Fin
MYSQL_PORT=3306
```

### 3. 准备 OpenAI API Key

如果使用 AI 功能，需要准备：
- OpenAI API Key：https://platform.openai.com/api-keys

---

## 📝 部署步骤

### 步骤 1：推送代码到 GitHub

```bash
# 如果还没有初始化 git 仓库
git init
git add .
git commit -m "feat: 适配 Vercel 部署"

# 推送到 GitHub
git remote add origin <你的GitHub仓库地址>
git branch -M main
git push -u origin main
```

### 步骤 2：连接 Vercel

1. 访问 [Vercel](https://vercel.com/)
2. 使用 GitHub 账号登录
3. 点击 **"New Project"**
4. 选择你的 GitHub 仓库 `Fin-ai`
5. 点击 **"Import"**

### 步骤 3：配置构建设置

Vercel 会自动检测配置，确认以下设置：

```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 步骤 4：配置环境变量

在 Vercel 项目设置中添加环境变量：

**必需的环境变量：**

```bash
# Flask 配置
SECRET_KEY=你的密钥（建议生成随机字符串）
FLASK_ENV=production

# 数据库配置（使用你的云数据库信息）
MYSQL_HOST=your-database-host.com
MYSQL_USER=your-database-user
MYSQL_PASSWORD=your-database-password
MYSQL_DATABASE=Fin
MYSQL_PORT=3306

# OpenAI API（如果使用 AI 功能）
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# 前端 API URL（Vercel 会自动设置，但也可以手动指定）
VITE_API_BASE_URL=/api
```

**如何添加环境变量：**
1. 进入项目设置（Settings）
2. 选择 **Environment Variables**
3. 逐个添加上述变量
4. 选择环境：Production, Preview, Development（全选）

### 步骤 5：部署

1. 点击 **"Deploy"** 按钮
2. 等待构建完成（通常 2-5 分钟）
3. 部署成功后会获得一个 URL，如：`https://fin-ai.vercel.app`

---

## ✅ 验证部署

### 1. 检查 API 是否正常

访问：`https://your-domain.vercel.app/api/health`

应该返回：
```json
{
  "status": "ok",
  "version": "2.1.0",
  "environment": "production",
  "platform": "Vercel Serverless"
}
```

### 2. 检查前端是否正常

访问：`https://your-domain.vercel.app`

应该能看到登录页面。

### 3. 测试数据库连接

尝试登录或访问需要数据库的功能，确认数据库连接正常。

---

## 🔧 常见问题

### Q1: 部署后 API 请求失败 (CORS 错误)

**解决方案：**
- 检查 `api/index.py` 中的 CORS 配置是否正确
- 确认环境变量中没有设置限制性的 `ALLOWED_ORIGINS`

### Q2: 数据库连接超时

**解决方案：**
- 确认云数据库允许 Vercel 的 IP 访问（通常需要允许所有 IP）
- 检查数据库连接信息是否正确
- 确认数据库服务是否正常运行

### Q3: OpenAI API 调用失败

**解决方案：**
- 检查 `OPENAI_API_KEY` 环境变量是否正确设置
- 确认 API Key 有足够的额度
- 检查 OpenAI 服务状态

### Q4: 构建失败

**解决方案：**
- 检查 `package.json` 和 `requirements.txt` 依赖是否正确
- 查看构建日志中的具体错误信息
- 确认 Node.js 和 Python 版本兼容

### Q5: 前端能访问但后端 404

**解决方案：**
- 检查 `vercel.json` 路由配置
- 确认 `api/index.py` 文件存在
- 查看 Vercel 函数日志

---

## 📊 监控和日志

### 查看日志

1. 进入 Vercel 项目控制台
2. 选择 **"Deployments"** 标签
3. 点击最新的部署
4. 查看 **"Functions"** 日志

### 性能监控

Vercel 提供内置的性能监控：
- **Analytics** - 访问统计
- **Speed Insights** - 页面加载性能
- **Functions** - 函数执行时间和错误

---

## 🔄 更新部署

### 自动部署

推送到 GitHub 会自动触发部署：
```bash
git add .
git commit -m "update: 更新功能"
git push
```

### 手动部署

在 Vercel 控制台点击 **"Redeploy"**。

---

## 🌍 自定义域名（可选）

### 添加自定义域名

1. 进入项目设置
2. 选择 **"Domains"**
3. 添加你的域名
4. 按照提示配置 DNS 记录

### DNS 配置示例

```
Type: A
Name: @
Value: 76.76.19.19

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

---

## 💡 最佳实践

### 1. 环境分离

- 使用 Vercel 的 Preview 环境进行测试
- Production 环境使用独立的数据库

### 2. 安全性

- 定期更新 `SECRET_KEY`
- 不要在代码中硬编码敏感信息
- 使用环境变量管理所有配置

### 3. 性能优化

- 启用 Vercel Edge Network
- 优化数据库查询
- 使用 Redis 缓存（如需要）

### 4. 成本控制

- 监控 Vercel 函数执行时间
- 优化冷启动时间
- 考虑使用免费的数据库服务

---

## 📞 获取帮助

- **Vercel 文档**: https://vercel.com/docs
- **PlanetScale 文档**: https://planetscale.com/docs
- **项目 Issues**: 在 GitHub 仓库提交 Issue

---

## 🎉 完成！

恭喜！你已经成功将 Fin-AI 部署到 Vercel。

现在你可以：
- ✅ 分享你的应用链接给用户
- ✅ 配置自定义域名
- ✅ 监控应用性能和错误
- ✅ 持续更新和改进

祝使用愉快！ 🚀

