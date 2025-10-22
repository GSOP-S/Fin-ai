# 金融数据分析后端服务

一个提供股票、基金数据和市场分析的后端API服务。

## 功能特点
- 用户认证与授权
- 股票市场数据查询
- 基金数据统计分析
- 市场趋势分析报告
- AI助手投资建议

## 环境要求
- Python 3.8+ 
- MySQL 5.7+ 
- pip (Python包管理器)
- 虚拟环境工具 (可选但推荐)

## 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/financial-analysis-backend.git
cd financial-analysis-backend
```

### 2. 创建并激活虚拟环境

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
创建`.env`文件在项目根目录，添加以下内容：
```
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=fin_db

# Flask配置
FLASK_APP=backend.py
FLASK_ENV=development
SECRET_KEY=your_secret_key

# API密钥
OPENAI_API_KEY=your_openai_key
```

### 5. 初始化数据库
```bash
python init_db.py
```

### 6. 启动服务
```bash
python backend.py
```

## API文档
服务启动后，访问 http://localhost:5000/api/docs 查看API文档

## 项目结构
- `backend.py` - 主应用入口
- `init_db.py` - 数据库初始化脚本
- `requirements.txt` - 项目依赖
- `.env` - 环境变量配置(不纳入版本控制)
- `src/` - 前端静态资源

## 贡献指南
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证
[MIT](https://choosealicense.com/licenses/mit/)
