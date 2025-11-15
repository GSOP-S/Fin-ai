@echo off
echo 启动Mock日志分析测试服务器...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if not defined VIRTUAL_ENV (
    echo 警告: 建议在虚拟环境中运行
    echo.
)

REM 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 启动Flask应用
echo.
echo 启动Flask应用...
echo 服务器将在 http://localhost:5000 上运行
echo 测试页面可在 http://localhost:5000/test_mock.html 访问
echo.
python app.py

pause