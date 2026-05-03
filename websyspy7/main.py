"""
主应用入口文件
FastAPI应用初始化和路由注册
"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from config import settings
from database import init_db, get_db, async_session_maker
from models import User, Passenger, MonitorTask, Order, AlertRecord
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from http_client import http_client
from monitor_service import monitor_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时初始化数据库
    await init_db()
    
    # 创建默认管理员用户
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        # 检查是否已存在管理员
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                email="admin@example.com",
                is_admin=True,
                is_active=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
    
    yield
    
    # 关闭时清理资源
    await http_client.close_session()


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件和模板目录
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ==================== 前端页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 - 登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """仪表盘页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/passengers", response_class=HTMLResponse)
async def passengers_page(request: Request):
    """乘客管理页面"""
    return templates.TemplateResponse("passengers.html", {"request": request})


@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    """监控任务页面"""
    return templates.TemplateResponse("monitor.html", {"request": request})


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    """订单管理页面"""
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """提醒中心页面"""
    return templates.TemplateResponse("alerts.html", {"request": request})


# ==================== API路由 ====================

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc


# Pydantic模型
class LoginRequest(BaseModel):
    username: str
    password: str


class PassengerCreate(BaseModel):
    name: str
    id_card: str
    phone: Optional[str] = None
    passenger_type: str = "成人"
    is_default: bool = False


class MonitorTaskCreate(BaseModel):
    task_name: str
    from_station: str
    to_station: str
    train_date: str
    train_numbers: Optional[str] = None
    seat_types: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    passenger_ids: Optional[str] = None
    poll_interval: float = 1.0
    auto_submit: bool = False
    max_retries: int = 3


# 认证API
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }
    }


@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": current_user.phone,
            "is_admin": current_user.is_admin
        }
    }


# 乘客管理API
@app.get("/api/v1/passengers")
async def list_passengers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取乘客列表"""
    result = await db.execute(
        select(Passenger).where(Passenger.user_id == current_user.id)
    )
    passengers = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "id_card": p.id_card[:6] + "********" + p.id_card[-4:] if p.id_card else None,
                "phone": p.phone,
                "passenger_type": p.passenger_type,
                "is_default": p.is_default,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in passengers
        ]
    }


@app.post("/api/v1/passengers")
async def create_passenger(
    passenger: PassengerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建乘客"""
    # 如果设置为默认，取消其他默认设置
    if passenger.is_default:
        await db.execute(
            update(Passenger)
            .where(Passenger.user_id == current_user.id)
            .values(is_default=False)
        )
    
    new_passenger = Passenger(
        user_id=current_user.id,
        name=passenger.name,
        id_card=passenger.id_card,
        phone=passenger.phone,
        passenger_type=passenger.passenger_type,
        is_default=passenger.is_default,
        status="active"
    )
    db.add(new_passenger)
    await db.commit()
    await db.refresh(new_passenger)
    
    return {
        "success": True,
        "data": {
            "id": new_passenger.id,
            "name": new_passenger.name
        },
        "message": "乘客添加成功"
    }


@app.put("/api/v1/passengers/{passenger_id}")
async def update_passenger(
    passenger_id: int,
    passenger_data: PassengerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新乘客信息"""
    result = await db.execute(
        select(Passenger).where(
            Passenger.id == passenger_id,
            Passenger.user_id == current_user.id
        )
    )
    passenger = result.scalar_one_or_none()
    
    if not passenger:
        raise HTTPException(status_code=404, detail="乘客不存在")
    
    # 如果设置为默认，取消其他默认设置
    if passenger_data.is_default:
        await db.execute(
            update(Passenger)
            .where(Passenger.user_id == current_user.id)
            .values(is_default=False)
        )
    
    passenger.name = passenger_data.name
    passenger.id_card = passenger_data.id_card
    passenger.phone = passenger_data.phone
    passenger.passenger_type = passenger_data.passenger_type
    passenger.is_default = passenger_data.is_default
    
    await db.commit()
    
    return {"success": True, "message": "乘客信息更新成功"}


@app.delete("/api/v1/passengers/{passenger_id}")
async def delete_passenger(
    passenger_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除乘客"""
    result = await db.execute(
        select(Passenger).where(
            Passenger.id == passenger_id,
            Passenger.user_id == current_user.id
        )
    )
    passenger = result.scalar_one_or_none()
    
    if not passenger:
        raise HTTPException(status_code=404, detail="乘客不存在")
    
    await db.delete(passenger)
    await db.commit()
    
    return {"success": True, "message": "乘客删除成功"}


# 监控任务API
@app.get("/api/v1/monitor-tasks")
async def list_monitor_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取监控任务列表"""
    result = await db.execute(
        select(MonitorTask)
        .where(MonitorTask.user_id == current_user.id)
        .order_by(desc(MonitorTask.created_at))
    )
    tasks = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "from_station": t.from_station,
                "to_station": t.to_station,
                "train_date": t.train_date,
                "train_numbers": t.train_numbers,
                "seat_types": t.seat_types,
                "poll_interval": t.poll_interval,
                "auto_submit": t.auto_submit,
                "status": t.status,
                "ticket_found": t.ticket_found,
                "last_check_time": t.last_check_time.isoformat() if t.last_check_time else None,
                "runtime_status": monitor_service.get_task_status(t.id),
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tasks
        ]
    }


@app.post("/api/v1/monitor-tasks")
async def create_monitor_task(
    task: MonitorTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建监控任务"""
    new_task = MonitorTask(
        user_id=current_user.id,
        task_name=task.task_name,
        from_station=task.from_station,
        to_station=task.to_station,
        train_date=task.train_date,
        train_numbers=task.train_numbers,
        seat_types=task.seat_types,
        min_price=task.min_price,
        max_price=task.max_price,
        passenger_ids=task.passenger_ids,
        poll_interval=task.poll_interval,
        auto_submit=task.auto_submit,
        max_retries=task.max_retries,
        status="stopped"
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return {
        "success": True,
        "data": {"id": new_task.id},
        "message": "监控任务创建成功"
    }


@app.post("/api/v1/monitor-tasks/{task_id}/start")
async def start_monitor_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """启动监控任务"""
    result = await db.execute(
        select(MonitorTask).where(
            MonitorTask.id == task_id,
            MonitorTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = await monitor_service.start_monitor(task_id, db)
    
    if result.get("success"):
        return {"success": True, "message": result.get("message")}
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@app.post("/api/v1/monitor-tasks/{task_id}/stop")
async def stop_monitor_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """停止监控任务"""
    result = await db.execute(
        select(MonitorTask).where(
            MonitorTask.id == task_id,
            MonitorTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = await monitor_service.stop_monitor(task_id, db)
    
    return {"success": True, "message": result.get("message")}


@app.delete("/api/v1/monitor-tasks/{task_id}")
async def delete_monitor_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除监控任务"""
    # 先停止任务
    await monitor_service.stop_monitor(task_id, db)
    
    result = await db.execute(
        select(MonitorTask).where(
            MonitorTask.id == task_id,
            MonitorTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    await db.delete(task)
    await db.commit()
    
    return {"success": True, "message": "监控任务删除成功"}


# 订单API
@app.get("/api/v1/orders")
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(desc(Order.created_at))
    )
    orders = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "train_number": o.train_number,
                "from_station": o.from_station,
                "to_station": o.to_station,
                "train_date": o.train_date,
                "depart_time": o.depart_time,
                "seat_type": o.seat_type,
                "seat_no": o.seat_no,
                "total_amount": o.total_amount,
                "status": o.status,
                "submit_time": o.submit_time.isoformat() if o.submit_time else None,
                "pay_deadline": o.pay_deadline.isoformat() if o.pay_deadline else None,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in orders
        ]
    }


@app.post("/api/v1/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order.status = "cancelled"
    order.cancel_time = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "订单已取消"}


# 提醒API
@app.get("/api/v1/alerts")
async def list_alerts(
    current_user: User = Depends(get_current_user),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取提醒列表"""
    query = select(AlertRecord).where(AlertRecord.user_id == current_user.id)
    
    if unread_only:
        query = query.where(AlertRecord.is_read == False)
    
    query = query.order_by(desc(AlertRecord.created_at))
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "alert_title": a.alert_title,
                "alert_content": a.alert_content,
                "is_read": a.is_read,
                "read_time": a.read_time.isoformat() if a.read_time else None,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]
    }


@app.post("/api/v1/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记提醒为已读"""
    result = await db.execute(
        select(AlertRecord).where(
            AlertRecord.id == alert_id,
            AlertRecord.user_id == current_user.id
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    alert.is_read = True
    alert.read_time = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "已标记为已读"}


# 测试API
@app.post("/api/v1/test/query-tickets")
async def test_query_tickets(
    from_station: str,
    to_station: str,
    train_date: str,
    current_user: User = Depends(get_current_user)
):
    """测试余票查询接口"""
    result = await http_client.query_tickets(from_station, to_station, train_date)
    return {"success": True, "data": result}


@app.get("/api/v1/test/stations")
async def get_test_stations(current_user: User = Depends(get_current_user)):
    """获取测试站点列表"""
    stations = [
        {"code": "BJP", "name": "北京", "pinyin": "beijing"},
        {"code": "VNP", "name": "北京南", "pinyin": "beijingnan"},
        {"code": "SHH", "name": "上海虹桥", "pinyin": "shanghaihongqiao"},
        {"code": "SHQ", "name": "上海", "pinyin": "shanghai"},
        {"code": "GZQ", "name": "广州南", "pinyin": "guangzhounan"},
        {"code": "SZQ", "name": "深圳北", "pinyin": "shenzhenbei"},
        {"code": "CDW", "name": "成都东", "pinyin": "chengdudong"},
        {"code": "CQW", "name": "重庆北", "pinyin": "chongqingbei"},
        {"code": "WHN", "name": "武汉", "pinyin": "wuhan"},
        {"code": "XAY", "name": "西安北", "pinyin": "xianbei"},
    ]
    return {"success": True, "data": stations}


# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
