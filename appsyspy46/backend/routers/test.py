from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random

from database import get_db, init_db
from models import User, Order, OrderLog, Withdrawal
from schemas import OrderStatus
from utils import get_password_hash, generate_order_no

router = APIRouter(prefix="/api/test", tags=["测试数据"])


@router.post("/init-db", summary="初始化数据库")
async def initialize_database():
    """
    初始化数据库表结构
    """
    init_db()
    return {"message": "数据库初始化成功"}


@router.post("/create-test-users", summary="创建测试用户")
async def create_test_users(db: Session = Depends(get_db)):
    """
    创建测试回收人员用户
    """
    test_users = [
        {
            "username": "collector1",
            "password": "123456",
            "real_name": "张三",
            "phone": "13800138001",
            "id_card": "110101199001011234"
        },
        {
            "username": "collector2",
            "password": "123456",
            "real_name": "李四",
            "phone": "13800138002",
            "id_card": "110101199002022345"
        },
        {
            "username": "collector3",
            "password": "123456",
            "real_name": "王五",
            "phone": "13800138003",
            "id_card": "110101199003033456"
        }
    ]
    
    created_users = []
    for user_data in test_users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            new_user = User(
                username=user_data["username"],
                password_hash=get_password_hash(user_data["password"]),
                real_name=user_data["real_name"],
                phone=user_data["phone"],
                id_card=user_data["id_card"],
                is_verified=True,
                total_orders=0,
                total_weight=0.0,
                total_income=0.0
            )
            db.add(new_user)
            created_users.append(user_data["username"])
    
    db.commit()
    
    return {
        "message": "测试用户创建成功",
        "created_users": created_users,
        "default_password": "123456"
    }


@router.post("/create-test-orders", summary="创建测试订单")
async def create_test_orders(
    count: int = 10,
    db: Session = Depends(get_db)
):
    """
    创建测试订单
    - count: 创建订单数量
    """
    user_addresses = [
        {
            "user_name": "赵先生",
            "user_phone": "13900139001",
            "address": "北京市朝阳区建国路88号SOHO现代城A座1001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "latitude": 39.92,
            "longitude": 116.46
        },
        {
            "user_name": "钱女士",
            "user_phone": "13900139002",
            "address": "北京市海淀区中关村大街1号科技大厦B座502",
            "province": "北京市",
            "city": "北京市",
            "district": "海淀区",
            "latitude": 39.98,
            "longitude": 116.31
        },
        {
            "user_name": "孙先生",
            "user_phone": "13900139003",
            "address": "北京市西城区西单北大街120号大悦城写字楼15层",
            "province": "北京市",
            "city": "北京市",
            "district": "西城区",
            "latitude": 39.91,
            "longitude": 116.37
        },
        {
            "user_name": "李女士",
            "user_phone": "13900139004",
            "address": "北京市东城区王府井大街88号银泰中心C座2001",
            "province": "北京市",
            "city": "北京市",
            "district": "东城区",
            "latitude": 39.91,
            "longitude": 116.41
        },
        {
            "user_name": "周先生",
            "user_phone": "13900139005",
            "address": "北京市丰台区南三环西路16号首地大峡谷写字楼8层",
            "province": "北京市",
            "city": "北京市",
            "district": "丰台区",
            "latitude": 39.85,
            "longitude": 116.35
        }
    ]
    
    clothing_types_options = ["上衣,裤子", "外套,鞋子", "裙子,包包", "上衣,裤子,外套", "其他"]
    
    created_orders = []
    for i in range(count):
        addr = random.choice(user_addresses)
        
        status_choices = [OrderStatus.PENDING.value, OrderStatus.ACCEPTED.value, OrderStatus.COMPLETED.value]
        weights = [0.5, 0.3, 0.2]
        order_status = random.choices(status_choices, weights=weights)[0]
        
        estimated_weight = round(random.uniform(2.0, 15.0), 1)
        estimated_quantity = random.randint(3, 20)
        
        new_order = Order(
            order_no=generate_order_no(),
            user_name=addr["user_name"],
            user_phone=addr["user_phone"],
            address=addr["address"],
            province=addr["province"],
            city=addr["city"],
            district=addr["district"],
            latitude=addr["latitude"] + random.uniform(-0.02, 0.02),
            longitude=addr["longitude"] + random.uniform(-0.02, 0.02),
            clothing_types=random.choice(clothing_types_options),
            estimated_weight=estimated_weight,
            estimated_quantity=estimated_quantity,
            description="家里闲置衣物需要回收",
            status=order_status,
            created_at=datetime.now() - timedelta(hours=random.randint(1, 72))
        )
        
        db.add(new_order)
        db.flush()
        
        log = OrderLog(
            order_id=new_order.id,
            operator_type="user",
            action="create_order",
            description="用户创建回收订单"
        )
        db.add(log)
        
        created_orders.append({
            "order_no": new_order.order_no,
            "status": order_status
        })
    
    db.commit()
    
    return {
        "message": f"成功创建 {len(created_orders)} 条测试订单",
        "orders": created_orders
    }


@router.post("/create-all-test-data", summary="创建所有测试数据")
async def create_all_test_data(db: Session = Depends(get_db)):
    """
    创建所有测试数据（用户+订单）
    """
    init_db()
    
    users_result = await create_test_users(db)
    orders_result = await create_test_orders(count=15, db=db)
    
    return {
        "message": "所有测试数据创建成功",
        "users": users_result,
        "orders": orders_result
    }


@router.get("/overview", summary="获取数据概览")
async def get_data_overview(db: Session = Depends(get_db)):
    """
    获取数据库数据概览
    """
    user_count = db.query(User).count()
    order_count = db.query(Order).count()
    pending_count = db.query(Order).filter(Order.status == OrderStatus.PENDING.value).count()
    accepted_count = db.query(Order).filter(Order.status == OrderStatus.ACCEPTED.value).count()
    completed_count = db.query(Order).filter(Order.status == OrderStatus.COMPLETED.value).count()
    
    return {
        "users": user_count,
        "orders": {
            "total": order_count,
            "pending": pending_count,
            "accepted": accepted_count,
            "completed": completed_count
        }
    }


@router.delete("/clear-all", summary="清空所有数据")
async def clear_all_data(db: Session = Depends(get_db)):
    """
    清空所有测试数据（谨慎使用）
    """
    db.query(OrderLog).delete()
    db.query(Order).delete()
    db.query(Withdrawal).delete()
    db.query(User).delete()
    db.commit()
    
    return {"message": "所有数据已清空"}
