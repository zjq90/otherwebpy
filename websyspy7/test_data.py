"""
测试数据生成模块
用于创建测试数据进行功能测试
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import async_session_maker, init_db
from models import User, Passenger, MonitorTask, Order, AlertRecord, Station, TrainInfo
from auth import get_password_hash


async def create_test_users(db: AsyncSession):
    """
    创建测试用户
    """
    # 检查是否已存在用户
    result = await db.execute(select(User).where(User.username == "admin"))
    admin = result.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@example.com",
            phone="13800138000",
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        print(f"✅ 创建管理员用户: admin / admin123")
    else:
        print(f"ℹ️ 管理员用户已存在")
    
    # 创建普通测试用户
    result = await db.execute(select(User).where(User.username == "testuser"))
    test_user = result.scalar_one_or_none()
    
    if not test_user:
        test_user = User(
            username="testuser",
            password_hash=get_password_hash("test123"),
            email="test@example.com",
            phone="13900139000",
            is_admin=False,
            is_active=True
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        print(f"✅ 创建测试用户: testuser / test123")
    else:
        print(f"ℹ️ 测试用户已存在")
    
    return admin


async def create_test_passengers(db: AsyncSession, user: User):
    """
    创建测试乘客
    """
    passengers_data = [
        {
            "name": "张三",
            "id_card": "110101199001011234",
            "phone": "13800138001",
            "passenger_type": "成人",
            "is_default": True
        },
        {
            "name": "李四",
            "id_card": "110101199205155678",
            "phone": "13800138002",
            "passenger_type": "成人",
            "is_default": False
        },
        {
            "name": "张小宝",
            "id_card": "110101201508209012",
            "phone": "13800138001",
            "passenger_type": "儿童",
            "is_default": False
        }
    ]
    
    for p_data in passengers_data:
        # 检查是否已存在
        result = await db.execute(
            select(Passenger).where(
                Passenger.user_id == user.id,
                Passenger.name == p_data["name"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            passenger = Passenger(
                user_id=user.id,
                **p_data,
                status="active"
            )
            db.add(passenger)
            await db.commit()
            print(f"✅ 创建测试乘客: {p_data['name']}")
        else:
            print(f"ℹ️ 乘客 {p_data['name']} 已存在")


async def create_test_stations(db: AsyncSession):
    """
    创建测试站点数据
    """
    stations_data = [
        {"station_name": "北京", "station_code": "BJP", "station_pinyin": "beijing", "province": "北京市"},
        {"station_name": "北京南", "station_code": "VNP", "station_pinyin": "beijingnan", "province": "北京市"},
        {"station_name": "上海", "station_code": "SHQ", "station_pinyin": "shanghai", "province": "上海市"},
        {"station_name": "上海虹桥", "station_code": "SHH", "station_pinyin": "shanghaihongqiao", "province": "上海市"},
        {"station_name": "广州南", "station_code": "GZQ", "station_pinyin": "guangzhounan", "province": "广东省"},
        {"station_name": "深圳北", "station_code": "SZQ", "station_pinyin": "shenzhenbei", "province": "广东省"},
        {"station_name": "成都东", "station_code": "CDW", "station_pinyin": "chengdudong", "province": "四川省"},
        {"station_name": "重庆北", "station_code": "CQW", "station_pinyin": "chongqingbei", "province": "重庆市"},
        {"station_name": "武汉", "station_code": "WHN", "station_pinyin": "wuhan", "province": "湖北省"},
        {"station_name": "西安北", "station_code": "XAY", "station_pinyin": "xianbei", "province": "陕西省"},
        {"station_name": "杭州东", "station_code": "HGH", "station_pinyin": "hangzhoudong", "province": "浙江省"},
        {"station_name": "南京南", "station_code": "NJH", "station_pinyin": "nanjingnan", "province": "江苏省"},
    ]
    
    count = 0
    for s_data in stations_data:
        result = await db.execute(
            select(Station).where(Station.station_code == s_data["station_code"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            station = Station(**s_data, is_active=True)
            db.add(station)
            count += 1
    
    if count > 0:
        await db.commit()
        print(f"✅ 创建 {count} 个站点数据")
    else:
        print(f"ℹ️ 站点数据已存在")


async def create_test_trains(db: AsyncSession):
    """
    创建测试车次数据
    """
    trains_data = [
        {"train_number": "G1", "train_type": "G", "from_station": "北京南", "to_station": "上海虹桥", "depart_time": "07:00", "arrive_time": "11:28", "duration": "4小时28分"},
        {"train_number": "G5", "train_type": "G", "from_station": "北京南", "to_station": "上海虹桥", "depart_time": "08:00", "arrive_time": "12:28", "duration": "4小时28分"},
        {"train_number": "G79", "train_type": "G", "from_station": "北京西", "to_station": "深圳北", "depart_time": "10:00", "arrive_time": "18:35", "duration": "8小时35分"},
        {"train_number": "D311", "train_type": "D", "from_station": "北京南", "to_station": "上海", "depart_time": "22:16", "arrive_time": "09:09", "duration": "10小时53分"},
        {"train_number": "G89", "train_type": "G", "from_station": "北京西", "to_station": "成都东", "depart_time": "06:53", "arrive_time": "14:41", "duration": "7小时48分"},
    ]
    
    count = 0
    for t_data in trains_data:
        result = await db.execute(
            select(TrainInfo).where(TrainInfo.train_number == t_data["train_number"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            train = TrainInfo(**t_data)
            db.add(train)
            count += 1
    
    if count > 0:
        await db.commit()
        print(f"✅ 创建 {count} 个车次数据")
    else:
        print(f"ℹ️ 车次数据已存在")


async def create_test_monitor_tasks(db: AsyncSession, user: User):
    """
    创建测试监控任务
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    tasks_data = [
        {
            "task_name": "北京到上海G字头监控",
            "from_station": "北京南",
            "to_station": "上海虹桥",
            "train_date": tomorrow,
            "train_numbers": "G1,G5",
            "seat_types": "二等座,一等座",
            "poll_interval": 2.0,
            "auto_submit": False,
            "status": "stopped"
        },
        {
            "task_name": "广州到深圳通勤监控",
            "from_station": "广州南",
            "to_station": "深圳北",
            "train_date": day_after,
            "seat_types": "二等座",
            "poll_interval": 1.0,
            "auto_submit": True,
            "status": "stopped"
        }
    ]
    
    for t_data in tasks_data:
        result = await db.execute(
            select(MonitorTask).where(
                MonitorTask.user_id == user.id,
                MonitorTask.task_name == t_data["task_name"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            task = MonitorTask(
                user_id=user.id,
                **t_data,
                max_retries=3
            )
            db.add(task)
            await db.commit()
            print(f"✅ 创建测试监控任务: {t_data['task_name']}")
        else:
            print(f"ℹ️ 监控任务 {t_data['task_name']} 已存在")


async def create_test_orders(db: AsyncSession, user: User):
    """
    创建测试订单
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    orders_data = [
        {
            "order_no": f"E{datetime.now().strftime('%Y%m%d')}0001",
            "train_number": "G1",
            "from_station": "北京南",
            "to_station": "上海虹桥",
            "depart_time": "07:00",
            "arrive_time": "11:28",
            "train_date": tomorrow,
            "passenger_info": '[{"name": "张三", "id_card": "110101199001011234"}]',
            "seat_type": "二等座",
            "seat_no": "12A",
            "ticket_price": 553.0,
            "total_amount": 553.0,
            "status": "submitted",
            "submit_time": datetime.now(),
            "pay_deadline": datetime.now() + timedelta(minutes=30)
        }
    ]
    
    for o_data in orders_data:
        result = await db.execute(
            select(Order).where(Order.order_no == o_data["order_no"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            order = Order(
                user_id=user.id,
                **o_data
            )
            db.add(order)
            await db.commit()
            print(f"✅ 创建测试订单: {o_data['order_no']}")
        else:
            print(f"ℹ️ 订单 {o_data['order_no']} 已存在")


async def create_test_alerts(db: AsyncSession, user: User):
    """
    创建测试提醒
    """
    alerts_data = [
        {
            "alert_type": "system",
            "alert_title": "【发现余票】北京南→上海虹桥",
            "alert_content": "监控到G1车次有余票！\n二等座：有\n一等座：有\n请及时处理。",
            "is_read": False,
            "is_sent": True
        },
        {
            "alert_type": "system",
            "alert_title": "订单提交成功",
            "alert_content": "您的订单已成功提交，请在30分钟内完成支付。\n订单号：E202605030001\n车次：G1 北京南→上海虹桥",
            "is_read": True,
            "is_sent": True
        }
    ]
    
    count = 0
    for a_data in alerts_data:
        result = await db.execute(
            select(AlertRecord).where(
                AlertRecord.user_id == user.id,
                AlertRecord.alert_title == a_data["alert_title"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            alert = AlertRecord(
                user_id=user.id,
                **a_data
            )
            db.add(alert)
            count += 1
    
    if count > 0:
        await db.commit()
        print(f"✅ 创建 {count} 个测试提醒")
    else:
        print(f"ℹ️ 测试提醒已存在")


async def generate_all_test_data():
    """
    生成所有测试数据
    """
    print("=" * 50)
    print("🚀 开始生成测试数据...")
    print("=" * 50)
    
    # 初始化数据库
    await init_db()
    
    async with async_session_maker() as session:
        # 创建测试用户
        print("\n📋 创建测试用户...")
        admin_user = await create_test_users(session)
        
        # 创建测试乘客
        print("\n👥 创建测试乘客...")
        await create_test_passengers(session, admin_user)
        
        # 创建测试站点
        print("\n🚉 创建测试站点...")
        await create_test_stations(session)
        
        # 创建测试车次
        print("\n🚄 创建测试车次...")
        await create_test_trains(session)
        
        # 创建测试监控任务
        print("\n👁️ 创建测试监控任务...")
        await create_test_monitor_tasks(session, admin_user)
        
        # 创建测试订单
        print("\n📋 创建测试订单...")
        await create_test_orders(session, admin_user)
        
        # 创建测试提醒
        print("\n🔔 创建测试提醒...")
        await create_test_alerts(session, admin_user)
    
    print("\n" + "=" * 50)
    print("✅ 测试数据生成完成！")
    print("=" * 50)
    print("\n📌 默认登录账号：")
    print("   - 管理员：admin / admin123")
    print("   - 测试用户：testuser / test123")
    print("\n📌 测试数据说明：")
    print("   - 3个测试乘客（张三、李四、张小宝）")
    print("   - 12个常用站点（北京、上海、广州、深圳等）")
    print("   - 5个测试车次（G1、G5、G79、D311、G89）")
    print("   - 2个测试监控任务")
    print("   - 1个测试订单")
    print("   - 2个测试提醒")


if __name__ == "__main__":
    asyncio.run(generate_all_test_data())
