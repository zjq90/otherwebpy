"""
测试数据生成模块
用于生成系统测试所需的各类测试数据，包括：
1. 用户数据（管理员、工作人员、租借人员）
2. 物品数据
3. 租借记录数据（包含各种状态）
4. 用于测试提醒功能的特殊场景数据
"""
from datetime import datetime, date, timedelta
from typing import Dict, List
import random
import string
from sqlalchemy.orm import Session

from models import User, Item, Rental, Reminder, CollectionOrder, SMSLog
from utils import get_password_hash, generate_rental_no


# 预设的测试数据
TEST_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "real_name": "系统管理员",
        "phone": "13800138000",
        "email": "admin@example.com",
        "role": "admin",
        "balance": 1000.0
    },
    {
        "username": "staff1",
        "password": "staff123",
        "real_name": "张经理",
        "phone": "13800138001",
        "email": "staff1@example.com",
        "role": "staff",
        "balance": 500.0
    },
    {
        "username": "staff2",
        "password": "staff123",
        "real_name": "李店员",
        "phone": "13800138002",
        "email": "staff2@example.com",
        "role": "staff",
        "balance": 300.0
    },
    {
        "username": "renter1",
        "password": "renter123",
        "real_name": "王小明",
        "phone": "13900139001",
        "email": "renter1@example.com",
        "role": "renter",
        "balance": 2000.0
    },
    {
        "username": "renter2",
        "password": "renter123",
        "real_name": "赵小红",
        "phone": "13900139002",
        "email": "renter2@example.com",
        "role": "renter",
        "balance": 1500.0
    },
    {
        "username": "renter3",
        "password": "renter123",
        "real_name": "孙小刚",
        "phone": "13900139003",
        "email": "renter3@example.com",
        "role": "renter",
        "balance": 800.0
    },
    {
        "username": "renter4",
        "password": "renter123",
        "real_name": "周小华",
        "phone": "13900139004",
        "email": "renter4@example.com",
        "role": "renter",
        "balance": 3000.0
    }
]

TEST_ITEMS = [
    {
        "name": "索尼A7M4全画幅相机",
        "description": "专业全画幅微单相机，适合专业摄影和视频拍摄",
        "category": "摄影器材",
        "daily_rent": 150.0,
        "deposit": 5000.0,
        "stock": 3,
        "available": 3
    },
    {
        "name": "佳能24-70mm F2.8镜头",
        "description": "专业级标准变焦镜头，大光圈恒定",
        "category": "摄影器材",
        "daily_rent": 80.0,
        "deposit": 3000.0,
        "stock": 2,
        "available": 2
    },
    {
        "name": "DJI Mavic 3无人机",
        "description": "专业航拍无人机，4/3 CMOS 哈苏相机",
        "category": "无人机",
        "daily_rent": 200.0,
        "deposit": 8000.0,
        "stock": 2,
        "available": 2
    },
    {
        "name": "智云稳定器Weebill 3",
        "description": "专业相机稳定器，支持横竖拍切换",
        "category": "摄影配件",
        "daily_rent": 50.0,
        "deposit": 1000.0,
        "stock": 5,
        "available": 5
    },
    {
        "name": "神牛闪光灯AD200",
        "description": "口袋便携闪光灯，TTL自动测光",
        "category": "摄影配件",
        "daily_rent": 40.0,
        "deposit": 800.0,
        "stock": 4,
        "available": 4
    },
    {
        "name": "罗德Wireless GO II麦克风",
        "description": "无线领夹麦克风，双通道录音",
        "category": "音频设备",
        "daily_rent": 30.0,
        "deposit": 500.0,
        "stock": 6,
        "available": 6
    },
    {
        "name": "苹果MacBook Pro 16寸",
        "description": "M2 Pro芯片，专业视频剪辑工作站",
        "category": "电脑设备",
        "daily_rent": 120.0,
        "deposit": 6000.0,
        "stock": 2,
        "available": 2
    },
    {
        "name": "Switch OLED游戏机",
        "description": "任天堂最新款游戏主机，含2款热门游戏",
        "category": "游戏设备",
        "daily_rent": 25.0,
        "deposit": 2000.0,
        "stock": 8,
        "available": 8
    },
    {
        "name": "索尼PS5游戏机",
        "description": "PlayStation 5次世代游戏主机",
        "category": "游戏设备",
        "daily_rent": 35.0,
        "deposit": 3000.0,
        "stock": 4,
        "available": 4
    },
    {
        "name": "露营帐篷4人套装",
        "description": "专业户外露营帐篷，含睡袋、防潮垫",
        "category": "户外装备",
        "daily_rent": 60.0,
        "deposit": 1000.0,
        "stock": 5,
        "available": 5
    }
]


def generate_random_phone() -> str:
    """
    生成随机手机号
    
    Returns:
        str: 随机手机号
    """
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices(string.digits, k=8))
    return prefix + suffix


def generate_random_name() -> str:
    """
    生成随机姓名
    
    Returns:
        str: 随机姓名
    """
    surnames = ['张', '王', '李', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
    names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
             '洋', '勇', '艳', '杰', '涛', '明', '超', '秀兰', '霞', '平',
             '刚', '桂英', '文', '华', '玲', '辉', '鑫', '斌', '波', '宇']
    surname = random.choice(surnames)
    name = random.choice(names)
    if random.random() < 0.5:
        name += random.choice(names)
    return surname + name


def create_test_users(db: Session, count: int = 10) -> List[User]:
    """
    创建测试用户
    
    Args:
        db: 数据库会话
        count: 额外创建的普通用户数量
        
    Returns:
        List[User]: 创建的用户列表
    """
    created_users = []
    
    # 先创建预设的测试用户
    for user_data in TEST_USERS:
        existing = db.query(User).filter(User.username == user_data['username']).first()
        if existing:
            created_users.append(existing)
            continue
        
        user = User(
            username=user_data['username'],
            password=get_password_hash(user_data['password']),
            real_name=user_data['real_name'],
            phone=user_data['phone'],
            email=user_data['email'],
            role=user_data['role'],
            balance=user_data['balance'],
            status='active'
        )
        db.add(user)
        created_users.append(user)
    
    # 创建额外的随机用户
    for i in range(count):
        username = f"user_{datetime.now().strftime('%m%d')}_{i+1:03d}"
        phone = generate_random_phone()
        
        # 确保手机号唯一
        while db.query(User).filter(User.phone == phone).first():
            phone = generate_random_phone()
        
        user = User(
            username=username,
            password=get_password_hash('123456'),
            real_name=generate_random_name(),
            phone=phone,
            email=f"{username}@example.com",
            role='renter',
            balance=random.uniform(100, 5000),
            status='active'
        )
        db.add(user)
        created_users.append(user)
    
    db.flush()
    return created_users


def create_test_items(db: Session) -> List[Item]:
    """
    创建测试物品
    
    Args:
        db: 数据库会话
        
    Returns:
        List[Item]: 创建的物品列表
    """
    created_items = []
    
    for item_data in TEST_ITEMS:
        existing = db.query(Item).filter(Item.name == item_data['name']).first()
        if existing:
            created_items.append(existing)
            continue
        
        item = Item(
            name=item_data['name'],
            description=item_data['description'],
            category=item_data['category'],
            daily_rent=item_data['daily_rent'],
            deposit=item_data['deposit'],
            stock=item_data['stock'],
            available=item_data['available'],
            status='available'
        )
        db.add(item)
        created_items.append(item)
    
    db.flush()
    return created_items


def create_test_rentals(db: Session, users: List[User], items: List[Item]) -> Dict:
    """
    创建测试租借记录
    包含各种状态：正常租借中、即将到期、已逾期1天、已逾期2天、已逾期3天以上、已归还
    
    Args:
        db: 数据库会话
        users: 用户列表
        items: 物品列表
        
    Returns:
        Dict: 各类租借记录的统计
    """
    stats = {
        'active': 0,
        'due_soon': 0,
        'overdue_1d': 0,
        'overdue_2d': 0,
        'overdue_3d_plus': 0,
        'returned': 0
    }
    
    today = date.today()
    renter_users = [u for u in users if u.role == 'renter']
    available_items = [i for i in items if i.available > 0]
    
    if not renter_users or not available_items:
        return stats
    
    # 1. 创建正常租借中（还有几天才到期）
    for i in range(3):
        renter = random.choice(renter_users)
        item = random.choice(available_items)
        if item.available < 1:
            continue
        
        start_date = today - timedelta(days=random.randint(1, 5))
        due_date = today + timedelta(days=random.randint(3, 7))
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=0.0,
            deposit_status='paid',
            status='active'
        )
        db.add(rental)
        item.available -= 1
        stats['active'] += 1
    
    # 2. 创建即将到期（明天到期）
    for i in range(2):
        renter = random.choice(renter_users)
        item = random.choice(available_items)
        if item.available < 1:
            continue
        
        start_date = today - timedelta(days=random.randint(2, 5))
        due_date = today + timedelta(days=1)
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=0.0,
            deposit_status='paid',
            status='active'
        )
        db.add(rental)
        item.available -= 1
        stats['due_soon'] += 1
    
    # 3. 创建逾期1天
    for i in range(2):
        renter = random.choice(renter_users)
        item = random.choice(available_items)
        if item.available < 1:
            continue
        
        start_date = today - timedelta(days=random.randint(5, 10))
        due_date = today - timedelta(days=1)
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=0.0,
            deposit_status='paid',
            status='overdue'
        )
        db.add(rental)
        item.available -= 1
        stats['overdue_1d'] += 1
    
    # 4. 创建逾期2天
    for i in range(2):
        renter = random.choice(renter_users)
        item = random.choice(available_items)
        if item.available < 1:
            continue
        
        start_date = today - timedelta(days=random.randint(6, 12))
        due_date = today - timedelta(days=2)
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=0.0,
            deposit_status='paid',
            status='overdue'
        )
        db.add(rental)
        item.available -= 1
        stats['overdue_2d'] += 1
    
    # 5. 创建逾期3天以上（用于测试押金扣除）
    for i in range(2):
        renter = random.choice(renter_users)
        item = random.choice(available_items)
        if item.available < 1:
            continue
        
        start_date = today - timedelta(days=random.randint(10, 20))
        due_date = today - timedelta(days=random.randint(3, 7))
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=0.0,
            deposit_status='paid',
            status='overdue'
        )
        db.add(rental)
        item.available -= 1
        stats['overdue_3d_plus'] += 1
    
    # 6. 创建已归还的记录
    for i in range(3):
        renter = random.choice(renter_users)
        item = random.choice(items)
        
        start_date = today - timedelta(days=random.randint(10, 30))
        due_date = today - timedelta(days=random.randint(5, 8))
        actual_return = today - timedelta(days=random.randint(1, 4))
        
        days_rented = (actual_return - start_date).days + 1
        total_rent = days_rented * item.daily_rent * 1
        
        rental = Rental(
            rental_no=generate_rental_no(),
            user_id=renter.id,
            item_id=item.id,
            quantity=1,
            start_date=start_date,
            due_date=due_date,
            actual_return_date=actual_return,
            daily_rent=item.daily_rent,
            deposit_amount=item.deposit,
            total_rent=total_rent,
            deposit_status='refunded',
            status='returned'
        )
        db.add(rental)
        stats['returned'] += 1
    
    db.flush()
    return stats


def generate_all_test_data(db: Session) -> Dict:
    """
    生成所有测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        Dict: 生成结果统计
    """
    result = {
        'success': True,
        'message': '测试数据生成成功',
        'data': {
            'users': 0,
            'items': 0,
            'rentals': {},
            'total_rentals': 0
        }
    }
    
    try:
        # 1. 创建用户
        users = create_test_users(db, count=5)
        result['data']['users'] = len(users)
        
        # 2. 创建物品
        items = create_test_items(db)
        result['data']['items'] = len(items)
        
        # 3. 创建租借记录
        rental_stats = create_test_rentals(db, users, items)
        result['data']['rentals'] = rental_stats
        result['data']['total_rentals'] = sum(rental_stats.values())
        
        # 提交事务
        db.commit()
        
        # 添加登录提示
        result['test_accounts'] = {
            'admin': {
                'username': 'admin',
                'password': 'admin123',
                'role': '管理员'
            },
            'staff': {
                'username': 'staff1',
                'password': 'staff123',
                'role': '工作人员'
            },
            'renter': {
                'username': 'renter1',
                'password': 'renter123',
                'role': '租借人员'
            }
        }
        
    except Exception as e:
        db.rollback()
        result['success'] = False
        result['message'] = f'生成测试数据时发生错误: {str(e)}'
    
    return result


def clear_all_test_data(db: Session) -> Dict:
    """
    清除所有测试数据（谨慎使用）
    
    Args:
        db: 数据库会话
        
    Returns:
        Dict: 清除结果
    """
    result = {
        'success': True,
        'message': '数据清除成功',
        'data': {}
    }
    
    try:
        # 按依赖顺序删除
        db.query(SMSLog).delete()
        db.query(Reminder).delete()
        db.query(CollectionOrder).delete()
        db.query(Rental).delete()
        db.query(Item).delete()
        db.query(User).filter(User.username != 'admin').delete()
        
        db.commit()
        result['message'] = '所有测试数据已清除（保留admin用户）'
        
    except Exception as e:
        db.rollback()
        result['success'] = False
        result['message'] = f'清除数据时发生错误: {str(e)}'
    
    return result
