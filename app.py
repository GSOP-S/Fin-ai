"""
Flask应用入口文件
负责应用初始化、蓝图注册和启动
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS - 允许常用的开发端口
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:3004",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# 注册蓝图 - Controller层
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

# 测试页面路由
@app.route('/test_mock.html')
def test_mock_page():
    """提供Mock测试页面"""
    return send_from_directory('.', 'test_mock.html')

@app.route('/mock_demo.html')
def mock_demo_page():
    """提供Mock演示页面"""
    return send_from_directory('.', 'mock_demo.html')

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'version': '2.1.0',
        'environment': os.getenv('FLASK_ENV', 'development')
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

# 启动应用
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)