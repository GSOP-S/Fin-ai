"""
Railway 数据库配置助手
帮助用户快速配置 Railway MySQL 连接信息
"""

import os
import secrets

def generate_secret_key():
    """生成随机的 SECRET_KEY"""
    return secrets.token_urlsafe(32)

def setup_railway():
    """交互式配置 Railway 数据库"""
    print("=" * 60)
    print("Railway MySQL 配置助手")
    print("=" * 60)
    print()
    print("请按照以下步骤配置 Railway 数据库:")
    print()
    print("1. 访问 https://railway.app/ 并登录")
    print("2. 创建新项目 → Provision MySQL")
    print("3. 在 MySQL 服务中:")
    print("   - Settings → Networking → Enable TCP Proxy")
    print("   - Variables 标签页获取连接信息")
    print()
    print("=" * 60)
    print()
    
    # 获取用户输入
    print("请输入 Railway MySQL 连接信息:")
    print()
    
    mysql_host = input("MYSQL_HOST (例: nozomi.proxy.rlwy.net): ").strip()
    mysql_port = input("MYSQL_PORT (默认: 3306): ").strip() or "3306"
    mysql_user = input("MYSQL_USER (默认: root): ").strip() or "root"
    mysql_password = input("MYSQL_PASSWORD: ").strip()
    mysql_database = input("MYSQL_DATABASE (默认: railway): ").strip() or "railway"
    
    print()
    openai_key = input("OPENAI_API_KEY (可选，直接回车跳过): ").strip()
    
    # 生成 SECRET_KEY
    secret_key = generate_secret_key()
    
    # 创建 .env 文件内容
    env_content = f"""# Flask 配置
FLASK_ENV=development
SECRET_KEY={secret_key}

# 数据库配置 (Railway MySQL)
MYSQL_HOST={mysql_host}
MYSQL_PORT={mysql_port}
MYSQL_USER={mysql_user}
MYSQL_PASSWORD={mysql_password}
MYSQL_DATABASE={mysql_database}

# OpenAI API 配置 (可选)
{f'OPENAI_API_KEY={openai_key}' if openai_key else '# OPENAI_API_KEY=sk-proj-your-openai-api-key'}
OPENAI_MODEL=gpt-3.5-turbo

# 前端 API 配置
VITE_API_BASE_URL=http://localhost:5000

# CORS 配置
ALLOWED_ORIGINS=*
"""
    
    # 写入 .env 文件
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print()
    print("=" * 60)
    print("✅ 配置完成!")
    print("=" * 60)
    print()
    print("已创建 .env 文件，包含以下配置:")
    print(f"  - MYSQL_HOST: {mysql_host}")
    print(f"  - MYSQL_PORT: {mysql_port}")
    print(f"  - MYSQL_USER: {mysql_user}")
    print(f"  - MYSQL_PASSWORD: {'*' * len(mysql_password)}")
    print(f"  - MYSQL_DATABASE: {mysql_database}")
    print(f"  - SECRET_KEY: {secret_key[:20]}...")
    if openai_key:
        print(f"  - OPENAI_API_KEY: {openai_key[:20]}...")
    print()
    print("下一步:")
    print("  1. 测试数据库连接: python test_connection.py")
    print("  2. 初始化数据库: python init_db.py")
    print("  3. 启动应用: python app.py")
    print()
    print("=" * 60)

if __name__ == '__main__':
    try:
        setup_railway()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
