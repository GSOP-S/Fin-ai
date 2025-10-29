"""
Flask应用入口文件
负责应用初始化、蓝图注册和启动
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 注册蓝图 - Controller层
from controllers.bill_controller import bill_bp
from controllers.transfer_controller import transfer_bp
from controllers.home_controller import home_bp
from controllers.user_controller import user_bp
from controllers.ai_controller import ai_bp
from controllers.stock_controller import stock_bp
from controllers.fund_controller import fund_bp

app.register_blueprint(bill_bp)
app.register_blueprint(transfer_bp)
app.register_blueprint(home_bp)
app.register_blueprint(user_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(fund_bp)

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