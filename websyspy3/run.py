"""
CD管理系统启动脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import HOST, PORT, DEBUG

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("CD管理系统")
    print("=" * 50)
    print(f"服务器地址: http://{HOST}:{PORT}")
    print("测试账号:")
    print("  管理员: admin / admin123")
    print("  普通用户: user1 / user123")
    print("=" * 50)
    print("提示: 首次运行请先执行 python database/init_db.py 初始化数据库")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
