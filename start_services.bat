@echo off

REM 启动Flask后端服务
start "Flask Backend" cmd /k "cd /d %cd% && python -m venv venv && call venv\Scripts\activate && pip install -r requirements.txt && python backend.py"

REM 等待后端服务启动
ping 127.0.0.1 -n 5 > nul

echo 后端服务已启动，正在启动前端服务...

REM 启动前端开发服务器
start "React Frontend" cmd /k "cd /d %cd% && npm install && npm run dev"

echo 服务启动完成！请在浏览器中访问 http://localhost:3000