from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
import random

from ..database import get_db
from ..models.coach import Coach, CoachSchedule
from ..models.member import Member, CoursePackage
from ..models.lesson import LessonRecord, MakeupLesson, FreezeRecord

"""
测试数据生成API路由
提供批量生成测试数据的功能，方便系统功能测试
"""

router = APIRouter(
    prefix="/api/test",
    tags=["测试数据"]
)

# 测试数据预设
COACH_NAMES = [
    "张三", "李四", "王五", "赵六", "孙七",
    "周八", "吴九", "郑十", "陈一", "刘二",
    "王芳", "李娜", "张伟", "刘洋", "陈静"
]

MEMBER_NAMES = [
    "王小华", "李小明", "张大伟", "刘小红", "陈晓峰",
    "周美丽", "吴志强", "郑雅琪", "孙浩然", "朱婷婷",
    "马云飞", "黄蓉", "欧阳震华", "东方朔", "西门吹雪",
    "令狐冲", "任盈盈", "韦小宝", "双儿", "赵敏"
]

EXPERTISE_OPTIONS = ["减脂", "增肌", "康复", "塑形", "普拉提", "瑜伽", "拳击", "拉伸"]
LEVELS = ["初级", "中级", "高级", "金牌"]
GENDERS = ["男", "女"]
COURSE_TYPES = ["常规课", "特色课", "拉伸课", "康复课"]
PAYMENT_METHODS = ["微信", "支付宝", "现金", "银行卡"]


@router.post("/generate/all", summary="生成所有测试数据")
def generate_all_test_data(
    coach_count: int = Query(5, ge=1, le=20, description="教练数量"),
    member_count: int = Query(15, ge=1, le=50, description="会员数量"),
    package_per_member: int = Query(2, ge=1, le=5, description="每个会员的课程包数量"),
    lessons_per_package: int = Query(8, ge=1, le=20, description="每个课程包的课时记录数"),
    db: Session = Depends(get_db)
):
    """
    一键生成所有测试数据
    包括教练、会员、课程包、课时记录、排班等
    """
    # 1. 生成教练
    coaches = generate_coaches(coach_count, db)
    
    # 2. 生成会员
    members = generate_members(member_count, db)
    
    # 3. 生成课程包
    packages = generate_course_packages(members, coaches, package_per_member, db)
    
    # 4. 生成课时记录
    generate_lesson_records(packages, coaches, lessons_per_package, db)
    
    # 5. 生成教练排班
    generate_schedules(coaches, db)
    
    return {
        "message": "测试数据生成成功",
        "counts": {
            "coaches": len(coaches),
            "members": len(members),
            "packages": len(packages)
        }
    }


def generate_coaches(count: int, db: Session) -> list:
    """生成教练数据"""
    coaches = []
    used_phones = set()
    
    for i in range(count):
        # 生成唯一手机号
        while True:
            phone = f"138{random.randint(10000000, 99999999)}"
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        coach = Coach(
            name=random.choice(COACH_NAMES),
            gender=random.choice(GENDERS),
            phone=phone,
            id_card=f"110101{random.randint(1980, 2000)}{random.randint(1000, 9999)}",
            email=f"coach{i+1}@example.com",
            address=f"北京市朝阳区第{i+1}街道",
            hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
            level=random.choice(LEVELS),
            expertise=",".join(random.sample(EXPERTISE_OPTIONS, k=random.randint(1, 3))),
            bio=f"拥有{random.randint(1, 10)}年健身教练经验，擅长多种训练方式。",
            hourly_rate=float(random.randint(100, 300)),
            commission_rate=float(random.randint(20, 40)),
            status="在职"
        )
        db.add(coach)
        coaches.append(coach)
    
    db.commit()
    # 刷新获取ID
    for coach in coaches:
        db.refresh(coach)
    
    return coaches


def generate_members(count: int, db: Session) -> list:
    """生成会员数据"""
    members = []
    used_phones = set()
    
    for i in range(count):
        # 生成唯一手机号
        while True:
            phone = f"139{random.randint(10000000, 99999999)}"
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        member = Member(
            name=random.choice(MEMBER_NAMES),
            gender=random.choice(GENDERS),
            phone=phone,
            id_card=f"110101{random.randint(1985, 2005)}{random.randint(1000, 9999)}",
            email=f"member{i+1}@example.com",
            age=random.randint(18, 60),
            level=random.choice(["普通", "银卡", "金卡", "钻石"]),
            fitness_goal=random.choice(["减脂", "增肌", "塑形", "康复", "增强体质"]),
            health_condition=random.choice(["无特殊状况", "轻度高血压", "腰椎不适", "膝盖损伤"]) if random.random() > 0.7 else None,
            status="正常",
            register_date=date.today() - timedelta(days=random.randint(1, 365))
        )
        db.add(member)
        members.append(member)
    
    db.commit()
    for member in members:
        db.refresh(member)
    
    return members


def generate_course_packages(members: list, coaches: list, per_member: int, db: Session) -> list:
    """生成课程包数据"""
    packages = []
    today = date.today()
    
    package_names = [
        "基础私教课程包",
        "进阶训练课程包",
        "减脂专项课程包",
        "增肌专项课程包",
        "康复训练课程包",
        "VIP定制课程包"
    ]
    
    for member in members:
        for _ in range(per_member):
            total_lessons = random.choice([10, 20, 30, 40, 50])
            unit_price = random.randint(200, 500)
            bonus_lessons = random.randint(0, 5) if random.random() > 0.5 else 0
            
            package = CoursePackage(
                package_no=f"CP{today.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                member_id=member.id,
                coach_id=random.choice(coaches).id if coaches else None,
                name=random.choice(package_names),
                course_type=random.choice(COURSE_TYPES),
                total_lessons=total_lessons,
                bonus_lessons=bonus_lessons,
                unit_price=float(unit_price),
                discount_amount=float(random.randint(0, 500)) if random.random() > 0.7 else 0.0,
                paid_amount=float(total_lessons * unit_price),
                total_amount=float(total_lessons * unit_price),
                remaining_lessons=total_lessons + bonus_lessons,
                used_lessons=0,
                purchase_date=today - timedelta(days=random.randint(0, 90)),
                start_date=today - timedelta(days=random.randint(0, 30)),
                expire_date=today + timedelta(days=random.randint(180, 365)),
                status="有效",
                payment_method=random.choice(PAYMENT_METHODS)
            )
            db.add(package)
            packages.append(package)
    
    db.commit()
    for pkg in packages:
        db.refresh(pkg)
    
    return packages


def generate_lesson_records(packages: list, coaches: list, per_package: int, db: Session):
    """生成课时记录数据"""
    today = date.today()
    
    for pkg in packages:
        # 随机决定这个课程包有多少已完成的课时
        completed_count = random.randint(0, per_package)
        
        for i in range(per_package):
            lesson_date = today - timedelta(days=random.randint(0, 90))
            
            is_completed = i < completed_count
            status = "已完成" if is_completed else "已预约"
            
            # 计算教练报酬和收入贡献
            coach = next((c for c in coaches if c.id == pkg.coach_id), None)
            if coach:
                coach_commission = coach.hourly_rate * (coach.commission_rate / 100)
            else:
                coach_commission = 100.0
            
            lesson = LessonRecord(
                record_no=f"LR{today.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                package_id=pkg.id,
                member_id=pkg.member_id,
                coach_id=pkg.coach_id or random.choice(coaches).id,
                lesson_type=random.choice(["常规课", "常规课", "常规课", "补课"]),
                hours_used=1.0,
                lesson_date=lesson_date,
                start_time=f"{random.randint(9, 19)}:{random.choice(['00', '30'])}",
                end_time=f"{random.randint(10, 20)}:{random.choice(['00', '30'])}",
                lesson_content=random.choice([
                    "热身+力量训练+拉伸",
                    "有氧运动+核心训练",
                    "功能性训练",
                    "针对性减脂训练",
                    "康复性训练"
                ]),
                member_rating=random.randint(3, 5) if is_completed and random.random() > 0.3 else None,
                member_feedback="训练效果不错，教练很专业。" if is_completed and random.random() > 0.5 else None,
                coach_note="会员状态良好，继续保持。" if is_completed else None,
                status=status,
                is_makeup=False,
                coach_commission=coach_commission if is_completed else 0.0,
                revenue_contribution=pkg.unit_price if is_completed else 0.0
            )
            db.add(lesson)
            
            # 如果是已完成的，更新课程包的已用课时
            if is_completed:
                pkg.used_lessons += 1
                pkg.remaining_lessons -= 1
                
                if pkg.remaining_lessons <= 0:
                    pkg.status = "已用完"
    
    db.commit()


def generate_schedules(coaches: list, db: Session):
    """生成教练排班数据"""
    time_slots = [
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
        ("14:00", "15:00"),
        ("15:00", "16:00"),
        ("16:00", "17:00"),
        ("17:00", "18:00"),
        ("18:00", "19:00"),
        ("19:00", "20:00"),
        ("20:00", "21:00"),
    ]
    
    for coach in coaches:
        # 每个教练生成随机排班
        schedule_count = random.randint(10, 20)
        
        for _ in range(schedule_count):
            day_of_week = random.randint(1, 7)
            start_time, end_time = random.choice(time_slots)
            
            schedule = CoachSchedule(
                coach_id=coach.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                status=random.choice(["可用", "可用", "已预约", "休息"])
            )
            db.add(schedule)
    
    db.commit()


@router.post("/generate/coaches", summary="生成教练测试数据")
def generate_coaches_endpoint(
    count: int = Query(5, ge=1, le=20, description="教练数量"),
    db: Session = Depends(get_db)
):
    """单独生成教练测试数据"""
    coaches = generate_coaches(count, db)
    return {
        "message": "教练数据生成成功",
        "count": len(coaches)
    }


@router.post("/generate/members", summary="生成会员测试数据")
def generate_members_endpoint(
    count: int = Query(10, ge=1, le=50, description="会员数量"),
    db: Session = Depends(get_db)
):
    """单独生成会员测试数据"""
    members = generate_members(count, db)
    return {
        "message": "会员数据生成成功",
        "count": len(members)
    }


@router.delete("/clear", summary="清空所有测试数据")
def clear_all_test_data(db: Session = Depends(get_db)):
    """
    清空所有测试数据
    注意：这将删除数据库中所有数据，请谨慎使用
    """
    # 删除顺序需考虑外键约束
    db.query(LessonRecord).delete()
    db.query(MakeupLesson).delete()
    db.query(FreezeRecord).delete()
    db.query(CoursePackage).delete()
    db.query(Member).delete()
    db.query(CoachSchedule).delete()
    db.query(Coach).delete()
    
    db.commit()
    
    return {
        "message": "所有测试数据已清空",
        "tables_cleared": [
            "lesson_records",
            "makeup_lessons",
            "freeze_records",
            "course_packages",
            "members",
            "coach_schedules",
            "coaches"
        ]
    }
