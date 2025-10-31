"""
Railway MySQL 配置助手
帮助快速配置 Railway 数据库连接
"""

import os
import secrets

def generate_secret_key():
    """生成随机密钥"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """创建 .env 文件"""
    print("=" * 60)
    print("Railway MySQL 配置助手")
    print("=" * 60)
    print()
    
    # 检查 .env 是否已存在
    env_exists = os.path.exists('.env')
    if env_exists:
        overwrite = input("⚠️  .env 文件已存在，是否覆盖？(y/n): ").lower()
        if overwrite != 'y':
            print("❌ 取消配置")
            return
    
    print("\n请输入 Railway MySQL 连接信息：")
    print("（从 Railway 控制台的 Variables 标签页获取）\n")
    
    # 获取用户输入
    mysql_host = input("MYSQL_HOST (例: containers-us-west-xxx.railway.app): ").strip()
    mysql_port = input("MYSQL_PORT (例: 6543): ").strip() or "3306"
    mysql_user = input("MYSQL_USER (默认: root): ").strip() or "root"
    mysql_password = input("MYSQL_PASSWORD: ").strip()
    mysql_database = input("MYSQL_DATABASE (默认: railway): ").strip() or "railway"
    
    # OpenAI API Key (可选)
    print("\n是否配置 OpenAI API？(如果不使用 AI 功能可跳过)")
    use_openai = input("配置 OpenAI? (y/n): ").lower() == 'y'
    openai_key = ""
    if use_openai:
        openai_key = input("OPENAI_API_KEY: ").strip()
    
    # 生成密钥
    secret_key = generate_secret_key()
    
    # 创建 .env 内容
    env_content = f"""# Flask 配置
FLASK_ENV=development
SECRET_KEY={secret_key}
PORT=5000

# Railway MySQL 数据库配置
MYSQL_HOST={mysql_host}
MYSQL_USER={mysql_user}
MYSQL_PASSWORD={mysql_password}
MYSQL_DATABASE={mysql_database}
MYSQL_PORT={mysql_port}

# OpenAI API 配置
OPENAI_API_KEY={openai_key}
OPENAI_MODEL=gpt-4-turbo-preview

# 前端 API 配置
VITE_API_BASE_URL=http://localhost:5000
"""
    
    # 写入文件
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n" + "=" * 60)
        print("✅ .env 文件创建成功！")
        print("=" * 60)
        print("\n配置信息：")
        print(f"  数据库主机: {mysql_host}")
        print(f"  数据库端口: {mysql_port}")
        print(f"  数据库用户: {mysql_user}")
        print(f"  数据库名称: {mysql_database}")
        print(f"  SECRET_KEY: {secret_key}")
        print()
        print("🔒 重要：请妥善保管这些信息！")
        print()
        print("=" * 60)
        print("下一步：")
        print("=" * 60)
        print("1. 运行：pip install -r requirements.txt")
        print("2. 运行：python init_db.py  （初始化数据库）")
        print("3. 运行：python app.py  （启动应用）")
        print()
        print("在 Vercel 部署时，需要添加以下环境变量：")
        print("-" * 60)
        print(f"SECRET_KEY={secret_key}")
        print(f"FLASK_ENV=production")
        print(f"MYSQL_HOST={mysql_host}")
        print(f"MYSQL_USER={mysql_user}")
        print(f"MYSQL_PASSWORD={mysql_password}")
        print(f"MYSQL_DATABASE={mysql_database}")
        print(f"MYSQL_PORT={mysql_port}")
        if openai_key:
            print(f"OPENAI_API_KEY={openai_key}")
        print(f"VITE_API_BASE_URL=/api")
        print("-" * 60)
        
    except Exception as e:
        print(f"\n❌ 创建 .env 文件失败: {e}")

if __name__ == '__main__':
    create_env_file()

