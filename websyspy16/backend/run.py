"""
后端服务启动脚本
解决Windows下GBK编码问题
"""
import sys
import os

# 设置默认编码为UTF-8，解决Windows下GBK编码问题
if sys.platform == 'win32':
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 重新设置stdout/stderr编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
