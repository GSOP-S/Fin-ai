"""
Vercel Serverless Functions 入口文件
负责应用初始化、蓝图注册和WSGI应用导出
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS - 生产环境允许所有来源
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 生产环境允许所有来源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

# 注册蓝图 - Controller层
try:
    from controllers.bill_controller import bill_bp
    from controllers.transfer_controller import transfer_bp
    from controllers.home_controller import home_bp
    from controllers.user_controller import user_bp
    from controllers.ai_interaction import ai_interaction_bp
    from controllers.fund_controller import fund_bp
    from controllers.news_controller import news_bp
    from controllers.behavior_controller import behavior_bp
    
    app.register_blueprint(bill_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ai_interaction_bp)
    app.register_blueprint(fund_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(behavior_bp)
    
    print("[Vercel] 蓝图注册成功")
except ImportError as e:
    print(f"[Vercel] 警告: 蓝图导入失败 - {str(e)}")

# 注册AI路由（使用新的注册方式）
try:
    from controllers.ai_controller import register_ai_routes
    register_ai_routes(app)
    print("[Vercel] AI路由注册成功")
except ImportError as e:
    print(f"[Vercel] 警告: AI路由导入失败 - {str(e)}")

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'version': '2.1.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'platform': 'Vercel Serverless'
    })

# 根路径
@app.route('/')
def index():
    """根路径重定向"""
    return jsonify({
        'message': 'Fin-AI API Server',
        'version': '2.1.0',
        'docs': '/api/health'
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested URL was not found on the server.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'The server encountered an internal error.'
    }), 500

# Vercel 会自动检测 'app' 变量作为 WSGI 应用
# 不需要 if __name__ == '__main__' 块
