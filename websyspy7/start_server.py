"""
启动服务器测试脚本
用于验证所有模块是否能正常导入和运行
"""
import os
import sys

# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("车票监控系统 - 启动测试")
print("=" * 60)

# 测试1: 检查所有依赖是否可用
print("\n[步骤1] 检查依赖库...")
try:
    import fastapi
    print(f"  [OK] fastapi: {fastapi.__version__}")
except ImportError as e:
    print(f"  [FAIL] fastapi: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"  [OK] uvicorn: 已安装")
except ImportError as e:
    print(f"  [FAIL] uvicorn: {e}")
    sys.exit(1)

try:
    import jinja2
    print(f"  [OK] jinja2: {jinja2.__version__}")
except ImportError as e:
    print(f"  [FAIL] jinja2: {e}")
    sys.exit(1)

try:
    from sqlalchemy import __version__ as sa_version
    print(f"  [OK] sqlalchemy: {sa_version}")
except ImportError as e:
    print(f"  [FAIL] sqlalchemy: {e}")
    sys.exit(1)

try:
    import aiosqlite
    print(f"  [OK] aiosqlite: {aiosqlite.__version__}")
except ImportError as e:
    print(f"  [FAIL] aiosqlite: {e}")
    sys.exit(1)

# 测试2: 导入项目模块
print("\n[步骤2] 导入项目模块...")
try:
    from config import settings
    print(f"  [OK] config - 项目名称: {settings.PROJECT_NAME}")
except Exception as e:
    print(f"  [FAIL] config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from database import engine, async_session_maker, Base, init_db, get_db
    print(f"  [OK] database - 数据库URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"  [FAIL] database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from models import User, Passenger, MonitorTask, Order, AlertRecord
    print(f"  [OK] models - 已加载所有数据模型")
except Exception as e:
    print(f"  [FAIL] models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from auth import get_password_hash, verify_password, create_access_token
    print(f"  [OK] auth - 认证模块已加载")
except Exception as e:
    print(f"  [FAIL] auth: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from http_client import http_client, TicketHttpClient
    print(f"  [OK] http_client - HTTP客户端已加载")
except Exception as e:
    print(f"  [FAIL] http_client: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from monitor_service import monitor_service, MonitorService
    print(f"  [OK] monitor_service - 监控服务已加载")
except Exception as e:
    print(f"  [FAIL] monitor_service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3: 导入主应用
print("\n[步骤3] 导入FastAPI主应用...")
try:
    import main
    print(f"  [OK] main - 应用标题: {main.app.title}")
    print(f"  [OK] main - API路由数量: {len(main.app.routes)}")
except Exception as e:
    print(f"  [FAIL] main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试4: 检查模板目录
print("\n[步骤4] 检查模板目录...")
template_dir = os.path.join(os.path.dirname(__file__), "templates")
if os.path.exists(template_dir):
    templates = os.listdir(template_dir)
    print(f"  [OK] 模板目录存在，包含 {len(templates)} 个文件:")
    for t in templates:
        print(f"       - {t}")
else:
    print(f"  [WARN] 模板目录不存在，将自动创建")

print("\n" + "=" * 60)
print("所有测试通过！系统准备就绪。")
print("=" * 60)
print("\n启动命令:")
print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
print("  或直接运行: python start_server.py")
print("\n访问地址:")
print("  登录页面: http://localhost:8000/")
print("  API文档: http://localhost:8000/docs")
print("\n默认账号:")
print("  管理员: admin / admin123")
print("  测试用户: testuser / test123")
print("")

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    print("正在启动服务器...")
    print("按 Ctrl+C 停止服务器")
    print("")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
