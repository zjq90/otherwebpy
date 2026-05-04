"""
测试数据生成模块
用于生成系统的测试数据，包括会员、商品、优惠券、储物柜等
"""
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import random
import string
from typing import List

from models import (
    Member, Locker, Product, Coupon, CheckIn, 
    LockerUsage, Order, OrderItem, PaymentRecord, RechargeRecord
)


def generate_member_no() -> str:
    """生成会员编号"""
    return f"M{datetime.now().strftime('%Y%m%d')}{''.join(random.choices(string.digits, k=4))}"


def generate_card_no() -> str:
    """生成卡号"""
    return ''.join(random.choices(string.digits, k=16))


def generate_qr_code() -> str:
    """生成二维码内容"""
    return 'QR' + ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_face_data() -> str:
    """生成人脸特征数据（模拟）"""
    return 'face_' + ''.join(random.choices(string.hexdigits, k=32))


def create_test_members(db: Session, count: int = 20) -> List[Member]:
    """
    创建测试会员数据
    
    - **db**: 数据库会话
    - **count**: 创建数量
    """
    membership_types = ["月卡", "季卡", "年卡", "次卡"]
    names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
             "郑一", "王二", "陈三", "褚四", "卫五", "蒋六", "沈七", "韩八",
             "杨九", "朱十", "秦一", "尤二", "许三", "何四", "吕五", "施六"]
    
    members = []
    
    for i in range(count):
        # 随机选择会籍类型
        membership_type = random.choice(membership_types)
        
        # 根据会籍类型设置有效期
        if membership_type == "月卡":
            membership_end = date.today() + timedelta(days=30)
        elif membership_type == "季卡":
            membership_end = date.today() + timedelta(days=90)
        elif membership_type == "年卡":
            membership_end = date.today() + timedelta(days=365)
        else:  # 次卡
            membership_end = date.today() + timedelta(days=180)
        
        # 部分会员设置为过期
        if i % 5 == 0:
            membership_end = date.today() - timedelta(days=random.randint(1, 30))
        
        # 部分会员设置为暂停
        status = "active"
        if i % 7 == 0:
            status = "suspended"
        
        member = Member(
            member_no=generate_member_no(),
            name=names[i % len(names)],
            id_card=''.join(random.choices(string.digits, k=18)),
            phone=f"138{''.join(random.choices(string.digits, k=8))}",
            email=f"user{i+1}@example.com",
            card_no=generate_card_no(),
            qr_code=generate_qr_code(),
            face_data=generate_face_data(),
            membership_type=membership_type,
            membership_start=date.today() - timedelta(days=random.randint(1, 60)),
            membership_end=membership_end,
            balance=random.uniform(0, 2000),
            status=status,
            remarks=f"测试会员 {i+1}"
        )
        db.add(member)
        members.append(member)
    
    db.commit()
    for member in members:
        db.refresh(member)
    
    print(f"✓ 已创建 {len(members)} 个测试会员")
    return members


def create_test_lockers(db: Session, count: int = 30) -> List[Locker]:
    """
    创建测试储物柜数据
    
    - **db**: 数据库会话
    - **count**: 创建数量
    """
    locker_types = ["small", "medium", "large"]
    locations = ["一楼A区", "一楼B区", "二楼A区", "二楼B区"]
    statuses = ["available", "available", "available", "occupied", "maintenance"]
    
    lockers = []
    
    for i in range(count):
        # 生成储物柜编号
        zone = chr(ord('A') + (i // 10))
        num = f"{(i % 10) + 1:03d}"
        locker_no = f"{zone}{num}"
        
        # 随机选择状态（大部分是available）
        status = random.choice(statuses)
        
        locker = Locker(
            locker_no=locker_no,
            location=random.choice(locations),
            locker_type=random.choice(locker_types),
            status=status,
            remarks=f"测试储物柜 {locker_no}"
        )
        db.add(locker)
        lockers.append(locker)
    
    db.commit()
    for locker in lockers:
        db.refresh(locker)
    
    print(f"✓ 已创建 {len(lockers)} 个测试储物柜")
    return lockers


def create_test_products(db: Session, count: int = 15) -> List[Product]:
    """
    创建测试商品数据
    
    - **db**: 数据库会话
    - **count**: 创建数量
    """
    products_data = [
        {"name": "矿泉水", "category": "饮料", "price": 5.0, "cost_price": 2.0, "stock": 100},
        {"name": "运动饮料", "category": "饮料", "price": 8.0, "cost_price": 3.5, "stock": 80},
        {"name": "蛋白棒", "category": "食品", "price": 15.0, "cost_price": 6.0, "stock": 50},
        {"name": "能量胶", "category": "食品", "price": 12.0, "cost_price": 5.0, "stock": 60},
        {"name": "运动毛巾", "category": "周边", "price": 25.0, "cost_price": 10.0, "stock": 30},
        {"name": "瑜伽垫", "category": "周边", "price": 89.0, "cost_price": 35.0, "stock": 20},
        {"name": "健身手套", "category": "周边", "price": 45.0, "cost_price": 18.0, "stock": 25},
        {"name": "蛋白代餐", "category": "食品", "price": 35.0, "cost_price": 15.0, "stock": 40},
        {"name": "咖啡", "category": "饮料", "price": 18.0, "cost_price": 8.0, "stock": 45},
        {"name": "绿茶", "category": "饮料", "price": 10.0, "cost_price": 4.0, "stock": 55},
        {"name": "运动护膝", "category": "周边", "price": 65.0, "cost_price": 25.0, "stock": 15},
        {"name": "蛋白奶昔", "category": "食品", "price": 28.0, "cost_price": 12.0, "stock": 35},
        {"name": "瓶装牛奶", "category": "饮料", "price": 12.0, "cost_price": 5.0, "stock": 50},
        {"name": "坚果包", "category": "食品", "price": 20.0, "cost_price": 8.0, "stock": 40},
        {"name": "背包", "category": "周边", "price": 128.0, "cost_price": 45.0, "stock": 10},
    ]
    
    products = []
    
    for i, pdata in enumerate(products_data[:count]):
        product = Product(
            product_code=f"PRD{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
            name=pdata["name"],
            category=pdata["category"],
            price=pdata["price"],
            cost_price=pdata["cost_price"],
            stock_quantity=pdata["stock"],
            warning_quantity=10,
            status="active",
            description=f"优质{pdata['name']}，品质保证"
        )
        db.add(product)
        products.append(product)
    
    db.commit()
    for product in products:
        db.refresh(product)
    
    print(f"✓ 已创建 {len(products)} 个测试商品")
    return products


def create_test_coupons(db: Session, count: int = 10) -> List[Coupon]:
    """
    创建测试优惠券数据
    
    - **db**: 数据库会话
    - **count**: 创建数量
    """
    coupons_data = [
        {"name": "新用户8折券", "type": "discount", "value": 0.8, "min_amount": 50.0},
        {"name": "满100减20券", "type": "cash", "value": 20.0, "min_amount": 100.0},
        {"name": "满200减50券", "type": "cash", "value": 50.0, "min_amount": 200.0},
        {"name": "会员专享7折券", "type": "discount", "value": 0.7, "min_amount": 100.0},
        {"name": "满50减10券", "type": "cash", "value": 10.0, "min_amount": 50.0},
        {"name": "生日特惠券", "type": "discount", "value": 0.5, "min_amount": 0.0},
        {"name": "周年庆9折券", "type": "discount", "value": 0.9, "min_amount": 0.0},
        {"name": "满300减80券", "type": "cash", "value": 80.0, "min_amount": 300.0},
        {"name": "新人礼包券", "type": "cash", "value": 30.0, "min_amount": 100.0},
        {"name": "赠品券", "type": "gift", "value": 0.0, "min_amount": 50.0},
    ]
    
    coupons = []
    
    for i, cdata in enumerate(coupons_data[:count]):
        # 部分优惠券设置过期时间
        if i % 3 == 0:
            expire_time = datetime.now() + timedelta(days=7)
        elif i % 3 == 1:
            expire_time = datetime.now() + timedelta(days=30)
        else:
            expire_time = datetime.now() + timedelta(days=90)
        
        # 部分优惠券设置为已使用或过期
        status = "available"
        if i % 5 == 0:
            status = "used"
        elif i % 7 == 0:
            status = "expired"
            expire_time = datetime.now() - timedelta(days=1)
        
        coupon = Coupon(
            coupon_code=f"CPN{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
            name=cdata["name"],
            coupon_type=cdata["type"],
            value=cdata["value"],
            min_amount=cdata["min_amount"],
            expire_time=expire_time,
            status=status,
            remarks=f"测试优惠券 {cdata['name']}"
        )
        db.add(coupon)
        coupons.append(coupon)
    
    db.commit()
    for coupon in coupons:
        db.refresh(coupon)
    
    print(f"✓ 已创建 {len(coupons)} 个测试优惠券")
    return coupons


def create_test_checkins(db: Session, members: List[Member], count: int = 50) -> List[CheckIn]:
    """
    创建测试签到记录
    
    - **db**: 数据库会话
    - **members**: 会员列表
    - **count**: 创建数量
    """
    check_in_types = ["card", "qr", "face"]
    statuses = ["success", "success", "success", "failed"]
    
    checkins = []
    
    active_members = [m for m in members if m.status == "active"]
    
    for i in range(count):
        member = random.choice(active_members) if active_members else random.choice(members)
        check_in_type = random.choice(check_in_types)
        status = random.choice(statuses)
        
        # 随机生成签到时间（最近30天内）
        check_in_time = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        fail_reason = None
        verification_details = {}
        
        if status == "failed":
            fail_reasons = ["会籍已过期", "会员状态异常", "验证失败"]
            fail_reason = random.choice(fail_reasons)
        
        if check_in_type == "card":
            verification_details["card_no"] = member.card_no
        elif check_in_type == "qr":
            verification_details["qr_code"] = member.qr_code
        elif check_in_type == "face":
            verification_details["face_similarity"] = round(random.uniform(0.7, 1.0), 2)
        
        checkin = CheckIn(
            member_id=member.id,
            check_in_type=check_in_type,
            check_in_time=check_in_time,
            status=status,
            fail_reason=fail_reason,
            verification_details=str(verification_details),
            device_no=f"DEV{random.randint(1, 5)}",
            remarks=f"测试签到记录 {i+1}"
        )
        db.add(checkin)
        checkins.append(checkin)
    
    db.commit()
    for checkin in checkins:
        db.refresh(checkin)
    
    print(f"✓ 已创建 {len(checkins)} 条测试签到记录")
    return checkins


def generate_all_test_data(db: Session):
    """
    生成所有测试数据
    
    - **db**: 数据库会话
    """
    print("=" * 50)
    print("开始生成测试数据...")
    print("=" * 50)
    
    # 1. 创建会员
    members = create_test_members(db, 20)
    
    # 2. 创建储物柜
    lockers = create_test_lockers(db, 30)
    
    # 3. 创建商品
    products = create_test_products(db, 15)
    
    # 4. 创建优惠券
    coupons = create_test_coupons(db, 10)
    
    # 5. 创建签到记录
    checkins = create_test_checkins(db, members, 50)
    
    print("=" * 50)
    print("测试数据生成完成！")
    print("=" * 50)
    
    return {
        "members": members,
        "lockers": lockers,
        "products": products,
        "coupons": coupons,
        "checkins": checkins
    }
