@echo off
echo ============================================
echo    农产品电商管理系统启动脚本
echo ============================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 检查虚拟环境...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt -q

echo.
echo ============================================
echo 请选择操作：
echo ============================================
echo.
echo [1] 启动系统（默认端口8000）
echo [2] 生成测试数据
echo [3] 查看API文档
echo [4] 退出
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 启动系统...
    echo 系统将在 http://localhost:8000 启动
    echo 按 Ctrl+C 停止服务
    echo.
    python run.py
) else if "%choice%"=="2" (
    echo.
    echo 生成测试数据...
    python -c "from test_data.generate_test_data import main; main()"
    echo.
    echo 测试数据生成完成！
    pause
) else if "%choice%"=="3" (
    echo.
    echo 正在打开API文档...
    start http://localhost:8000/docs
    echo 请先启动系统（选择选项1）
    pause
) else if "%choice%"=="4" (
    echo 退出...
    exit /b 0
) else (
    echo 无效选项，请重新运行脚本
    pause
)
