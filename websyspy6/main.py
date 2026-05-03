"""
租借系统主应用入口
基于FastAPI + SQLite + Bootstrap V5的租借管理系统
"""
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db, init_db
from models import User, Item, Rental, Reminder, CollectionOrder, SMSLog
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    ItemCreate, ItemUpdate, ItemResponse,
    RentalCreate, RentalUpdate, RentalResponse, RentalDetailResponse,
    ReminderResponse, CollectionOrderResponse, SMSLogResponse,
    Token, APIResponse, PaginatedResponse
)
from utils import get_password_hash, verify_password, generate_rental_no, calculate_rental_total
from reminder_service import ReminderService
from sms_service import SMSService
from config import PAGE_SIZE

# 创建FastAPI应用实例
app = FastAPI(
    title="租借管理系统",
    description="基于FastAPI的租借管理系统，支持自动提醒、短信通知、押金自动扣除等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保static和templates目录存在
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置模板引擎
templates = Jinja2Templates(directory=templates_dir)


# 应用启动时初始化数据库
@app.on_event("startup")
def startup_event():
    """应用启动事件"""
    init_db()
    print("数据库初始化完成！")


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """首页 - 重定向到登录页面"""
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """仪表盘页面"""
    # 获取统计数据
    total_users = db.query(User).count()
    total_items = db.query(Item).count()
    active_rentals = db.query(Rental).filter(Rental.status == 'active').count()
    overdue_rentals = db.query(Rental).filter(Rental.status == 'overdue').count()
    pending_reminders = db.query(Reminder).filter(
        Reminder.reminder_type == 'platform',
        Reminder.is_read == False
    ).count()
    pending_orders = db.query(CollectionOrder).filter(
        CollectionOrder.status == 'pending'
    ).count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": {
            "total_users": total_users,
            "total_items": total_items,
            "active_rentals": active_rentals,
            "overdue_rentals": overdue_rentals,
            "pending_reminders": pending_reminders,
            "pending_orders": pending_orders
        }
    })


@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request):
    """用户管理页面"""
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/items", response_class=HTMLResponse)
def items_page(request: Request):
    """物品管理页面"""
    return templates.TemplateResponse("items.html", {"request": request})


@app.get("/rentals", response_class=HTMLResponse)
def rentals_page(request: Request):
    """租借记录页面"""
    return templates.TemplateResponse("rentals.html", {"request": request})


@app.get("/reminders", response_class=HTMLResponse)
def reminders_page(request: Request):
    """提醒记录页面"""
    return templates.TemplateResponse("reminders.html", {"request": request})


@app.get("/collection-orders", response_class=HTMLResponse)
def collection_orders_page(request: Request):
    """催还订单页面"""
    return templates.TemplateResponse("collection_orders.html", {"request": request})


@app.get("/sms-logs", response_class=HTMLResponse)
def sms_logs_page(request: Request):
    """短信日志页面"""
    return templates.TemplateResponse("sms_logs.html", {"request": request})


@app.get("/test-reminder", response_class=HTMLResponse)
def test_reminder_page(request: Request):
    """提醒功能测试页面"""
    return templates.TemplateResponse("test_reminder.html", {"request": request})


# ==================== API路由 - 用户管理 ====================

@app.post("/api/users/", response_model=APIResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return APIResponse(code=400, message="用户名已存在")
    
    # 检查手机号是否已存在
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        return APIResponse(code=400, message="手机号已被注册")
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        phone=user_data.phone,
        email=user_data.email,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return APIResponse(
        code=200,
        message="用户创建成功",
        data={"user_id": new_user.id}
    )


@app.get("/api/users/", response_model=PaginatedResponse)
def get_users(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    keyword: str = None,
    role: str = None,
    db: Session = Depends(get_db)
):
    """获取用户列表（分页）"""
    query = db.query(User)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword),
                User.phone.contains(keyword)
            )
        )
    
    # 角色筛选
    if role:
        query = query.filter(User.role == role)
    
    # 获取总数
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    # 分页查询
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [UserResponse.from_orm(u).dict() for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@app.get("/api/users/{user_id}", response_model=APIResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    return APIResponse(
        code=200,
        message="success",
        data={"user": UserResponse.from_orm(user).dict()}
    )


@app.put("/api/users/{user_id}", response_model=APIResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    # 更新字段
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    return APIResponse(code=200, message="用户更新成功")


@app.delete("/api/users/{user_id}", response_model=APIResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    # 检查是否有活跃的租借记录
    active_rentals = db.query(Rental).filter(
        Rental.user_id == user_id,
        or_(Rental.status == 'active', Rental.status == 'overdue')
    ).count()
    if active_rentals > 0:
        return APIResponse(code=400, message="该用户有未完成的租借记录，无法删除")
    
    db.delete(user)
    db.commit()
    return APIResponse(code=200, message="用户删除成功")


# ==================== API路由 - 物品管理 ====================

@app.post("/api/items/", response_model=APIResponse)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """创建新物品"""
    new_item = Item(
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        daily_rent=item_data.daily_rent,
        deposit=item_data.deposit,
        stock=item_data.stock,
        available=item_data.stock,
        image_url=item_data.image_url
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return APIResponse(
        code=200,
        message="物品创建成功",
        data={"item_id": new_item.id}
    )


@app.get("/api/items/", response_model=PaginatedResponse)
def get_items(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    keyword: str = None,
    category: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取物品列表（分页）"""
    query = db.query(Item)
    
    if keyword:
        query = query.filter(
            or_(Item.name.contains(keyword), Item.description.contains(keyword))
        )
    if category:
        query = query.filter(Item.category == category)
    if status:
        query = query.filter(Item.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    items = query.order_by(Item.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [ItemResponse.from_orm(i).dict() for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@app.get("/api/items/{item_id}", response_model=APIResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """获取单个物品详情"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return APIResponse(code=404, message="物品不存在")
    
    return APIResponse(
        code=200,
        message="success",
        data={"item": ItemResponse.from_orm(item).dict()}
    )


@app.put("/api/items/{item_id}", response_model=APIResponse)
def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    """更新物品信息"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return APIResponse(code=404, message="物品不存在")
    
    update_data = item_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    db.commit()
    return APIResponse(code=200, message="物品更新成功")


@app.delete("/api/items/{item_id}", response_model=APIResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """删除物品"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return APIResponse(code=404, message="物品不存在")
    
    # 检查是否有活跃的租借记录
    active_rentals = db.query(Rental).filter(
        Rental.item_id == item_id,
        or_(Rental.status == 'active', Rental.status == 'overdue')
    ).count()
    if active_rentals > 0:
        return APIResponse(code=400, message="该物品有未完成的租借记录，无法删除")
    
    db.delete(item)
    db.commit()
    return APIResponse(code=200, message="物品删除成功")


# ==================== API路由 - 租借记录管理 ====================

@app.post("/api/rentals/", response_model=APIResponse)
def create_rental(rental_data: RentalCreate, db: Session = Depends(get_db)):
    """创建新租借记录"""
    # 验证用户
    user = db.query(User).filter(User.id == rental_data.user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    # 验证物品
    item = db.query(Item).filter(Item.id == rental_data.item_id).first()
    if not item:
        return APIResponse(code=404, message="物品不存在")
    
    # 检查库存
    if item.available < rental_data.quantity:
        return APIResponse(code=400, message=f"物品库存不足，当前可用：{item.available}")
    
    # 检查日期
    if rental_data.due_date < rental_data.start_date:
        return APIResponse(code=400, message="应归还日期不能早于租借开始日期")
    
    # 计算押金和租金
    deposit_amount = item.deposit * rental_data.quantity
    daily_rent = item.daily_rent
    
    # 生成租借单号
    rental_no = generate_rental_no()
    
    # 创建租借记录
    new_rental = Rental(
        rental_no=rental_no,
        user_id=rental_data.user_id,
        item_id=rental_data.item_id,
        quantity=rental_data.quantity,
        start_date=rental_data.start_date,
        due_date=rental_data.due_date,
        daily_rent=daily_rent,
        deposit_amount=deposit_amount,
        status='active',
        remark=rental_data.remark
    )
    
    # 更新物品可用数量
    item.available -= rental_data.quantity
    
    db.add(new_rental)
    db.commit()
    db.refresh(new_rental)
    
    return APIResponse(
        code=200,
        message="租借创建成功",
        data={"rental_id": new_rental.id, "rental_no": rental_no}
    )


@app.get("/api/rentals/", response_model=PaginatedResponse)
def get_rentals(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    keyword: str = None,
    status: str = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """获取租借记录列表（分页）"""
    query = db.query(Rental)
    
    if keyword:
        # 关联用户和物品搜索
        users = db.query(User.id).filter(
            or_(User.username.contains(keyword), User.real_name.contains(keyword))
        ).all()
        user_ids = [u.id for u in users]
        
        items = db.query(Item.id).filter(Item.name.contains(keyword)).all()
        item_ids = [i.id for i in items]
        
        query = query.filter(
            or_(
                Rental.rental_no.contains(keyword),
                Rental.user_id.in_(user_ids) if user_ids else False,
                Rental.item_id.in_(item_ids) if item_ids else False
            )
        )
    
    if status:
        query = query.filter(Rental.status == status)
    if user_id:
        query = query.filter(Rental.user_id == user_id)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    rentals = query.order_by(Rental.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [RentalResponse.from_orm(r).dict() for r in rentals],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@app.get("/api/rentals/{rental_id}", response_model=APIResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    """获取单个租借记录详情（包含关联信息）"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        return APIResponse(code=404, message="租借记录不存在")
    
    # 关联查询用户和物品
    user = db.query(User).filter(User.id == rental.user_id).first()
    item = db.query(Item).filter(Item.id == rental.item_id).first()
    
    rental_dict = RentalResponse.from_orm(rental).dict()
    if user:
        rental_dict['renter'] = UserResponse.from_orm(user).dict()
    if item:
        rental_dict['item'] = ItemResponse.from_orm(item).dict()
    
    return APIResponse(
        code=200,
        message="success",
        data={"rental": rental_dict}
    )


@app.put("/api/rentals/{rental_id}", response_model=APIResponse)
def update_rental(rental_id: int, rental_data: RentalUpdate, db: Session = Depends(get_db)):
    """更新租借记录（主要用于归还）"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        return APIResponse(code=404, message="租借记录不存在")
    
    # 如果是归还操作
    if rental_data.actual_return_date:
        # 计算实际租金
        end_date = rental_data.actual_return_date
        total_rent = calculate_rental_total(
            rental.start_date, end_date, rental.daily_rent, rental.quantity
        )
        rental.total_rent = total_rent
        rental.actual_return_date = end_date
        rental.status = 'returned'
        
        # 退还物品库存
        item = db.query(Item).filter(Item.id == rental.item_id).first()
        if item:
            item.available += rental.quantity
        
        # 发送归还确认短信
        renter = db.query(User).filter(User.id == rental.user_id).first()
        if renter and renter.phone:
            sms_service = SMSService(db)
            sms_service.send_return_confirm(
                phone=renter.phone,
                renter_name=renter.real_name or renter.username,
                item_name=item.name if item else '物品',
                return_date=end_date.strftime('%Y-%m-%d')
            )
        
        # 退还押金（如果还没扣除）
        if rental.deposit_status == 'paid':
            rental.deposit_status = 'refunded'
    
    # 更新其他字段
    update_data = rental_data.dict(exclude_unset=True, exclude={'actual_return_date'})
    for key, value in update_data.items():
        setattr(rental, key, value)
    
    db.commit()
    return APIResponse(code=200, message="租借记录更新成功")


# ==================== API路由 - 提醒管理 ====================

@app.get("/api/reminders/", response_model=PaginatedResponse)
def get_reminders(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    user_id: int = None,
    reminder_type: str = None,
    is_read: bool = None,
    db: Session = Depends(get_db)
):
    """获取提醒列表"""
    query = db.query(Reminder)
    
    if user_id:
        query = query.filter(Reminder.user_id == user_id)
    if reminder_type:
        query = query.filter(Reminder.reminder_type == reminder_type)
    if is_read is not None:
        query = query.filter(Reminder.is_read == is_read)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    reminders = query.order_by(Reminder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [ReminderResponse.from_orm(r).dict() for r in reminders],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@app.put("/api/reminders/{reminder_id}/read", response_model=APIResponse)
def mark_reminder_read(reminder_id: int, db: Session = Depends(get_db)):
    """标记提醒为已读"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        return APIResponse(code=404, message="提醒不存在")
    
    reminder.is_read = True
    db.commit()
    return APIResponse(code=200, message="标记已读成功")


@app.post("/api/reminders/trigger", response_model=APIResponse)
def trigger_reminders(db: Session = Depends(get_db)):
    """手动触发提醒检查（用于测试）"""
    reminder_service = ReminderService(db)
    stats = reminder_service.check_and_generate_reminders()
    
    return APIResponse(
        code=200,
        message="提醒触发完成",
        data=stats
    )


# ==================== API路由 - 催还订单管理 ====================

@app.get("/api/collection-orders/", response_model=PaginatedResponse)
def get_collection_orders(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    status: str = None,
    is_urgent: bool = None,
    db: Session = Depends(get_db)
):
    """获取催还订单列表"""
    query = db.query(CollectionOrder)
    
    if status:
        query = query.filter(CollectionOrder.status == status)
    if is_urgent is not None:
        query = query.filter(CollectionOrder.is_urgent == is_urgent)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    orders = query.order_by(CollectionOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [CollectionOrderResponse.from_orm(o).dict() for o in orders],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@app.put("/api/collection-orders/{order_id}/resolve", response_model=APIResponse)
def resolve_collection_order(
    order_id: int,
    remark: str = Form(None),
    db: Session = Depends(get_db)
):
    """处理催还订单（标记为已解决）"""
    order = db.query(CollectionOrder).filter(CollectionOrder.id == order_id).first()
    if not order:
        return APIResponse(code=404, message="催还订单不存在")
    
    order.status = 'resolved'
    order.handled_at = datetime.now()
    if remark:
        order.remark = remark
    
    db.commit()
    return APIResponse(code=200, message="催还订单已处理")


# ==================== API路由 - 短信日志 ====================

@app.get("/api/sms-logs/", response_model=PaginatedResponse)
def get_sms_logs(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    phone: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取短信日志列表"""
    query = db.query(SMSLog)
    
    if phone:
        query = query.filter(SMSLog.phone.contains(phone))
    if status:
        query = query.filter(SMSLog.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    logs = query.order_by(SMSLog.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PaginatedResponse(
        data={
            "items": [SMSLogResponse.from_orm(l).dict() for l in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


# ==================== API路由 - 测试功能 ====================

@app.post("/api/test/generate-test-data", response_model=APIResponse)
def generate_test_data(db: Session = Depends(get_db)):
    """生成测试数据"""
    from test_data import generate_all_test_data
    result = generate_all_test_data(db)
    return APIResponse(code=200, message="测试数据生成完成", data=result)


@app.post("/api/test/send-sms", response_model=APIResponse)
def test_send_sms(phone: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    """测试短信发送"""
    sms_service = SMSService(db)
    result = sms_service.send_sms(
        phone=phone,
        template_code='TEST',
        content=content
    )
    return APIResponse(
        code=200 if result['success'] else 500,
        message=result['message'],
        data=result.get('data')
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
