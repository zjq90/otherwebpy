"""
智慧农业管理系统启动脚本
用于快速启动系统的开发服务器
"""
import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.config import settings


def main():
    """
    主函数 - 启动FastAPI服务器
    """
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)
    print("\n正在启动系统...")
    print(f"\n访问地址:")
    print(f"  - 首页: http://localhost:8000")
    print(f"  - API文档: http://localhost:8000/docs")
    print(f"  - API备用文档: http://localhost:8000/redoc")
    print(f"\n功能模块:")
    print(f"  - 种植计划管理: http://localhost:8000/planting-plans")
    print(f"  - 农事作业记录: http://localhost:8000/farm-operations")
    print(f"  - 精准施肥与灌溉: http://localhost:8000/fertilization-irrigations")
    print(f"  - 病虫害防治管理: http://localhost:8000/pest-disease-controls")
    print("\n" + "=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智慧农业管理系统启动脚本")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)")
    parser.add_argument("--no-reload", action="store_true", help="禁用自动重载")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload and settings.DEBUG,
        log_level="info"
    )
