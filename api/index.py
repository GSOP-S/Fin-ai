"""
Vercel Serverless Function 入口文件
将Flask应用适配为Vercel的Serverless Functions
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS - 生产环境允许所有来源
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
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
    from controllers.asset_controller import asset_bp
    
    app.register_blueprint(bill_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ai_interaction_bp)
    app.register_blueprint(fund_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(behavior_bp)
    app.register_blueprint(asset_bp)
    
    # 注册AI路由（使用新的注册方式）
    from controllers.ai_controller import register_ai_routes
    register_ai_routes(app)
    
    print("✅ 所有蓝图注册成功")
except ImportError as e:
    print(f"⚠️ 警告: 蓝图导入失败 - {str(e)}")

# 静态资讯图片路由
@app.route('/api/assets/news/<path:filename>')
def serve_news_image(filename):
    """提供新闻图片资源"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'figure'),
            filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

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
