"""
首页控制器 Controller
处理首页相关的HTTP请求
"""

from flask import Blueprint, request
from utils.response import success_response, error_response, handle_exceptions
from services.home_suggestion_service import HomeSuggestionService

# 创建蓝图
home_bp = Blueprint('home', __name__, url_prefix='/api')

