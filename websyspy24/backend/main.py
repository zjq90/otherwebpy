"""
主应用入口文件
FastAPI应用的入口，包含路由注册、中间件配置和启动事件
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn

from database import init_db, get_db
from test_data import generate_all_test_data

# 导入路由模块
from routers import members, checkins, lockers, cashier


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库
    """
    # 启动时执行
    print("=" * 60)
    print("正在启动 Gym Management System API...")
    print("=" * 60)
    
    # 初始化数据库
    init_db()
    print("✓ 数据库初始化完成")
    
    print("=" * 60)
    print("API服务已启动")
    print("API文档地址: http://localhost:8000/docs")
    print("=" * 60)
    
    yield
    
    # 关闭时执行
    print("=" * 60)
    print("API服务已关闭")
    print("=" * 60)


# 创建FastAPI应用实例
app = FastAPI(
    title="Gym Management System API",
    description="""
    健身房管理系统API文档
    
    ## 功能模块
    
    - **会员管理**: 会员的增删改查、会籍管理、账户充值
    - **签到管理**: 支持刷卡、扫码、人脸识别三种签到方式，自动判断会籍有效性
    - **储物柜管理**: 储物柜状态监控、自动/手动分配、归还提醒
    - **收银管理**: 商品管理、优惠券管理、订单管理、支付功能、流水对账
    
    ## 技术栈
    
    - 后端: Python + FastAPI + SQLAlchemy
    - 数据库: SQLite
    - 文档: OpenAPI (Swagger UI)
    """,
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(members.router)
app.include_router(checkins.router)
app.include_router(lockers.router)
app.include_router(cashier.router)


# ==================== 系统管理API ====================
@app.get("/", tags=["系统管理"], summary="系统状态检查")
def root():
    """
    检查系统是否正常运行
    """
    return {
        "status": "running",
        "message": "Gym Management System API is running",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/api/health", tags=["系统管理"], summary="健康检查")
def health_check():
    """
    健康检查接口，用于监控
    """
    return {
        "status": "healthy",
        "timestamp": "2026-05-04T00:00:00"
    }


@app.post("/api/test/generate-data", tags=["测试功能"], summary="生成测试数据")
def generate_test_data_api(
    db: Session = Depends(get_db)
):
    """
    生成测试数据，包括：
    - 会员数据 (20个)
    - 储物柜数据 (30个)
    - 商品数据 (15个)
    - 优惠券数据 (10个)
    - 签到记录 (50条)
    """
    try:
        result = generate_all_test_data(db)
        return {
            "success": True,
            "message": "测试数据生成成功",
            "data": {
                "members_count": len(result["members"]),
                "lockers_count": len(result["lockers"]),
                "products_count": len(result["products"]),
                "coupons_count": len(result["coupons"]),
                "checkins_count": len(result["checkins"])
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"测试数据生成失败: {str(e)}",
            "data": None
        }


@app.get("/api/test/summary", tags=["测试功能"], summary="获取数据统计摘要")
def get_test_summary(
    db: Session = Depends(get_db)
):
    """
    获取数据库中各表的数据统计
    """
    from models import Member, Locker, Product, Coupon, CheckIn, Order, PaymentRecord
    
    counts = {
        "members": db.query(Member).count(),
        "lockers": db.query(Locker).count(),
        "products": db.query(Product).count(),
        "coupons": db.query(Coupon).count(),
        "checkins": db.query(CheckIn).count(),
        "orders": db.query(Order).count(),
        "payments": db.query(PaymentRecord).count()
    }
    
    # 储物柜状态统计
    from models import LockerStatus
    locker_stats = {
        "available": db.query(Locker).filter(Locker.status == "available").count(),
        "occupied": db.query(Locker).filter(Locker.status == "occupied").count(),
        "maintenance": db.query(Locker).filter(Locker.status == "maintenance").count()
    }
    
    # 会员状态统计
    member_stats = {
        "active": db.query(Member).filter(Member.status == "active").count(),
        "suspended": db.query(Member).filter(Member.status == "suspended").count()
    }
    
    return {
        "success": True,
        "message": "获取统计成功",
        "data": {
            "total_counts": counts,
            "locker_stats": locker_stats,
            "member_stats": member_stats
        }
    }


@app.get("/api/test/quick-test", tags=["测试功能"], summary="快速测试功能")
def quick_test(
    db: Session = Depends(get_db)
):
    """
    快速测试接口，返回系统的基本测试数据
    用于前端页面快速填充测试数据
    """
    from models import Member, Locker, Product, Coupon, Order
    
    # 获取一些活跃会员
    active_members = db.query(Member).filter(
        Member.status == "active"
    ).limit(10).all()
    
    # 获取可用储物柜
    available_lockers = db.query(Locker).filter(
        Locker.status == "available"
    ).limit(10).all()
    
    # 获取在售商品
    active_products = db.query(Product).filter(
        Product.status == "active"
    ).limit(10).all()
    
    # 获取可用优惠券
    available_coupons = db.query(Coupon).filter(
        Coupon.status == "available"
    ).limit(5).all()
    
    return {
        "success": True,
        "message": "快速测试数据获取成功",
        "data": {
            "active_members": [
                {
                    "id": m.id,
                    "member_no": m.member_no,
                    "name": m.name,
                    "phone": m.phone,
                    "card_no": m.card_no,
                    "qr_code": m.qr_code,
                    "membership_type": m.membership_type,
                    "membership_end": m.membership_end.isoformat() if m.membership_end else None,
                    "balance": round(m.balance, 2)
                }
                for m in active_members
            ],
            "available_lockers": [
                {
                    "id": l.id,
                    "locker_no": l.locker_no,
                    "location": l.location,
                    "locker_type": l.locker_type
                }
                for l in available_lockers
            ],
            "active_products": [
                {
                    "id": p.id,
                    "product_code": p.product_code,
                    "name": p.name,
                    "category": p.category,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity
                }
                for p in active_products
            ],
            "available_coupons": [
                {
                    "id": c.id,
                    "coupon_code": c.coupon_code,
                    "name": c.name,
                    "coupon_type": c.coupon_type,
                    "value": c.value,
                    "min_amount": c.min_amount,
                    "expire_time": c.expire_time.isoformat() if c.expire_time else None
                }
                for c in available_coupons
            ]
        }
    }


if __name__ == "__main__":
    # 运行服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
