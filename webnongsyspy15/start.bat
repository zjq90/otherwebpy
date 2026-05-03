@echo off
chcp 65001
echo ============================================
echo    农业报表系统 - 启动脚本
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python环境已就绪

echo.
echo [2/4] 检查虚拟环境...
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)
echo [OK] 虚拟环境已就绪

echo.
echo [3/4] 安装依赖包...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖包已安装

echo.
echo [4/4] 启动服务...
echo.
echo ============================================
echo    服务已启动！
echo ============================================
echo.
echo 访问地址：
echo   - 主页: http://localhost:8000
echo   - API文档: http://localhost:8000/docs
echo   - 登录页面: http://localhost:8000/login
echo.
echo 测试账号：
echo   - 管理员: admin / admin123
echo   - 农场经理: manager / manager123
echo   - 数据查看员: viewer / viewer123
echo.
echo 首次使用请先运行：python generate_test_data.py
echo 按 Ctrl+C 停止服务
echo ============================================
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
