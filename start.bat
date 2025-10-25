@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   🚀 Fin-AI v2.0 快速启动脚本                           ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo [2/3] 检查Node.js环境...
node --version
if errorlevel 1 (
    echo ❌ Node.js未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo [3/3] 启动服务...
echo.

echo 📌 提示：
echo   - 后端将运行在 http://localhost:5000
echo   - 前端将运行在 http://localhost:3000
echo   - 按 Ctrl+C 可以停止服务
echo.
pause

echo.
echo 正在启动后端服务...
start "Fin-AI 后端" cmd /k "python backend.py"

timeout /t 3 >nul

echo 正在启动前端服务...
start "Fin-AI 前端" cmd /k "npm run dev"

echo.
echo ✅ 服务启动完成！
echo.
echo 🌐 请在浏览器中访问: http://localhost:3000
echo.
echo 📚 查看升级文档: UPGRADE_V2_README.md
echo.

