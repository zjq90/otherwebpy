"""
测试数据生成模块
用于生成系统测试所需的基础数据和示例数据
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, time, timedelta, datetime
import random
import string

from .database import SessionLocal, engine, Base
from .models import (
    CardType, Card, CourseType, Course, Venue, 
    CourseSchedule, Member, MemberCard, CourseBooking
)


def generate_random_phone() -> str:
    """生成随机手机号码"""
    return "1" + ''.join(random.choice(string.digits) for _ in range(10))


def generate_random_name() -> str:
    """生成随机姓名"""
    surnames = ["张", "李", "王", "刘", "陈", "杨", "黄", "赵", "周", "吴", "徐", "孙", "马", "胡", "朱"]
    names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞", "平", "刚", "桂英"]
    return random.choice(surnames) + random.choice(names)


def init_card_types(db: Session) -> list:
    """
    初始化卡类型数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的卡类型列表
    """
    card_types_data = [
        {"name": "年卡", "code": "yearly", "description": "按年计费的会员卡，有效期内无限次使用", "is_active": True},
        {"name": "月卡", "code": "monthly", "description": "按月计费的会员卡，有效期内无限次使用", "is_active": True},
        {"name": "次卡", "code": "count", "description": "按次数计费的会员卡，次数用完即失效", "is_active": True},
        {"name": "储值卡", "code": "stored", "description": "预先充值金额，消费时从卡内扣除", "is_active": True},
        {"name": "私教包", "code": "private", "description": "包含私教课程的套餐卡", "is_active": True},
    ]
    
    created = []
    for data in card_types_data:
        existing = db.execute(select(CardType).where(CardType.code == data["code"])).scalar_one_or_none()
        if not existing:
            card_type = CardType(**data)
            db.add(card_type)
            created.append(card_type)
    
    db.commit()
    return created


def init_cards(db: Session) -> list:
    """
    初始化卡项数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的卡项列表
    """
    # 先获取卡类型
    card_types = db.execute(select(CardType)).scalars().all()
    type_map = {ct.code: ct for ct in card_types}
    
    cards_data = [
        {
            "name": "至尊年卡",
            "card_type_id": type_map.get("yearly").id if type_map.get("yearly") else 1,
            "price": 3999.0,
            "original_price": 5999.0,
            "valid_days": 365,
            "benefits": '{"yoga": true, "spinning": true, "swimming": true, "sauna": true, "personal_trainer": 12}',
            "renewal_rules": '{"discount": 0.85, "extend_days": 30}',
            "description": "全年无限次使用所有设施，包含12节私教课",
            "is_active": True,
            "sort_order": 1
        },
        {
            "name": "精英年卡",
            "card_type_id": type_map.get("yearly").id if type_map.get("yearly") else 1,
            "price": 2999.0,
            "original_price": 3999.0,
            "valid_days": 365,
            "benefits": '{"yoga": true, "spinning": true, "swimming": true}',
            "renewal_rules": '{"discount": 0.9, "extend_days": 15}',
            "description": "全年无限次使用主要健身设施",
            "is_active": True,
            "sort_order": 2
        },
        {
            "name": "畅享月卡",
            "card_type_id": type_map.get("monthly").id if type_map.get("monthly") else 2,
            "price": 399.0,
            "original_price": 499.0,
            "valid_days": 30,
            "benefits": '{"yoga": true, "spinning": true, "gym": true}',
            "renewal_rules": '{"discount": 0.95, "extend_days": 3}',
            "description": "一个月内无限次使用团操课和健身房",
            "is_active": True,
            "sort_order": 3
        },
        {
            "name": "次卡30次",
            "card_type_id": type_map.get("count").id if type_map.get("count") else 3,
            "price": 1800.0,
            "original_price": 2400.0,
            "valid_count": 30,
            "valid_days": 365,
            "benefits": '{"yoga": true, "spinning": true}',
            "description": "30次团操课程，有效期一年",
            "is_active": True,
            "sort_order": 4
        },
        {
            "name": "次卡10次",
            "card_type_id": type_map.get("count").id if type_map.get("count") else 3,
            "price": 680.0,
            "original_price": 800.0,
            "valid_count": 10,
            "valid_days": 180,
            "benefits": '{"yoga": true, "spinning": true}',
            "description": "10次团操课程，有效期半年",
            "is_active": True,
            "sort_order": 5
        },
        {
            "name": "储值卡5000",
            "card_type_id": type_map.get("stored").id if type_map.get("stored") else 4,
            "price": 5000.0,
            "stored_amount": 5000.0,
            "bonus_amount": 500.0,
            "benefits": '{"all": true}',
            "description": "充值5000元赠送500元，全场通用",
            "is_active": True,
            "sort_order": 6
        },
        {
            "name": "储值卡2000",
            "card_type_id": type_map.get("stored").id if type_map.get("stored") else 4,
            "price": 2000.0,
            "stored_amount": 2000.0,
            "bonus_amount": 100.0,
            "benefits": '{"all": true}',
            "description": "充值2000元赠送100元，全场通用",
            "is_active": True,
            "sort_order": 7
        },
        {
            "name": "私教包12节",
            "card_type_id": type_map.get("private").id if type_map.get("private") else 5,
            "price": 3600.0,
            "original_price": 4200.0,
            "valid_count": 12,
            "valid_days": 365,
            "benefits": '{"personal_trainer": true, "yoga": true}',
            "description": "12节专业私教课，有效期一年",
            "is_active": True,
            "sort_order": 8
        },
    ]
    
    created = []
    for data in cards_data:
        existing = db.execute(select(Card).where(Card.name == data["name"])).scalar_one_or_none()
        if not existing:
            card = Card(**data)
            db.add(card)
            created.append(card)
    
    db.commit()
    return created


def init_course_types(db: Session) -> list:
    """
    初始化课程类型数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的课程类型列表
    """
    course_types_data = [
        {"name": "团操课", "code": "group", "description": "多人团体健身课程，如瑜伽、动感单车等", "is_active": True},
        {"name": "私教课", "code": "private", "description": "一对一私人教练指导课程", "is_active": True},
        {"name": "定制课程", "code": "custom", "description": "根据会员需求定制的特殊课程", "is_active": True},
    ]
    
    created = []
    for data in course_types_data:
        existing = db.execute(select(CourseType).where(CourseType.code == data["code"])).scalar_one_or_none()
        if not existing:
            course_type = CourseType(**data)
            db.add(course_type)
            created.append(course_type)
    
    db.commit()
    return created


def init_courses(db: Session) -> list:
    """
    初始化课程数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的课程列表
    """
    course_types = db.execute(select(CourseType)).scalars().all()
    type_map = {ct.code: ct for ct in course_types}
    
    courses_data = [
        {
            "name": "哈他瑜伽",
            "course_type_id": type_map.get("group").id if type_map.get("group") else 1,
            "duration": 60,
            "max_capacity": 20,
            "description": "传统哈他瑜伽，适合所有级别的练习者",
            "difficulty_level": 2,
            "suitable_for": "所有年龄段，初学者友好",
            "precautions": "请穿着舒适的运动服装，自带瑜伽垫",
            "instructor": "李教练",
            "is_active": True
        },
        {
            "name": "流瑜伽",
            "course_type_id": type_map.get("group").id if type_map.get("group") else 1,
            "duration": 60,
            "max_capacity": 15,
            "description": "流畅的体式串联，配合呼吸节奏",
            "difficulty_level": 3,
            "suitable_for": "有一定瑜伽基础者",
            "precautions": "需有一定瑜伽基础",
            "instructor": "王教练",
            "is_active": True
        },
        {
            "name": "动感单车",
            "course_type_id": type_map.get("group").id if type_map.get("group") else 1,
            "duration": 45,
            "max_capacity": 25,
            "description": "高强度有氧骑行，燃脂塑形",
            "difficulty_level": 4,
            "suitable_for": "健康成年人",
            "precautions": "有心脏病史者请咨询医生后参加",
            "instructor": "张教练",
            "is_active": True
        },
        {
            "name": "普拉提",
            "course_type_id": type_map.get("group").id if type_map.get("group") else 1,
            "duration": 60,
            "max_capacity": 12,
            "description": "核心力量训练，改善体态",
            "difficulty_level": 3,
            "suitable_for": "所有年龄段",
            "precautions": "穿着紧身运动服",
            "instructor": "陈教练",
            "is_active": True
        },
        {
            "name": "搏击操",
            "course_type_id": type_map.get("group").id if type_map.get("group") else 1,
            "duration": 50,
            "max_capacity": 20,
            "description": "结合拳击动作的有氧健身操",
            "difficulty_level": 4,
            "suitable_for": "健康成年人",
            "precautions": "佩戴护腕",
            "instructor": "刘教练",
            "is_active": True
        },
        {
            "name": "私教-增肌训练",
            "course_type_id": type_map.get("private").id if type_map.get("private") else 2,
            "duration": 60,
            "max_capacity": 1,
            "description": "一对一指导，针对增肌需求的专业训练",
            "difficulty_level": 3,
            "suitable_for": "所有健身爱好者",
            "precautions": "需提前预约",
            "instructor": "赵教练",
            "is_active": True
        },
        {
            "name": "私教-减脂塑形",
            "course_type_id": type_map.get("private").id if type_map.get("private") else 2,
            "duration": 60,
            "max_capacity": 1,
            "description": "一对一指导，科学减脂塑形",
            "difficulty_level": 2,
            "suitable_for": "所有健身爱好者",
            "precautions": "需提前预约",
            "instructor": "孙教练",
            "is_active": True
        },
    ]
    
    created = []
    for data in courses_data:
        existing = db.execute(select(Course).where(Course.name == data["name"])).scalar_one_or_none()
        if not existing:
            course = Course(**data)
            db.add(course)
            created.append(course)
    
    db.commit()
    return created


def init_venues(db: Session) -> list:
    """
    初始化场地数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的场地列表
    """
    venues_data = [
        {"name": "瑜伽室A", "code": "YOGA_A", "venue_type": "瑜伽室", "capacity": 20, "location": "二楼东侧", "facilities": '{"yoga_mat": 20, "blocks": 20, "straps": 20}', "description": "主要瑜伽教室", "is_active": True, "sort_order": 1},
        {"name": "瑜伽室B", "code": "YOGA_B", "venue_type": "瑜伽室", "capacity": 15, "location": "二楼西侧", "facilities": '{"yoga_mat": 15, "blocks": 15}', "description": "小型瑜伽教室", "is_active": True, "sort_order": 2},
        {"name": "动感单车室", "code": "SPINNING", "venue_type": "动感单车室", "capacity": 25, "location": "一楼北侧", "facilities": '{"bike": 25, "speaker": 1, "screen": 1}', "description": "动感单车专用教室", "is_active": True, "sort_order": 3},
        {"name": "私教室A", "code": "PRIVATE_A", "venue_type": "私教室", "capacity": 2, "location": "三楼东侧", "facilities": '{"dumbbell": 10, "bench": 1, "mirror": 1}', "description": "一对一私教训练室", "is_active": True, "sort_order": 4},
        {"name": "私教室B", "code": "PRIVATE_B", "venue_type": "私教室", "capacity": 2, "location": "三楼西侧", "facilities": '{"dumbbell": 10, "bench": 1, "mirror": 1}', "description": "一对一私教训练室", "is_active": True, "sort_order": 5},
        {"name": "团操室", "code": "GROUP", "venue_type": "团操室", "capacity": 30, "location": "一楼大厅", "facilities": '{"mirror": 1, "speaker": 2, "step": 30}', "description": "大型团操课程教室", "is_active": True, "sort_order": 6},
    ]
    
    created = []
    for data in venues_data:
        existing = db.execute(select(Venue).where(Venue.code == data["code"])).scalar_one_or_none()
        if not existing:
            venue = Venue(**data)
            db.add(venue)
            created.append(venue)
    
    db.commit()
    return created


def init_sample_schedules(db: Session) -> list:
    """
    初始化示例课程排期数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的排期列表
    """
    courses = db.execute(select(Course)).scalars().all()
    venues = db.execute(select(Venue)).scalars().all()
    
    if not courses or not venues:
        return []
    
    # 生成未来7天的排期
    created = []
    today = date.today()
    
    # 课程与场地的映射
    course_venue_map = {
        "哈他瑜伽": "YOGA_A",
        "流瑜伽": "YOGA_B",
        "动感单车": "SPINNING",
        "普拉提": "YOGA_A",
        "搏击操": "GROUP",
        "私教-增肌训练": "PRIVATE_A",
        "私教-减脂塑形": "PRIVATE_B",
    }
    
    # 每日课程安排
    daily_schedule = [
        (time(9, 0), time(10, 0), "哈他瑜伽"),
        (time(10, 30), time(11, 30), "普拉提"),
        (time(14, 0), time(15, 0), "流瑜伽"),
        (time(15, 30), time(16, 15), "动感单车"),
        (time(18, 0), time(18, 50), "搏击操"),
        (time(19, 0), time(19, 45), "动感单车"),
        (time(20, 0), time(21, 0), "流瑜伽"),
    ]
    
    venue_map = {v.code: v for v in venues}
    course_map = {c.name: c for c in courses}
    
    for day_offset in range(7):
        schedule_date = today + timedelta(days=day_offset)
        
        for start_time, end_time, course_name in daily_schedule:
            course = course_map.get(course_name)
            venue_code = course_venue_map.get(course_name)
            venue = venue_map.get(venue_code)
            
            if course and venue:
                # 检查是否已存在
                existing = db.execute(
                    select(CourseSchedule).where(
                        CourseSchedule.course_id == course.id,
                        CourseSchedule.venue_id == venue.id,
                        CourseSchedule.schedule_date == schedule_date,
                        CourseSchedule.start_time == start_time
                    )
                ).scalar_one_or_none()
                
                if not existing:
                    schedule = CourseSchedule(
                        course_id=course.id,
                        venue_id=venue.id,
                        schedule_date=schedule_date,
                        start_time=start_time,
                        end_time=end_time,
                        instructor=course.instructor,
                        max_capacity=min(course.max_capacity, venue.capacity),
                        booked_count=random.randint(0, min(course.max_capacity, venue.capacity) // 2),
                        status="scheduled"
                    )
                    db.add(schedule)
                    created.append(schedule)
    
    db.commit()
    return created


def init_sample_members(db: Session) -> list:
    """
    初始化示例会员数据
    
    Args:
        db: 数据库会话
    
    Returns:
        list: 创建的会员列表
    """
    created = []
    
    for i in range(10):
        phone = generate_random_phone()
        existing = db.execute(select(Member).where(Member.phone == phone)).scalar_one_or_none()
        
        if not existing:
            member = Member(
                member_no=f"M{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}",
                name=generate_random_name(),
                gender=random.choice(["男", "女"]),
                phone=phone,
                email=f"test{i+1}@example.com",
                birthday=date(1990 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28)),
                status="active"
            )
            db.add(member)
            created.append(member)
    
    db.commit()
    return created


def generate_all_test_data():
    """
    生成所有测试数据
    包括卡类型、卡项、课程类型、课程、场地、排期和会员
    """
    db = SessionLocal()
    try:
        print("正在初始化数据库表...")
        Base.metadata.create_all(bind=engine)
        
        print("正在生成卡类型数据...")
        card_types = init_card_types(db)
        print(f"创建了 {len(card_types)} 个卡类型")
        
        print("正在生成卡项数据...")
        cards = init_cards(db)
        print(f"创建了 {len(cards)} 个卡项")
        
        print("正在生成课程类型数据...")
        course_types = init_course_types(db)
        print(f"创建了 {len(course_types)} 个课程类型")
        
        print("正在生成课程数据...")
        courses = init_courses(db)
        print(f"创建了 {len(courses)} 个课程")
        
        print("正在生成场地数据...")
        venues = init_venues(db)
        print(f"创建了 {len(venues)} 个场地")
        
        print("正在生成课程排期数据...")
        schedules = init_sample_schedules(db)
        print(f"创建了 {len(schedules)} 个课程排期")
        
        print("正在生成示例会员数据...")
        members = init_sample_members(db)
        print(f"创建了 {len(members)} 个示例会员")
        
        print("\n测试数据生成完成！")
        return True
        
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_test_data()
