"""
数据库初始化和测试数据生成脚本
运行此脚本将创建数据库表并插入测试数据
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.service_request import ServiceRequest, ServiceProgress, ServiceType, ServiceStatus
from app.models.activity import Activity, ActivityRegistration, ActivityType, ActivityStatus
from app.crud.user import get_password_hash


def create_tables():
    """
    创建数据库表
    """
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def create_test_users(db):
    """
    创建测试用户
    """
    print("正在创建测试用户...")
    
    users_data = [
        {
            "username": "admin",
            "password": "123456",
            "real_name": "系统管理员",
            "phone": "13800138001",
            "email": "admin@community.com",
            "room_number": None,
            "role": UserRole.ADMIN.value
        },
        {
            "username": "property",
            "password": "123456",
            "real_name": "物业人员",
            "phone": "13800138002",
            "email": "property@community.com",
            "room_number": None,
            "role": UserRole.PROPERTY.value
        },
        {
            "username": "resident1",
            "password": "123456",
            "real_name": "张三",
            "phone": "13800138003",
            "email": "zhangsan@example.com",
            "room_number": "1栋101室",
            "role": UserRole.RESIDENT.value
        },
        {
            "username": "resident2",
            "password": "123456",
            "real_name": "李四",
            "phone": "13800138004",
            "email": "lisi@example.com",
            "room_number": "1栋201室",
            "role": UserRole.RESIDENT.value
        },
        {
            "username": "resident3",
            "password": "123456",
            "real_name": "王五",
            "phone": "13800138005",
            "email": "wangwu@example.com",
            "room_number": "2栋101室",
            "role": UserRole.RESIDENT.value
        }
    ]
    
    users = []
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            user = User(
                username=user_data["username"],
                password=get_password_hash(user_data["password"]),
                real_name=user_data["real_name"],
                phone=user_data["phone"],
                email=user_data["email"],
                room_number=user_data["room_number"],
                role=user_data["role"]
            )
            db.add(user)
            users.append(user)
            print(f"  创建用户: {user_data['username']} ({user_data['real_name']})")
        else:
            users.append(existing_user)
            print(f"  用户已存在: {user_data['username']}")
    
    db.commit()
    
    return {u.username: u for u in users}


def create_test_service_requests(db, users):
    """
    创建测试服务请求
    """
    print("正在创建测试服务请求...")
    
    admin = users.get("admin")
    property_user = users.get("property")
    resident1 = users.get("resident1")
    resident2 = users.get("resident2")
    
    services_data = [
        {
            "title": "卫生间漏水维修",
            "description": "卫生间天花板漏水，水滴滴到楼下住户，需要紧急维修。",
            "service_type": ServiceType.REPAIR.value,
            "status": ServiceStatus.PENDING.value,
            "user_id": resident1.id if resident1 else 3,
            "assignee_id": None,
            "room_number": "1栋101室",
            "contact_name": "张三",
            "contact_phone": "13800138003",
            "priority": 3,
            "location": "卫生间",
            "created_at": datetime.now() - timedelta(hours=2)
        },
        {
            "title": "电梯噪音投诉",
            "description": "最近电梯运行时噪音很大，尤其是在夜间，严重影响居民休息。希望物业能够安排检查和维护。",
            "service_type": ServiceType.COMPLAINT.value,
            "status": ServiceStatus.ASSIGNED.value,
            "user_id": resident2.id if resident2 else 4,
            "assignee_id": property_user.id if property_user else 2,
            "room_number": "1栋201室",
            "contact_name": "李四",
            "contact_phone": "13800138004",
            "priority": 2,
            "location": "1栋电梯",
            "created_at": datetime.now() - timedelta(hours=5)
        },
        {
            "title": "关于停车收费标准咨询",
            "description": "请问小区的停车收费标准是怎样的？月卡和临时停车分别怎么收费？",
            "service_type": ServiceType.CONSULT.value,
            "status": ServiceStatus.COMPLETED.value,
            "user_id": resident1.id if resident1 else 3,
            "assignee_id": admin.id if admin else 1,
            "room_number": "1栋101室",
            "contact_name": "张三",
            "contact_phone": "13800138003",
            "priority": 1,
            "location": None,
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "title": "楼道灯损坏维修",
            "description": "1栋3楼的楼道灯损坏了，晚上走路很不方便，希望尽快维修。",
            "service_type": ServiceType.REPAIR.value,
            "status": ServiceStatus.PROCESSING.value,
            "user_id": resident2.id if resident2 else 4,
            "assignee_id": property_user.id if property_user else 2,
            "room_number": "1栋3层",
            "contact_name": "李四",
            "contact_phone": "13800138004",
            "priority": 2,
            "location": "1栋3楼楼道",
            "created_at": datetime.now() - timedelta(hours=8)
        },
        {
            "title": "门禁系统故障",
            "description": "小区北门的门禁系统经常失灵，刷门禁卡没有反应，需要多次尝试才能开门。",
            "service_type": ServiceType.REPAIR.value,
            "status": ServiceStatus.CLOSED.value,
            "user_id": resident1.id if resident1 else 3,
            "assignee_id": admin.id if admin else 1,
            "room_number": "北门门禁",
            "contact_name": "张三",
            "contact_phone": "13800138003",
            "priority": 2,
            "location": "小区北门",
            "created_at": datetime.now() - timedelta(days=5),
            "completed_at": datetime.now() - timedelta(days=3)
        }
    ]
    
    for service_data in services_data:
        existing = db.query(ServiceRequest).filter(
            ServiceRequest.title == service_data["title"]
        ).first()
        if not existing:
            service = ServiceRequest(**service_data)
            db.add(service)
            print(f"  创建服务请求: {service_data['title']}")
    
    db.commit()


def create_test_activities(db, users):
    """
    创建测试活动
    """
    print("正在创建测试活动...")
    
    admin = users.get("admin")
    
    now = datetime.now()
    
    activities_data = [
        {
            "title": "2024年春节联欢会",
            "description": "为庆祝农历新年，小区将举办春节联欢会。活动内容包括：\n\n1. 业主才艺表演\n2. 抽奖活动\n3. 美食分享\n4. 亲子游戏\n\n欢迎各位业主携家人参加，共度新春佳节！",
            "activity_type": ActivityType.FESTIVAL.value,
            "status": ActivityStatus.REGISTRATION_OPEN.value,
            "organizer_id": admin.id if admin else 1,
            "start_time": now + timedelta(days=15, hours=14),
            "end_time": now + timedelta(days=15, hours=18),
            "registration_deadline": now + timedelta(days=10),
            "location": "小区会所大厅",
            "max_participants": 100,
            "current_participants": 45,
            "is_featured": True,
            "views_count": 156,
            "contact_name": "管理员",
            "contact_phone": "13800138001"
        },
        {
            "title": "邻里美食分享会",
            "description": "为增进邻里感情，特举办美食分享会。每位参加的业主请准备一道拿手菜，与邻里一起分享美食、交流厨艺心得。",
            "activity_type": ActivityType.NEIGHBOR_INTERACTION.value,
            "status": ActivityStatus.REGISTRATION_OPEN.value,
            "organizer_id": admin.id if admin else 1,
            "start_time": now + timedelta(days=7, hours=17),
            "end_time": now + timedelta(days=7, hours=20),
            "registration_deadline": now + timedelta(days=5),
            "location": "小区中央花园",
            "max_participants": 50,
            "current_participants": 28,
            "is_featured": True,
            "views_count": 89,
            "contact_name": "管理员",
            "contact_phone": "13800138001"
        },
        {
            "title": "社区篮球友谊赛",
            "description": "小区篮球友谊赛开始报名！欢迎各位篮球爱好者组队参加。\n\n比赛规则：\n- 4V4半场比赛\n- 每队至少4人\n- 采用淘汰制\n\n报名截止日期：即日起至比赛前3天",
            "activity_type": ActivityType.SPORTS.value,
            "status": ActivityStatus.REGISTRATION_OPEN.value,
            "organizer_id": admin.id if admin else 1,
            "start_time": now + timedelta(days=20, hours=9),
            "end_time": now + timedelta(days=20, hours=12),
            "registration_deadline": now + timedelta(days=17),
            "location": "小区篮球场",
            "max_participants": 32,
            "current_participants": 16,
            "is_featured": False,
            "views_count": 67,
            "contact_name": "管理员",
            "contact_phone": "13800138001"
        },
        {
            "title": "传统文化讲座 - 书法艺术",
            "description": "为弘扬中华传统文化，小区特邀知名书法家举办书法讲座。\n\n讲座内容：\n1. 书法基础知识\n2. 基本笔法练习\n3. 作品赏析\n4. 现场指导\n\n欢迎各位书法爱好者参加，现场提供笔墨纸砚。",
            "activity_type": ActivityType.CULTURAL.value,
            "status": ActivityStatus.COMPLETED.value,
            "organizer_id": admin.id if admin else 1,
            "start_time": now - timedelta(days=10, hours=14),
            "end_time": now - timedelta(days=10, hours=17),
            "registration_deadline": now - timedelta(days=15),
            "location": "小区会所多功能厅",
            "max_participants": 40,
            "current_participants": 35,
            "is_featured": False,
            "views_count": 120,
            "contact_name": "管理员",
            "contact_phone": "13800138001"
        },
        {
            "title": "爱心义卖活动",
            "description": "小区将举办爱心义卖活动，所得款项将全部捐赠给慈善机构。\n\n如果您有闲置物品（书籍、玩具、日用品等），欢迎捐赠或参与义卖。让我们一起传递爱心，共建和谐社区！",
            "activity_type": ActivityType.CHARITY.value,
            "status": ActivityStatus.PUBLISHED.value,
            "organizer_id": admin.id if admin else 1,
            "start_time": now + timedelta(days=30, hours=10),
            "end_time": now + timedelta(days=30, hours=16),
            "registration_deadline": now + timedelta(days=25),
            "location": "小区中央广场",
            "max_participants": None,
            "current_participants": 0,
            "is_featured": True,
            "views_count": 45,
            "contact_name": "管理员",
            "contact_phone": "13800138001"
        }
    ]
    
    created_activities = []
    for activity_data in activities_data:
        existing = db.query(Activity).filter(
            Activity.title == activity_data["title"]
        ).first()
        if not existing:
            activity = Activity(**activity_data)
            db.add(activity)
            db.flush()
            created_activities.append(activity)
            print(f"  创建活动: {activity_data['title']}")
        else:
            created_activities.append(existing)
    
    db.commit()
    
    return created_activities


def create_test_registrations(db, users, activities):
    """
    创建测试活动报名记录
    """
    print("正在创建测试活动报名记录...")
    
    resident1 = users.get("resident1")
    resident2 = users.get("resident2")
    resident3 = users.get("resident3")
    
    registrations_data = []
    
    for activity in activities:
        if activity.status == ActivityStatus.REGISTRATION_OPEN.value:
            if resident1 and activity.current_participants < (activity.max_participants or 100):
                registrations_data.append({
                    "activity_id": activity.id,
                    "user_id": resident1.id,
                    "participant_name": resident1.real_name,
                    "participant_phone": resident1.phone,
                    "participant_count": 2,
                    "room_number": resident1.room_number
                })
            if resident2 and activity.current_participants < (activity.max_participants or 100):
                registrations_data.append({
                    "activity_id": activity.id,
                    "user_id": resident2.id,
                    "participant_name": resident2.real_name,
                    "participant_phone": resident2.phone,
                    "participant_count": 3,
                    "room_number": resident2.room_number
                })
            if resident3 and activity.current_participants < (activity.max_participants or 100):
                registrations_data.append({
                    "activity_id": activity.id,
                    "user_id": resident3.id,
                    "participant_name": resident3.real_name,
                    "participant_phone": resident3.phone,
                    "participant_count": 1,
                    "room_number": resident3.room_number
                })
    
    for reg_data in registrations_data:
        existing = db.query(ActivityRegistration).filter(
            ActivityRegistration.activity_id == reg_data["activity_id"],
            ActivityRegistration.user_id == reg_data["user_id"]
        ).first()
        if not existing:
            registration = ActivityRegistration(**reg_data)
            db.add(registration)
            print(f"  创建报名记录: 活动ID={reg_data['activity_id']}, 用户ID={reg_data['user_id']}")
    
    db.commit()


def main():
    """
    主函数
    """
    print("=" * 50)
    print("社区管理系统 - 数据库初始化脚本")
    print("=" * 50)
    
    create_tables()
    
    db = SessionLocal()
    try:
        users = create_test_users(db)
        create_test_service_requests(db, users)
        activities = create_test_activities(db, users)
        create_test_registrations(db, users, activities)
        
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        print("\n测试账号信息：")
        print("-" * 30)
        print("管理员账号：")
        print("  用户名: admin")
        print("  密码: 123456")
        print("\n物业人员账号：")
        print("  用户名: property")
        print("  密码: 123456")
        print("\n业主账号：")
        print("  用户名: resident1, resident2, resident3")
        print("  密码: 123456")
        print("-" * 30)
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
