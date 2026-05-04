"""
健身课程预约系统 - 后端API
技术栈: Python + FastAPI + SQLite + SQLAlchemy + OpenAPI

目录结构:
backend/
├── app/
│   ├── main.py          # FastAPI主应用入口
│   ├── db/              # 数据库配置
│   │   ├── __init__.py
│   │   └── database.py  # 数据库连接和会话管理
│   ├── models/          # 数据库模型
│   │   ├── __init__.py
│   │   └── models.py    # SQLAlchemy模型定义
│   ├── schemas/         # Pydantic模型
│   │   ├── __init__.py
│   │   └── schemas.py   # 请求/响应数据验证模型
│   ├── crud/            # 数据库操作
│   │   ├── __init__.py
│   │   └── crud.py      # CRUD操作封装
│   ├── core/            # 核心模块
│   │   ├── __init__.py
│   │   └── security.py  # 安全认证(JWT, 密码加密)
│   ├── routers/         # API路由
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证路由
│   │   ├── classes.py       # 课程日历路由
│   │   ├── bookings.py      # 预约路由
│   │   ├── checkin.py       # 签到路由
│   │   ├── private_booking.py # 私教预约路由
│   │   ├── cards.py         # 会员卡路由
│   │   └── admin.py         # 管理后台路由
│   └── scripts/         # 脚本
│       ├── __init__.py
│       └── init_data.py # 初始化测试数据
├── requirements.txt     # Python依赖
└── run.py              # 启动脚本
"""
