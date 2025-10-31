# Vercel Serverless 部署架构文档

> **版本**: 2.1.0  
> **最后更新**: 2025-10-31  
> **作者**: Fin-AI Team  
> **状态**: Production Ready

---

## 📋 目录

- [项目概述](#项目概述)
- [架构变更](#架构变更)
- [文件结构](#文件结构)
- [核心配置](#核心配置)
- [部署流程](#部署流程)
- [环境变量](#环境变量)
- [数据库配置](#数据库配置)
- [故障排查](#故障排查)
- [维护指南](#维护指南)
- [最佳实践](#最佳实践)

---

## 项目概述

### 技术栈

**前端**:
- React 18.2.0
- Vite 4.4.5
- Ant Design 5.27.6
- React Router DOM 7.9.4

**后端**:
- Python 3.9+
- Flask 3.0.0
- PyMySQL 1.1.0
- OpenAI API 1.12.0

**基础设施**:
- **部署平台**: Vercel (Serverless)
- **数据库**: Railway MySQL 9.4.0
- **版本控制**: GitHub
- **CI/CD**: Vercel 自动部署

### 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel Platform                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌────────────────────┐       │
│  │   Frontend   │         │  Backend (Flask)   │       │
│  │  React+Vite  │ ◄─────► │  Serverless Func   │       │
│  │   (Static)   │         │  /api/index.py     │       │
│  └──────────────┘         └────────────────────┘       │
│                                     │                    │
└─────────────────────────────────────┼────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   Railway MySQL      │
                          │   Cloud Database     │
                          └──────────────────────┘
```

---

## 架构变更

### 从传统服务器到 Serverless

#### 原架构 (本地开发)
```
前端: localhost:3000 (Vite Dev Server)
    ↓
后端: localhost:5000 (Flask Development Server)
    ↓
数据库: localhost:3306 (MySQL)
```

#### 新架构 (Vercel Production)
```
用户请求 → Vercel Edge Network
    ├─→ 静态资源 → CDN
    └─→ /api/* → Serverless Function (Flask)
            ↓
        Railway MySQL (Cloud)
```

### 关键改动清单

| 类别 | 改动项 | 原因 |
|------|--------|------|
| **后端入口** | 创建 `api/index.py` | Vercel Serverless Functions 要求 |
| **路由配置** | 添加 `vercel.json` | 定义前后端路由规则 |
| **CORS** | 生产环境允许所有来源 | 支持多域名访问 |
| **数据库** | 从本地迁移到 Railway | Serverless 不支持持久化连接 |
| **依赖升级** | Flask 2.0→3.0, OpenAI 0.27→1.12 | Vercel 兼容性 |
| **外键约束** | 移除部分外键 | 云数据库兼容性 |
| **环境变量** | 分离本地/生产配置 | 不同环境不同配置 |

---

## 文件结构

### 新增文件

```
Fin-ai/
├── api/                          # 🆕 Serverless Functions
│   └── index.py                  # Flask 应用入口
├── vercel.json                   # 🆕 Vercel 配置文件
├── .env.example                  # 🆕 环境变量模板
├── test_connection.py            # 🆕 数据库连接测试
├── setup_railway.py              # 🆕 Railway 配置助手
└── VERCEL_DEPLOYMENT.md          # 🆕 本文档
```

### 修改文件

```
├── app.py                        # ✏️ CORS 配置优化
├── init_db.py                    # ✏️ 数据库兼容性修复
├── requirements.txt              # ✏️ 依赖版本升级
└── .gitignore                    # ✏️ 添加 Python/Vercel 忽略
```

---

## 核心配置

### 1. vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

**配置说明**:
- `buildCommand`: 前端构建命令
- `outputDirectory`: 前端构建输出目录
- `framework`: 告诉 Vercel 使用 Vite 框架
- `rewrites`: 将 `/api/*` 请求路由到 Python 后端

### 2. api/index.py

**核心改动**:

```python
# 1. CORS 配置 - 生产环境允许所有来源
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 生产环境
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

# 2. 自动导入所有 Controller
try:
    from controllers.bill_controller import bill_bp
    from controllers.transfer_controller import transfer_bp
    from controllers.home_controller import home_bp
    from controllers.user_controller import user_bp
    from controllers.ai_controller import ai_bp
    from controllers.ai_interaction import ai_interaction_bp
    from controllers.stock_controller import stock_bp
    from controllers.fund_controller import fund_bp
    
    app.register_blueprint(bill_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(ai_interaction_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(fund_bp)
except ImportError as e:
    print(f"警告: 蓝图导入失败 - {str(e)}")

# 3. Vercel 会自动检测 'app' 变量作为 WSGI 应用
```

### 3. 环境变量配置

#### 本地开发 (.env)
```env
FLASK_ENV=development
SECRET_KEY=<随机生成>
MYSQL_HOST=nozomi.proxy.rlwy.net
MYSQL_PORT=10872
MYSQL_USER=root
MYSQL_PASSWORD=<Railway密码>
MYSQL_DATABASE=railway
VITE_API_BASE_URL=http://localhost:5000
```

#### Vercel 生产环境
```env
FLASK_ENV=production
SECRET_KEY=<随机生成>
MYSQL_HOST=nozomi.proxy.rlwy.net
MYSQL_PORT=10872
MYSQL_USER=root
MYSQL_PASSWORD=<Railway密码>
MYSQL_DATABASE=railway
VITE_API_BASE_URL=/api  # ⚠️ 注意：使用相对路径
```

**差异说明**:
- `FLASK_ENV`: 本地用 `development`，生产用 `production`
- `VITE_API_BASE_URL`: 本地用完整 URL，生产用相对路径

---

## 部署流程

### 首次部署

#### 1. 准备云数据库 (Railway)

```bash
# 1.1 注册 Railway
访问: https://railway.app/
使用 GitHub 登录

# 1.2 创建 MySQL 数据库
New Project → Provision MySQL

# 1.3 启用公网访问
MySQL 服务 → Settings → Networking → Enable TCP Proxy

# 1.4 获取连接信息
Variables 标签页:
- MYSQLHOST=xxxxx.railway.app
- MYSQLPORT=xxxxx
- MYSQLUSER=root
- MYSQLPASSWORD=xxxxx
- MYSQLDATABASE=railway
```

#### 2. 配置本地环境

```bash
# 2.1 配置数据库连接
python setup_railway.py
# 或手动创建 .env 文件

# 2.2 安装依赖
pip install -r requirements.txt
npm install

# 2.3 初始化数据库
python init_db.py

# 2.4 测试本地运行
python app.py         # 后端
npm run dev           # 前端（新终端）
```

#### 3. 推送到 GitHub

```bash
git add .
git commit -m "feat: adapt project for Vercel deployment"
git push origin main
```

#### 4. 部署到 Vercel

```bash
# 4.1 访问 Vercel
https://vercel.com/

# 4.2 导入项目
New Project → Import Git Repository → 选择 Fin-ai

# 4.3 配置环境变量
Settings → Environment Variables → 添加以下变量
（详见下方环境变量章节）

# 4.4 部署
Deploy → 等待 2-5 分钟
```

### 更新部署

```bash
# 1. 本地开发和测试
# ... 修改代码 ...

# 2. 提交更改
git add .
git commit -m "feat: add new feature"
git push origin main

# 3. Vercel 自动部署
# 推送后自动触发，无需手动操作
```

---

## 环境变量

### 必需变量 (Required)

| 变量名 | 说明 | 示例 | Environment |
|--------|------|------|-------------|
| `SECRET_KEY` | Flask 密钥 | `ZT4_D7p7Vsxv...` | Production |
| `FLASK_ENV` | Flask 环境 | `production` | Production |
| `MYSQL_HOST` | 数据库地址 | `nozomi.proxy.rlwy.net` | All |
| `MYSQL_PORT` | 数据库端口 | `10872` | All |
| `MYSQL_USER` | 数据库用户 | `root` | All |
| `MYSQL_PASSWORD` | 数据库密码 | `heGCYFrr...` | All |
| `MYSQL_DATABASE` | 数据库名称 | `railway` | All |

### 可选变量 (Optional)

| 变量名 | 说明 | 示例 | 默认值 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-proj-...` | - |
| `OPENAI_MODEL` | OpenAI 模型 | `gpt-4-turbo-preview` | - |
| `ALLOWED_ORIGINS` | CORS 允许来源 | `https://example.com` | `*` |

### 环境变量配置步骤

#### Vercel 控制台

1. 进入项目 → **Settings** → **Environment Variables**
2. 点击 **Add** 按钮
3. 填写 Key 和 Value
4. 选择环境：
   - ✅ **Production** (必选)
   - ✅ **Preview** (推荐)
   - ✅ **Development** (可选)
5. 点击 **Save**
6. 重新部署使配置生效

#### 生成 SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 数据库配置

### Railway MySQL

#### 特性
- ✅ MySQL 9.4.0 (完全兼容)
- ✅ 支持外键约束
- ✅ 支持 JSON 字段
- ✅ 512 MB 免费存储
- ✅ 自动备份

#### 连接方式

```python
# utils/db.py 已配置
import pymysql
from pymysql.cursors import DictCursor
import os

conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE'),
    port=int(os.getenv('MYSQL_PORT', '3306')),
    cursorclass=DictCursor,
    charset='utf8mb4',
    connect_timeout=10
)
```

#### 数据库表结构

```sql
-- 用户表
Users (user_id, password, display_name)

-- 账单表
Bills (id, user_id, merchant, category, amount, transaction_date)

-- 转账历史表
TransferHistory (id, user_id, recipient_account, amount, transfer_date)

-- 股票表
Stocks (id, name, code, industry, market_cap, pe)

-- 基金表
Fundings (id, code, name, nav, change_percent, category)

-- AI 建议表
AISuggestions (id, page_type, suggestion_type, content)

-- 用户 AI 交互表
UserAIActions (id, user_id, page_type, action_type)
```

#### 初始化数据

```bash
# 运行初始化脚本
python init_db.py

# 创建的数据:
# - 1 个测试用户 (UTSZ/admin)
# - 8 条股票数据
# - 5 条基金数据
# - 10 条账单数据
# - 5 条转账历史数据
# - AI 建议配置数据
```

---

## 故障排查

### 常见问题

#### 1. API 返回 404

**症状**: `/api/login` 返回 404 Not Found

**原因**:
- `vercel.json` 路由配置错误
- `api/index.py` 未正确部署

**解决方案**:
```bash
# 检查 vercel.json 配置
cat vercel.json

# 确认 rewrites 配置正确
"rewrites": [
  { "source": "/api/(.*)", "destination": "/api/index.py" }
]

# 重新部署
git push origin main
```

#### 2. API 返回 500

**症状**: FUNCTION_INVOCATION_FAILED

**原因**:
- 环境变量缺失
- Python 代码错误
- 数据库连接失败

**解决方案**:
```bash
# 1. 查看 Vercel 日志
Deployments → Functions → api/index.py

# 2. 检查环境变量
Settings → Environment Variables

# 3. 测试数据库连接
python test_connection.py

# 4. 本地复现问题
FLASK_ENV=production python app.py
```

#### 3. CORS 错误

**症状**: Access-Control-Allow-Origin 错误

**原因**: CORS 配置不正确

**解决方案**:
```python
# api/index.py 中确认 CORS 配置
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 生产环境允许所有来源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    }
})
```

#### 4. 数据库连接超时

**症状**: Connection timeout

**原因**:
- Railway 服务未启动
- 网络问题
- 连接信息错误

**解决方案**:
```bash
# 1. 检查 Railway 服务状态
访问 Railway 控制台，确认 MySQL 服务为 Active

# 2. 验证连接信息
python test_connection.py

# 3. 检查防火墙
Railway 默认允许所有 IP，无需配置
```

### 调试技巧

#### 查看 Vercel 日志

```bash
# 1. 实时日志
Deployments → 最新部署 → View Function Logs

# 2. 构建日志
Deployments → 最新部署 → Building

# 3. 运行时日志
Deployments → Functions → api/index.py
```

#### 本地复现生产环境

```bash
# 1. 设置生产环境变量
export FLASK_ENV=production

# 2. 使用生产数据库
# 确保 .env 中的数据库是 Railway

# 3. 运行应用
python app.py

# 4. 测试 API
curl http://localhost:5000/api/health
```

---

## 维护指南

### 日常维护

#### 监控应用状态

```bash
# 1. Vercel Analytics
项目页面 → Analytics
- 查看访问量
- 分析用户行为
- 监控性能指标

# 2. Functions 执行时间
Deployments → Functions
- 查看函数执行时间
- 识别性能瓶颈
- 优化慢查询

# 3. Railway 数据库监控
MySQL 服务 → Metrics
- CPU 使用率
- 内存使用率
- 连接数
- 查询性能
```

#### 数据库备份

```bash
# Railway 自动备份（每日）
# 手动备份:
1. 访问 Railway 控制台
2. MySQL 服务 → Backups
3. Create Backup
4. 下载备份文件
```

#### 更新依赖

```bash
# Python 依赖
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt

# Node 依赖
npm outdated
npm update
npm install <package>@latest
```

### 扩展和优化

#### 性能优化

1. **数据库连接池**
```python
# utils/db.py
from DBUtils.PooledDB import PooledDB
import pymysql

pool = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE'),
    port=int(os.getenv('MYSQL_PORT', '3306')),
)
```

2. **缓存策略**
```python
# 使用 Redis (可选)
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL')
})

@app.route('/api/stocks')
@cache.cached(timeout=300)
def get_stocks():
    return stock_service.get_all()
```

3. **CDN 优化**
```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'antd-vendor': ['antd'],
        }
      }
    }
  }
})
```

#### 安全加固

1. **API 限流**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/login')
@limiter.limit("5 per minute")
def login():
    pass
```

2. **输入验证**
```python
from flask import request
from marshmallow import Schema, fields, ValidationError

class LoginSchema(Schema):
    username = fields.Str(required=True, max_length=50)
    password = fields.Str(required=True, max_length=50)

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = LoginSchema().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
```

3. **SQL 注入防护**
```python
# ✅ 正确: 使用参数化查询
cursor.execute(
    "SELECT * FROM Users WHERE user_id = %s",
    (user_id,)
)

# ❌ 错误: 字符串拼接
cursor.execute(
    f"SELECT * FROM Users WHERE user_id = '{user_id}'"
)
```

---

## 最佳实践

### 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 本地开发和测试
python app.py
npm run dev

# 3. 提交代码
git add .
git commit -m "feat: add new feature"

# 4. 推送到远程
git push origin feature/new-feature

# 5. 创建 Pull Request
在 GitHub 创建 PR

# 6. 合并到 main
合并后自动部署到生产环境
```

### 代码规范

#### Python
```python
# 使用类型提示
def get_user_by_id(user_id: str) -> Optional[Dict]:
    pass

# 使用文档字符串
def login(username: str, password: str) -> Dict:
    """
    用户登录
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        用户信息字典
        
    Raises:
        ValueError: 用户名或密码错误
    """
    pass
```

#### JavaScript
```javascript
// 使用 JSDoc
/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @returns {Promise<Array>} 用户列表
 */
export const getUserList = async (params) => {
  return request.get('/api/users', { params });
};
```

### 环境隔离

```
Development (本地)
    ↓
Preview (Vercel Preview)
    ↓
Staging (可选)
    ↓
Production (Vercel Production)
```

### 监控告警

```bash
# 1. 设置 Vercel 告警
Settings → Notifications
- 部署失败通知
- 函数错误通知
- 性能异常通知

# 2. Railway 监控
Settings → Alerts
- CPU 使用率 > 80%
- 内存使用率 > 80%
- 磁盘空间 < 20%
```

---

## 附录

### 相关链接

- **生产环境**: https://fin-ai-new6.vercel.app/
- **GitHub 仓库**: https://github.com/GSOP-S/Fin-ai
- **Vercel 文档**: https://vercel.com/docs
- **Railway 文档**: https://docs.railway.app/
- **Flask 文档**: https://flask.palletsprojects.com/

### 测试账号

- **用户名**: `UTSZ`
- **密码**: `admin`

### 联系方式

如有问题，请在 GitHub 提交 Issue。

---

**文档版本**: v2.1.0  
**最后更新**: 2025-10-31  
**维护者**: Fin-AI Team

