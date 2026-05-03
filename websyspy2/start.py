"""
启动脚本
用于测试和启动进销存管理系统
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("进销存管理系统 - 启动测试")
print("=" * 60)

# 测试导入依赖
print("\n[1/3] 检查依赖包...")
dependencies = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("sqlalchemy", "SQLAlchemy"),
    ("pydantic", "Pydantic"),
    ("jinja2", "Jinja2"),
    ("openpyxl", "OpenPyXL"),
    ("passlib", "PassLib"),
]

all_ok = True
for module, name in dependencies:
    try:
        __import__(module)
        print(f"  ✓ {name} - 已安装")
    except ImportError:
        print(f"  ✗ {name} - 未安装")
        all_ok = False

if not all_ok:
    print("\n警告：部分依赖未安装，请运行: pip install -r requirements.txt")
    sys.exit(1)

print("\n[2/3] 导入模块...")
try:
    from config import DATABASE_URL
    print(f"  ✓ 配置模块 - 数据库: {DATABASE_URL}")
    
    from database import init_db, get_db
    print("  ✓ 数据库模块")
    
    import models
    print("  ✓ 数据模型")
    
    import schemas
    print("  ✓ 数据验证模型")
    
    import crud
    print("  ✓ CRUD操作模块")
    
    print("\n[3/3] 初始化数据库...")
    init_db()
    print("  ✓ 数据库表创建成功")
    
except Exception as e:
    print(f"  ✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("系统初始化完成！")
print("=" * 60)
print("\n启动方式:")
print("  1. 使用 uvicorn:")
print("     uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
print("")
print("  2. 直接运行:")
print("     python main.py")
print("")
print("访问地址: http://localhost:8000")
print("")
print("测试账号:")
print("  - 管理员: admin / admin123")
print("  - 普通用户: user1 / 123456")
print("")
print("提示: 首次使用请点击页面上的\"生成测试数据\"按钮")
print("=" * 60)

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    print("\n启动服务器...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
