"""
混凝土生产管理系统 - 后端启动入口
"""
import uvicorn
import os

if __name__ == "__main__":
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"系统启动目录: {current_dir}")
    print("=" * 60)
    print("混凝土生产管理系统 - 后端服务")
    print("=" * 60)
    print(f"API文档地址: http://localhost:8000/docs")
    print(f"ReDoc文档地址: http://localhost:8000/redoc")
    print(f"健康检查地址: http://localhost:8000/health")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
