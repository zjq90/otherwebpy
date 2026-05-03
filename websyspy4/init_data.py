"""
测试数据初始化脚本
用于在数据库中生成测试数据，包括：
- 管理员账户
- 测试用户
- 产品分类
- 测试产品
- 预约记录
- 通知消息

运行方式：python init_data.py
"""

import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.product import Product
from app.models.reservation import Reservation, ReservationStatus
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.utils.security import get_password_hash
from app.utils.helpers import generate_reservation_no, calculate_rental_days


def init_test_data():
    """
    初始化测试数据
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("开始初始化测试数据...")
        print("=" * 60)
        
        Base.metadata.create_all(bind=engine)
        
        create_admin_user(db)
        
        create_test_users(db)
        
        create_categories(db)
        
        create_products(db)
        
        create_test_reservations(db)
        
        print("=" * 60)
        print("测试数据初始化完成！")
        print("=" * 60)
        print("\n测试账号信息：")
        print("  管理员账号：13800000000，密码：admin123")
        print("  普通用户1：13800000001，密码：123456")
        print("  普通用户2：13800000002，密码：123456")
        print("\n系统访问地址：")
        print("  首页：http://127.0.0.1:8000/")
        print("  登录：http://127.0.0.1:8000/login")
        print("  管理后台：http://127.0.0.1:8000/admin")
        print("=" * 60)
        
    except Exception as e:
        print(f"初始化数据时出错：{e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def create_admin_user(db):
    """
    创建管理员用户
    """
    admin_phone = "13800000000"
    existing_admin = db.query(User).filter(User.phone == admin_phone).first()
    
    if existing_admin:
        print(f"管理员账号 {admin_phone} 已存在，跳过创建")
        return
    
    admin = User(
        phone=admin_phone,
        name="系统管理员",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    print(f"已创建管理员账号：{admin_phone}，密码：admin123")


def create_test_users(db):
    """
    创建测试用户
    """
    test_users = [
        {"phone": "13800000001", "name": "张三", "password": "123456"},
        {"phone": "13800000002", "name": "李四", "password": "123456"},
        {"phone": "13800000003", "name": "王五", "password": "123456"},
    ]
    
    for user_data in test_users:
        existing_user = db.query(User).filter(User.phone == user_data["phone"]).first()
        if existing_user:
            print(f"用户 {user_data['phone']} 已存在，跳过创建")
            continue
        
        user = User(
            phone=user_data["phone"],
            name=user_data["name"],
            password_hash=get_password_hash(user_data["password"]),
            role=UserRole.USER,
            is_verified=True
        )
        db.add(user)
        print(f"已创建测试用户：{user_data['phone']}（{user_data['name']}），密码：{user_data['password']}")
    
    db.commit()


def create_categories(db):
    """
    创建产品分类
    """
    categories_data = [
        {"name": "电子设备", "description": "各类电子产品、数码设备租借", "sort_order": 1},
        {"name": "户外装备", "description": "露营、登山、旅行等户外装备", "sort_order": 2},
        {"name": "摄影器材", "description": "相机、镜头、三脚架等摄影设备", "sort_order": 3},
        {"name": "家居用品", "description": "家具、家电、工具等家居用品", "sort_order": 4},
        {"name": "运动器材", "description": "各类运动健身器材租借", "sort_order": 5},
        {"name": "办公设备", "description": "投影仪、打印机等办公设备", "sort_order": 6},
    ]
    
    for cat_data in categories_data:
        existing_cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing_cat:
            print(f"分类 '{cat_data['name']}' 已存在，跳过创建")
            continue
        
        category = Category(**cat_data)
        db.add(category)
        print(f"已创建分类：{cat_data['name']}")
    
    db.commit()


def create_products(db):
    """
    创建测试产品
    """
    categories = db.query(Category).all()
    cat_map = {cat.name: cat.id for cat in categories}
    
    products_data = [
        {
            "name": "索尼全画幅微单相机 A7M4",
            "description": "索尼最新全画幅微单相机，支持4K 60p视频录制，28-70mm套机镜头",
            "category_name": "摄影器材",
            "daily_rent": 150.00,
            "deposit": 5000.00,
            "stock_quantity": 5,
            "available_quantity": 5,
            "is_hot": True,
            "status": 1
        },
        {
            "name": "大疆无人机 Mavic 3",
            "description": "大疆旗舰级航拍无人机，4/3 CMOS 哈苏相机，支持5.1K视频录制",
            "category_name": "电子设备",
            "daily_rent": 200.00,
            "deposit": 8000.00,
            "stock_quantity": 3,
            "available_quantity": 3,
            "is_hot": True,
            "status": 1
        },
        {
            "name": "露营帐篷 4人",
            "description": "防水防风露营帐篷，自动速开设计，适合家庭露营使用",
            "category_name": "户外装备",
            "daily_rent": 80.00,
            "deposit": 500.00,
            "stock_quantity": 10,
            "available_quantity": 10,
            "is_hot": True,
            "status": 1
        },
        {
            "name": "山地自行车",
            "description": "专业级山地自行车，铝合金车架，变速系统，适合户外骑行",
            "category_name": "运动器材",
            "daily_rent": 50.00,
            "deposit": 1000.00,
            "stock_quantity": 8,
            "available_quantity": 8,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "投影仪 4K",
            "description": "4K超高清投影仪，3000流明亮度，支持无线投屏，适合会议和家庭影院",
            "category_name": "办公设备",
            "daily_rent": 120.00,
            "deposit": 3000.00,
            "stock_quantity": 6,
            "available_quantity": 6,
            "is_hot": True,
            "status": 1
        },
        {
            "name": "露营睡袋",
            "description": "舒适保暖睡袋，适用于-5°C至15°C环境，便携收纳",
            "category_name": "户外装备",
            "daily_rent": 30.00,
            "deposit": 200.00,
            "stock_quantity": 20,
            "available_quantity": 20,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "长焦镜头 70-200mm",
            "description": "佳能专业长焦镜头，f/2.8大光圈，适合人像和体育摄影",
            "category_name": "摄影器材",
            "daily_rent": 100.00,
            "deposit": 3000.00,
            "stock_quantity": 4,
            "available_quantity": 4,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "烧烤炉套装",
            "description": "便携式烧烤炉套装，包含烤架、炭网、烤盘等配件",
            "category_name": "户外装备",
            "daily_rent": 60.00,
            "deposit": 300.00,
            "stock_quantity": 8,
            "available_quantity": 8,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "三脚架 专业级",
            "description": "碳纤维专业三脚架，支持360度云台，承重10kg",
            "category_name": "摄影器材",
            "daily_rent": 40.00,
            "deposit": 800.00,
            "stock_quantity": 10,
            "available_quantity": 10,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "笔记本电脑",
            "description": "MacBook Pro 16寸，M2 Pro芯片，适合移动办公和创意工作",
            "category_name": "电子设备",
            "daily_rent": 150.00,
            "deposit": 6000.00,
            "stock_quantity": 5,
            "available_quantity": 5,
            "is_hot": True,
            "status": 1
        },
        {
            "name": "登山背包 60L",
            "description": "专业级登山背包，透气背负系统，多功能隔层设计",
            "category_name": "户外装备",
            "daily_rent": 40.00,
            "deposit": 400.00,
            "stock_quantity": 12,
            "available_quantity": 12,
            "is_hot": False,
            "status": 1
        },
        {
            "name": "无线麦克风套装",
            "description": "专业无线领夹麦克风，一拖二，适合采访和视频录制",
            "category_name": "电子设备",
            "daily_rent": 60.00,
            "deposit": 1500.00,
            "stock_quantity": 6,
            "available_quantity": 6,
            "is_hot": False,
            "status": 1
        },
    ]
    
    for prod_data in products_data:
        category_name = prod_data.pop("category_name")
        existing_prod = db.query(Product).filter(Product.name == prod_data["name"]).first()
        
        if existing_prod:
            print(f"产品 '{prod_data['name']}' 已存在，跳过创建")
            continue
        
        prod_data["category_id"] = cat_map.get(category_name)
        product = Product(**prod_data)
        db.add(product)
        print(f"已创建产品：{prod_data['name']}（¥{prod_data['daily_rent']}/天）")
    
    db.commit()


def create_test_reservations(db):
    """
    创建测试预约记录
    """
    users = db.query(User).filter(User.role == UserRole.USER).all()
    products = db.query(Product).filter(Product.status == 1, Product.available_quantity > 0).all()
    
    if not users or not products:
        print("没有足够的用户或产品数据，跳过创建预约记录")
        return
    
    today = date.today()
    
    reservation_data_list = [
        {
            "user_index": 0,
            "product_index": 0,
            "start_offset": 1,
            "end_offset": 3,
            "quantity": 1,
            "status": ReservationStatus.PENDING,
            "deposit_paid": False,
            "remark": "周末露营使用"
        },
        {
            "user_index": 0,
            "product_index": 2,
            "start_offset": 2,
            "end_offset": 5,
            "quantity": 2,
            "status": ReservationStatus.PAID,
            "deposit_paid": True,
            "remark": "家庭出游"
        },
        {
            "user_index": 1,
            "product_index": 4,
            "start_offset": -5,
            "end_offset": -3,
            "quantity": 1,
            "status": ReservationStatus.COMPLETED,
            "deposit_paid": True,
            "remark": "公司会议使用"
        },
        {
            "user_index": 1,
            "product_index": 9,
            "start_offset": 3,
            "end_offset": 7,
            "quantity": 1,
            "status": ReservationStatus.CONFIRMED,
            "deposit_paid": False,
            "remark": "出差办公使用"
        },
        {
            "user_index": 2,
            "product_index": 1,
            "start_offset": -10,
            "end_offset": -8,
            "quantity": 1,
            "status": ReservationStatus.COMPLETED,
            "deposit_paid": True,
            "remark": "婚礼拍摄"
        },
    ]
    
    for resv_data in reservation_data_list:
        user_index = resv_data["user_index"] % len(users)
        product_index = resv_data["product_index"] % len(products)
        
        user = users[user_index]
        product = products[product_index]
        
        start_date = today + timedelta(days=resv_data["start_offset"])
        end_date = today + timedelta(days=resv_data["end_offset"])
        
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        
        rental_days = calculate_rental_days(start_date, end_date)
        total_rent = float(product.daily_rent) * rental_days * resv_data["quantity"]
        total_deposit = float(product.deposit) * resv_data["quantity"]
        
        reservation = Reservation(
            reservation_no=generate_reservation_no(),
            user_id=user.id,
            product_id=product.id,
            start_date=start_date,
            end_date=end_date,
            rental_days=rental_days,
            quantity=resv_data["quantity"],
            daily_rent=product.daily_rent,
            total_rent=total_rent,
            deposit=total_deposit,
            deposit_paid=resv_data["deposit_paid"],
            status=resv_data["status"],
            remark=resv_data["remark"]
        )
        
        if resv_data["status"] == ReservationStatus.PAID:
            reservation.deposit_paid_at = datetime.utcnow()
        elif resv_data["status"] == ReservationStatus.PICKED_UP:
            reservation.picked_up_at = datetime.utcnow()
        elif resv_data["status"] == ReservationStatus.RETURNED:
            reservation.picked_up_at = datetime.utcnow() - timedelta(days=3)
            reservation.returned_at = datetime.utcnow()
        elif resv_data["status"] == ReservationStatus.COMPLETED:
            reservation.picked_up_at = datetime.utcnow() - timedelta(days=10)
            reservation.returned_at = datetime.utcnow() - timedelta(days=7)
        
        db.add(reservation)
        
        notification = Notification(
            notification_type=NotificationType.NEW_RESERVATION,
            title="新预约通知",
            content=f"用户 {user.name or user.phone} 创建了新预约，预约单号：{reservation.reservation_no}",
            status=NotificationStatus.UNREAD,
            reservation_id=None,
            sms_sent=False
        )
        db.add(notification)
        
        print(f"已创建预约：{reservation.reservation_no} - {product.name}（用户：{user.name or user.phone}，状态：{resv_data['status'].value}）")
    
    db.commit()


if __name__ == "__main__":
    init_test_data()
