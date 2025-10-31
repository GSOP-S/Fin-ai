"""
Vercel Serverless Function 入口文件
将 Flask 应用改造为适配 Vercel 的 WSGI 应用
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 配置CORS - 支持所有来源（生产环境）
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Vercel 部署后允许所有来源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
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

# 健康检查接口
@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'version': '2.1.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'platform': 'Vercel Serverless'
    })

# 根路径接口
@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def index():
    """API 根路径"""
    return jsonify({
        'message': 'Fin-AI API Server',
        'version': '2.1.0',
        'status': 'running',
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
        'message': str(error)
    }), 500

# Vercel 需要这个变量名
handler = app

# 本地测试支持
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

