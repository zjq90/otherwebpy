"""
测试功能路由模块
用于生成测试数据和辅助功能测试
包含批量创建测试用户、课程、教练、预约、消息等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import random

from database import get_db
from models import (
    User, UserRole, Gender, Coach, Course, CourseCategory, CourseType,
    MemberPreference, Booking, BookingStatus, Message, MessageType,
    ChatSession, ChatType, ChatMessage, Review,
    NutritionProduct, NutritionProductCategory, Recommendation, RecommendationType
)
from schemas import ResponseModel
from utils import get_password_hash, require_role

router = APIRouter()

# ========================================
# 生成所有测试数据
# ========================================

@router.post("/generate-all", response_model=ResponseModel)
async def generate_all_test_data(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    生成所有测试数据
    
    包括：用户、教练、课程、营养产品、预约、消息、评价等
    需要管理员权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含生成结果的响应
    """
    results = {}
    
    try:
        results['users'] = await generate_test_users_internal(db, member_count=20, coach_count=5, staff_count=3)
        results['coaches'] = await generate_test_coaches_internal(db)
        results['courses'] = await generate_test_courses_internal(db)
        results['products'] = await generate_test_products_internal(db)
        results['preferences'] = await generate_test_preferences_internal(db)
        results['bookings'] = await generate_test_bookings_internal(db)
        results['messages'] = await generate_test_messages_internal(db)
        results['reviews'] = await generate_test_reviews_internal(db)
        
        return ResponseModel(
            code=200,
            message="测试数据生成成功",
            data=results
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试数据失败: {str(e)}"
        )

# ========================================
# 生成测试用户
# ========================================

@router.post("/generate/users", response_model=ResponseModel)
async def generate_test_users(
    member_count: int = Query(10, ge=1, le=100, description="会员数量"),
    coach_count: int = Query(5, ge=1, le=50, description="教练数量"),
    staff_count: int = Query(2, ge=1, le=20, description="工作人员数量"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    生成测试用户数据
    
    Args:
        member_count: 会员数量
        coach_count: 教练数量
        staff_count: 工作人员数量
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含生成结果的响应
    """
    try:
        result = await generate_test_users_internal(db, member_count, coach_count, staff_count)
        return ResponseModel(
            code=200,
            message="测试用户生成成功",
            data=result
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试用户失败: {str(e)}"
        )

async def generate_test_users_internal(
    db: Session,
    member_count: int = 10,
    coach_count: int = 5,
    staff_count: int = 2
) -> dict:
    """内部函数：生成测试用户"""
    created_users = {
        'members': [],
        'coaches': [],
        'staff': []
    }
    
    member_names = [
        "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
        "陈小明", "刘小红", "杨小华", "黄小丽", "周小强", "吴小芳",
        "郑小军", "孙小燕", "朱小峰", "马小娟", "胡小伟", "林小娜"
    ]
    
    coach_names = [
        "王教练", "李教练", "张教练", "刘教练", "陈教练",
        "杨教练", "黄教练", "周教练", "吴教练", "郑教练"
    ]
    
    staff_names = [
        "张主管", "李前台", "王顾问", "赵经理", "钱客服"
    ]
    
    for i in range(member_count):
        name = member_names[i % len(member_names)]
        phone = f"138{str(10000000 + i).zfill(8)}"
        
        member = User(
            username=f"member{i+1}",
            password_hash=get_password_hash("123456"),
            email=f"member{i+1}@gym.com",
            phone=phone,
            real_name=name,
            gender=random.choice([Gender.MALE, Gender.FEMALE]),
            role=UserRole.MEMBER,
            is_active=True
        )
        db.add(member)
        db.flush()
        created_users['members'].append({
            'id': member.id,
            'username': member.username,
            'real_name': member.real_name
        })
    
    for i in range(coach_count):
        name = coach_names[i % len(coach_names)]
        phone = f"139{str(10000000 + i).zfill(8)}"
        
        coach_user = User(
            username=f"coach{i+1}",
            password_hash=get_password_hash("123456"),
            email=f"coach{i+1}@gym.com",
            phone=phone,
            real_name=name,
            gender=random.choice([Gender.MALE, Gender.FEMALE]),
            role=UserRole.COACH,
            is_active=True
        )
        db.add(coach_user)
        db.flush()
        created_users['coaches'].append({
            'id': coach_user.id,
            'username': coach_user.username,
            'real_name': coach_user.real_name
        })
    
    for i in range(staff_count):
        name = staff_names[i % len(staff_names)]
        phone = f"137{str(10000000 + i).zfill(8)}"
        
        staff = User(
            username=f"staff{i+1}",
            password_hash=get_password_hash("123456"),
            email=f"staff{i+1}@gym.com",
            phone=phone,
            real_name=name,
            gender=random.choice([Gender.MALE, Gender.FEMALE]),
            role=UserRole.STAFF,
            is_active=True
        )
        db.add(staff)
        db.flush()
        created_users['staff'].append({
            'id': staff.id,
            'username': staff.username,
            'real_name': staff.real_name
        })
    
    db.commit()
    return created_users

# ========================================
# 生成测试教练资料
# ========================================

@router.post("/generate/coaches", response_model=ResponseModel)
async def generate_test_coaches(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    生成测试教练资料
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含生成结果的响应
    """
    try:
        result = await generate_test_coaches_internal(db)
        return ResponseModel(
            code=200,
            message="测试教练资料生成成功",
            data=result
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试教练资料失败: {str(e)}"
        )

async def generate_test_coaches_internal(db: Session) -> dict:
    """内部函数：生成测试教练资料"""
    coach_users = db.query(User).filter(User.role == UserRole.COACH).all()
    
    specializations = [
        "力量训练,增肌",
        "有氧运动,减脂",
        "瑜伽,普拉提,柔韧性训练",
        "拳击,格斗,体能训练",
        "康复训练,体态矫正",
        "游泳教学,水中健身",
        "舞蹈,尊巴,有氧舞蹈"
    ]
    
    bios = [
        "拥有8年健身教练经验，擅长力量训练和增肌计划制定。",
        "国家级健身教练认证，专注有氧运动和减脂训练。",
        "资深瑜伽教练，持有国际瑜伽联盟认证，擅长普拉提和柔韧性训练。",
        "前职业拳击手，现专注于拳击教学和体能训练。",
        "康复训练专家，擅长体态矫正和运动损伤康复。"
    ]
    
    created_coaches = []
    
    for i, coach_user in enumerate(coach_users):
        existing_coach = db.query(Coach).filter(Coach.user_id == coach_user.id).first()
        if existing_coach:
            continue
        
        coach = Coach(
            user_id=coach_user.id,
            specialization=specializations[i % len(specializations)],
            experience_years=random.randint(1, 15),
            certifications="国家健身教练认证, CPR急救认证",
            bio=bios[i % len(bios)],
            rating=round(random.uniform(4.0, 5.0), 1),
            review_count=random.randint(5, 50),
            hourly_rate=random.choice([150.0, 200.0, 250.0, 300.0, 350.0]),
            is_available=True
        )
        db.add(coach)
        db.flush()
        created_coaches.append({
            'id': coach.id,
            'user_id': coach.user_id,
            'specialization': coach.specialization
        })
    
    db.commit()
    return {'created_coaches': created_coaches}

# ========================================
# 生成测试课程
# ========================================

@router.post("/generate/courses", response_model=ResponseModel)
async def generate_test_courses(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    生成测试课程数据
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含生成结果的响应
    """
    try:
        result = await generate_test_courses_internal(db)
        return ResponseModel(
            code=200,
            message="测试课程生成成功",
            data=result
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试课程失败: {str(e)}"
        )

async def generate_test_courses_internal(db: Session) -> dict:
    """内部函数：生成测试课程"""
    courses_data = [
        {"name": "基础力量训练", "category": CourseCategory.STRENGTH, "course_type": CourseType.GROUP, "duration": 60, "difficulty": 2, "calories": 300},
        {"name": "高级增肌训练", "category": CourseCategory.STRENGTH, "course_type": CourseType.PRIVATE, "duration": 90, "difficulty": 4, "calories": 450},
        {"name": "动感单车", "category": CourseCategory.CARDIO, "course_type": CourseType.GROUP, "duration": 45, "difficulty": 2, "calories": 400},
        {"name": "HIIT高强度间歇", "category": CourseCategory.CARDIO, "course_type": CourseType.GROUP, "duration": 30, "difficulty": 4, "calories": 350},
        {"name": "哈他瑜伽", "category": CourseCategory.YOGA, "course_type": CourseType.GROUP, "duration": 60, "difficulty": 1, "calories": 150},
        {"name": "流瑜伽", "category": CourseCategory.YOGA, "course_type": CourseType.GROUP, "duration": 60, "difficulty": 3, "calories": 200},
        {"name": "普拉提核心", "category": CourseCategory.PILATES, "course_type": CourseType.GROUP, "duration": 50, "difficulty": 2, "calories": 180},
        {"name": "尊巴舞蹈", "category": CourseCategory.DANCE, "course_type": CourseType.GROUP, "duration": 60, "difficulty": 2, "calories": 350},
        {"name": "有氧舞蹈", "category": CourseCategory.DANCE, "course_type": CourseType.GROUP, "duration": 60, "difficulty": 2, "calories": 320},
        {"name": "拳击基础", "category": CourseCategory.BOXING, "course_type": CourseType.PRIVATE, "duration": 60, "difficulty": 3, "calories": 400},
        {"name": "自由搏击", "category": CourseCategory.BOXING, "course_type": CourseType.SEMI_PRIVATE, "duration": 60, "difficulty": 4, "calories": 450},
        {"name": "游泳教学", "category": CourseCategory.SWIMMING, "course_type": CourseType.PRIVATE, "duration": 60, "difficulty": 2, "calories": 400},
        {"name": "水中健身", "category": CourseCategory.SWIMMING, "course_type": CourseType.GROUP, "duration": 45, "difficulty": 1, "calories": 250},
        {"name": "康复训练", "category": CourseCategory.REHABILITATION, "course_type": CourseType.PRIVATE, "duration": 60, "difficulty": 1, "calories": 150},
        {"name": "体态矫正", "category": CourseCategory.REHABILITATION, "course_type": CourseType.PRIVATE, "duration": 60, "difficulty": 2, "calories": 180},
    ]
    
    created_courses = []
    
    for course_data in courses_data:
        existing_course = db.query(Course).filter(Course.name == course_data["name"]).first()
        if existing_course:
            continue
        
        course = Course(
            name=course_data["name"],
            description=f"专业的{course_data['name']}课程，由经验丰富的教练授课。",
            category=course_data["category"],
            course_type=course_data["course_type"],
            duration=course_data["duration"],
            difficulty_level=course_data["difficulty"],
            calories_burned=course_data["calories"],
            is_active=True
        )
        db.add(course)
        db.flush()
        created_courses.append({
            'id': course.id,
            'name': course.name,
            'category': course.category.value
        })
    
    db.commit()
    return {'created_courses': created_courses}

# ========================================
# 生成测试营养产品
# ========================================

@router.post("/generate/products", response_model=ResponseModel)
async def generate_test_products(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    生成测试营养产品数据
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含生成结果的响应
    """
    try:
        result = await generate_test_products_internal(db)
        return ResponseModel(
            code=200,
            message="测试营养产品生成成功",
            data=result
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试营养产品失败: {str(e)}"
        )

async def generate_test_products_internal(db: Session) -> dict:
    """内部函数：生成测试营养产品"""
    products_data = [
        {"name": "乳清蛋白粉（香草味）", "brand": "Optimum Nutrition", "category": NutritionProductCategory.PROTEIN, "price": 298.0, "stock": 100, "suitable_for": "增肌人群", "is_recommended": True},
        {"name": "乳清蛋白粉（巧克力味）", "brand": "Optimum Nutrition", "category": NutritionProductCategory.PROTEIN, "price": 298.0, "stock": 80, "suitable_for": "增肌人群", "is_recommended": True},
        {"name": "分离乳清蛋白粉", "brand": "MuscleTech", "category": NutritionProductCategory.PROTEIN, "price": 398.0, "stock": 50, "suitable_for": "乳糖不耐受人群", "is_recommended": False},
        {"name": "复合维生素片", "brand": "GNC", "category": NutritionProductCategory.VITAMIN, "price": 168.0, "stock": 200, "suitable_for": "所有人群", "is_recommended": True},
        {"name": "维生素C泡腾片", "brand": "Swisse", "category": NutritionProductCategory.VITAMIN, "price": 89.0, "stock": 150, "suitable_for": "所有人群", "is_recommended": False},
        {"name": "肌酸粉", "brand": "Cellucor", "category": NutritionProductCategory.SUPPLEMENT, "price": 198.0, "stock": 60, "suitable_for": "力量训练人群", "is_recommended": True},
        {"name": "支链氨基酸BCAA", "brand": "XTEND", "category": NutritionProductCategory.SUPPLEMENT, "price": 228.0, "stock": 70, "suitable_for": "耐力训练人群", "is_recommended": False},
        {"name": "左旋肉碱", "brand": "MuscleTech", "category": NutritionProductCategory.SUPPLEMENT, "price": 158.0, "stock": 90, "suitable_for": "减脂人群", "is_recommended": True},
        {"name": "蛋白代餐奶昔（草莓味）", "brand": "SlimFast", "category": NutritionProductCategory.MEAL_REPLACEMENT, "price": 258.0, "stock": 80, "suitable_for": "减脂人群", "is_recommended": True},
        {"name": "蛋白代餐奶昔（巧克力味）", "brand": "SlimFast", "category": NutritionProductCategory.MEAL_REPLACEMENT, "price": 258.0, "stock": 75, "suitable_for": "减脂人群", "is_recommended": False},
        {"name": "能量胶", "brand": "GU", "category": NutritionProductCategory.ENERGY, "price": 25.0, "stock": 500, "suitable_for": "马拉松/耐力运动", "is_recommended": True},
        {"name": "运动饮料冲剂", "brand": "Gatorade", "category": NutritionProductCategory.ENERGY, "price": 68.0, "stock": 200, "suitable_for": "所有运动人群", "is_recommended": False},
    ]
    
    created_products = []
    
    for product_data in products_data:
        existing_product = db.query(NutritionProduct).filter(
            NutritionProduct.name == product_data["name"],
            NutritionProduct.brand == product_data["brand"]
        ).first()
        if existing_product:
            continue
        
        product = NutritionProduct(
            name=product_data["name"],
            brand=product_data["brand"],
            category=product_data["category"],
            description=f"高品质{product_data['brand']}品牌{product_data['name']}，适合{product_data['suitable_for']}。",
            price=product_data["price"],
            original_price=product_data["price"] * 1.2,
            stock=product_data["stock"],
            suitable_for=product_data["suitable_for"],
            is_recommended=product_data["is_recommended"],
            is_active=True,
            rating=round(random.uniform(4.0, 5.0), 1),
            review_count=random.randint(10, 200),
            sales_count=random.randint(50, 500)
        )
        db.add(product)
        db.flush()
        created_products.append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand
        })
    
    db.commit()
    return {'created_products': created_products}

# ========================================
# 生成测试会员偏好
# ========================================

async def generate_test_preferences_internal(db: Session) -> dict:
    """内部函数：生成测试会员偏好"""
    members = db.query(User).filter(User.role == UserRole.MEMBER).all()
    
    created_preferences = []
    
    for member in members:
        existing_pref = db.query(MemberPreference).filter(MemberPreference.user_id == member.id).first()
        if existing_pref:
            continue
        
        categories = ["strength", "cardio", "yoga"]
        selected_categories = random.sample(categories, random.randint(1, 2))
        
        goals = ["增肌", "减脂", "塑形", "增强体能"]
        selected_goals = random.sample(goals, random.randint(1, 2))
        
        preference = MemberPreference(
            user_id=member.id,
            preferred_categories=",".join(selected_categories),
            preferred_course_types="group,private",
            preferred_difficulty=random.randint(1, 3),
            training_frequency_per_week=random.randint(2, 5),
            preferred_training_days="周一,周三,周五",
            preferred_training_time=random.choice(["早上", "下午", "晚上"]),
            fitness_goals=",".join(selected_goals),
            has_injuries=False
        )
        db.add(preference)
        db.flush()
        created_preferences.append({
            'user_id': preference.user_id,
            'fitness_goals': preference.fitness_goals
        })
    
    db.commit()
    return {'created_preferences': created_preferences}

# ========================================
# 生成测试预约
# ========================================

async def generate_test_bookings_internal(db: Session) -> dict:
    """内部函数：生成测试预约"""
    members = db.query(User).filter(User.role == UserRole.MEMBER).all()
    courses = db.query(Course).all()
    coaches = db.query(Coach).all()
    
    created_bookings = []
    
    for member in members[:10]:
        for _ in range(random.randint(2, 5)):
            course = random.choice(courses)
            coach = random.choice(coaches) if course.course_type != CourseType.GROUP else None
            
            days_ago = random.randint(-7, 14)
            booking_date = datetime.now().date() + timedelta(days=days_ago)
            
            start_hour = random.choice([9, 10, 14, 15, 16, 18, 19, 20])
            start_time = f"{start_hour:02d}:00"
            end_time = f"{start_hour + 1:02d}:00"
            
            if days_ago < -1:
                status = BookingStatus.COMPLETED
            elif days_ago < 0:
                status = random.choice([BookingStatus.COMPLETED, BookingStatus.NO_SHOW])
            elif days_ago == 0:
                status = random.choice([BookingStatus.CONFIRMED, BookingStatus.PENDING])
            else:
                status = random.choice([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            
            booking = Booking(
                user_id=member.id,
                course_id=course.id,
                coach_id=coach.id if coach else None,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                status=status,
                reminder_sent=days_ago <= 0
            )
            db.add(booking)
            db.flush()
            created_bookings.append({
                'id': booking.id,
                'member_id': booking.user_id,
                'course_id': booking.course_id,
                'status': booking.status.value
            })
    
    db.commit()
    return {'created_bookings': created_bookings}

# ========================================
# 生成测试消息
# ========================================

async def generate_test_messages_internal(db: Session) -> dict:
    """内部函数：生成测试消息"""
    members = db.query(User).filter(User.role == UserRole.MEMBER).all()
    
    message_templates = [
        {"type": MessageType.COURSE_REMINDER, "title": "课程提醒", "content": "您预约的课程将在2小时后开始，请准时到达健身房。"},
        {"type": MessageType.RENEWAL_NOTICE, "title": "续费通知", "content": "您的会员卡即将到期，为避免影响您的正常使用，请及时续费。"},
        {"type": MessageType.ACTIVITY_PUSH, "title": "活动推送", "content": "本月健身挑战赛开始了！完成指定训练即可获得精美礼品。"},
        {"type": MessageType.SYSTEM_ANNOUNCEMENT, "title": "系统公告", "content": "健身房将于下周一进行设备维护，营业时间调整为10:00-22:00。"},
    ]
    
    created_messages = []
    
    for member in members[:15]:
        for template in message_templates:
            message = Message(
                user_id=member.id,
                message_type=template["type"],
                title=template["title"],
                content=template["content"],
                is_read=random.choice([True, False]),
                read_at=datetime.now() if random.choice([True, False]) else None
            )
            db.add(message)
            db.flush()
            created_messages.append({
                'id': message.id,
                'user_id': message.user_id,
                'type': message.message_type.value
            })
    
    db.commit()
    return {'created_messages': created_messages}

# ========================================
# 生成测试评价
# ========================================

async def generate_test_reviews_internal(db: Session) -> dict:
    """内部函数：生成测试评价"""
    completed_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.COMPLETED
    ).all()
    
    created_reviews = []
    
    review_contents = [
        "教练非常专业，训练效果很好！",
        "课程安排合理，强度适中，推荐给大家。",
        "教练很有耐心，会根据我的情况调整训练计划。",
        "今天的训练感觉很棒，出汗很多，期待下次！",
        "教练指导很到位，动作讲解详细，收获满满。"
    ]
    
    for booking in completed_bookings[:20]:
        existing_review = db.query(Review).filter(Review.booking_id == booking.id).first()
        if existing_review:
            continue
        
        if not booking.coach_id:
            continue
        
        rating = random.randint(4, 5)
        
        review = Review(
            user_id=booking.user_id,
            coach_id=booking.coach_id,
            booking_id=booking.id,
            rating=rating,
            professionalism_rating=rating,
            punctuality_rating=rating,
            attitude_rating=rating,
            content=random.choice(review_contents),
            is_visible=True,
            is_anonymous=random.choice([True, False])
        )
        db.add(review)
        db.flush()
        created_reviews.append({
            'id': review.id,
            'coach_id': review.coach_id,
            'rating': review.rating
        })
    
    db.commit()
    return {'created_reviews': created_reviews}

# ========================================
# 清除所有测试数据
# ========================================

@router.post("/clear-all", response_model=ResponseModel)
async def clear_all_test_data(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    清除所有测试数据
    
    注意：这将删除除管理员外的所有数据
    需要管理员权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    try:
        db.query(Review).delete()
        db.query(Booking).delete()
        db.query(Message).delete()
        db.query(ChatMessage).delete()
        db.query(ChatSession).delete()
        db.query(Recommendation).delete()
        db.query(MemberPreference).delete()
        db.query(Coach).delete()
        db.query(Course).delete()
        db.query(NutritionProduct).delete()
        
        db.query(User).filter(User.role != UserRole.ADMIN).delete()
        
        db.commit()
        
        return ResponseModel(
            code=200,
            message="所有测试数据已清除",
            data=None
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除测试数据失败: {str(e)}"
        )

# ========================================
# 获取测试账号信息
# ========================================

@router.get("/accounts", response_model=ResponseModel)
async def get_test_accounts(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    获取测试账号信息
    
    需要管理员权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含测试账号信息的响应
    """
    users = db.query(User).all()
    
    accounts = []
    for user in users:
        accounts.append({
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role.value,
            'phone': user.phone,
            'email': user.email,
            'is_active': user.is_active,
            'default_password': '123456' if user.role != UserRole.ADMIN else 'admin123'
        })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"accounts": accounts}
    )

# ========================================
# API接口测试页面信息
# ========================================

@router.get("/api-info", response_model=ResponseModel)
async def get_api_test_info():
    """
    获取API测试信息
    
    返回所有主要API接口的测试说明
    
    Returns:
        ResponseModel: 包含API信息的响应
    """
    api_info = {
        "base_url": "http://localhost:8000/api/v1",
        "docs_url": "http://localhost:8000/docs",
        "redoc_url": "http://localhost:8000/redoc",
        "default_admin": {
            "username": "admin",
            "password": "admin123"
        },
        "test_users": {
            "member": "member1 / 123456",
            "coach": "coach1 / 123456",
            "staff": "staff1 / 123456"
        },
        "main_modules": [
            {"name": "认证管理", "prefix": "/auth", "description": "注册、登录、令牌刷新等"},
            {"name": "用户管理", "prefix": "/users", "description": "用户增删改查、统计信息"},
            {"name": "教练管理", "prefix": "/coaches", "description": "教练资料、评价列表"},
            {"name": "课程管理", "prefix": "/courses", "description": "课程列表、详情、分类"},
            {"name": "预约管理", "prefix": "/bookings", "description": "预约创建、状态管理"},
            {"name": "消息中心", "prefix": "/messages", "description": "消息列表、已读标记"},
            {"name": "在线客服", "prefix": "/chat", "description": "会话管理、消息发送"},
            {"name": "服务评价", "prefix": "/reviews", "description": "评价创建、教练回复"},
            {"name": "智能推荐", "prefix": "/recommendations", "description": "课程/教练/产品推荐"},
            {"name": "营养产品", "prefix": "/products", "description": "产品列表、详情"},
            {"name": "会员偏好", "prefix": "/preferences", "description": "偏好设置"},
            {"name": "测试功能", "prefix": "/test", "description": "测试数据生成、清除"}
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=api_info
    )
