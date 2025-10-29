"""统一响应结构与异常处理工具
提供 success_response、error_response 以及 handle_exceptions 装饰器，
方便在各个 Controller 中统一返回格式并集中处理异常。
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Tuple

from flask import jsonify

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

JsonResponse = Tuple[Any, int]


def success_response(data: Any = None, message: str = "success", status_code: int = 200) -> JsonResponse:
    """构造成功响应

    Args:
        data: 响应数据，可为任意 JSON 可序列化对象。
        message: 提示消息，默认为 "success"。
        status_code: HTTP 状态码，默认 200。
    """
    return jsonify({
        "success": True,
        "data": data,
        "message": message,
    }), status_code


def error_response(error: str = "", message: str = "error", status_code: int = 500) -> JsonResponse:
    """构造错误响应

    Args:
        error: 错误详情信息。
        message: 人类可读提示，默认为 "error"。
        status_code: HTTP 状态码，默认 500。
    """
    return jsonify({
        "success": False,
        "error": error,
        "message": message,
    }), status_code


def handle_exceptions(func: Callable) -> Callable:
    """装饰器：捕获路由处理函数中的异常并统一返回错误响应"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            # 记录详细的错误日志
            logger.error(f"Error in {func.__name__}: {str(exc)}", exc_info=True)
            # 这里可以根据异常类型做更细粒度的处理，例如数据库错误、验证错误等
            return error_response(str(exc), message="Internal Server Error", status_code=500)

    return wrapper