from datetime import date, time, timedelta, datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.database import SessionLocal, Base, engine
from app.models.models import (
    User, UserRole, ClassCategory, Room, Class,
    MemberCard, CardType, CardCategoryLink, CoachSchedule
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def init_database():
    Base.metadata.create_all(bind=engine)

def create_test_data():
    db: Session = SessionLocal()
    
    try:
        if db.query(User).count() > 0:
            print("Test data already exists, skipping...")
            return
        
        print("Creating test users...")
        
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            name="管理员",
            phone="13800000000",
            email="admin@example.com",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        coach1 = User(
            username="coach1",
            password_hash=get_password_hash("coach123"),
            name="李教练",
            phone="13800000001",
            email="coach1@example.com",
            role=UserRole.COACH,
            is_active=True
        )
        db.add(coach1)
        
        coach2 = User(
            username="coach2",
            password_hash=get_password_hash("coach123"),
            name="王教练",
            phone="13800000002",
            email="coach2@example.com",
            role=UserRole.COACH,
            is_active=True
        )
        db.add(coach2)
        
        coach3 = User(
            username="coach3",
            password_hash=get_password_hash("coach123"),
            name="张教练",
            phone="13800000003",
            email="coach3@example.com",
            role=UserRole.COACH,
            is_active=True
        )
        db.add(coach3)
        
        member1 = User(
            username="member1",
            password_hash=get_password_hash("member123"),
            name="张三",
            phone="13900000001",
            email="member1@example.com",
            role=UserRole.MEMBER,
            is_active=True
        )
        db.add(member1)
        
        member2 = User(
            username="member2",
            password_hash=get_password_hash("member123"),
            name="李四",
            phone="13900000002",
            email="member2@example.com",
            role=UserRole.MEMBER,
            is_active=True
        )
        db.add(member2)
        
        db.commit()
        
        print("Creating class categories...")
        
        category1 = ClassCategory(name="瑜伽", description="修身养性的瑜伽课程", is_active=True)
        db.add(category1)
        
        category2 = ClassCategory(name="动感单车", description="高强度有氧动感单车", is_active=True)
        db.add(category2)
        
        category3 = ClassCategory(name="普拉提", description="核心力量训练", is_active=True)
        db.add(category3)
        
        category4 = ClassCategory(name="搏击", description="拳击和搏击训练", is_active=True)
        db.add(category4)
        
        category5 = ClassCategory(name="私教课", description="一对一私教训练", is_active=True)
        db.add(category5)
        
        db.commit()
        
        print("Creating rooms...")
        
        room1 = Room(name="瑜伽室A", capacity=20, location="二楼东侧", qr_code="ROOM_YOGA_A_001", is_active=True)
        db.add(room1)
        
        room2 = Room(name="单车室", capacity=30, location="一楼大厅", qr_code="ROOM_SPIN_001", is_active=True)
        db.add(room2)
        
        room3 = Room(name="力量训练室", capacity=15, location="三楼西侧", qr_code="ROOM_STRENGTH_001", is_active=True)
        db.add(room3)
        
        room4 = Room(name="私教教室", capacity=5, location="二楼VIP区", qr_code="ROOM_PRIVATE_001", is_active=True)
        db.add(room4)
        
        db.commit()
        
        print("Creating member cards...")
        
        today = date.today()
        start_date = today
        end_date = today + timedelta(days=365)
        
        card1 = MemberCard(
            user_id=member1.id,
            card_type=CardType.YEARLY,
            card_name="年度通卡",
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        db.add(card1)
        
        card2 = MemberCard(
            user_id=member2.id,
            card_type=CardType.MONTHLY,
            card_name="月卡",
            start_date=start_date,
            end_date=today + timedelta(days=30),
            is_active=True
        )
        db.add(card2)
        
        card3 = MemberCard(
            user_id=member1.id,
            card_type=CardType.PRIVATE,
            card_name="私教次卡",
            total_times=20,
            used_times=0,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        db.add(card3)
        
        db.commit()
        
        print("Creating card-category links...")
        
        for card in [card1, card2, card3]:
            for category in [category1, category2, category3, category4]:
                link = CardCategoryLink(card_id=card.id, category_id=category.id)
                db.add(link)
        
        link5 = CardCategoryLink(card_id=card3.id, category_id=category5.id)
        db.add(link5)
        
        db.commit()
        
        print("Creating classes...")
        
        db.refresh(coach1)
        db.refresh(coach2)
        db.refresh(coach3)
        
        for i in range(14):
            class_date = today + timedelta(days=i)
            weekday = class_date.weekday()
            
            if weekday < 5:
                class1 = Class(
                    category_id=category1.id,
                    coach_id=coach1.id,
                    room_id=room1.id,
                    name="晨间瑜伽",
                    description="适合新手的基础瑜伽课程，放松身心",
                    class_date=class_date,
                    start_time=time(8, 0),
                    end_time=time(9, 0),
                    capacity=20,
                    booked_count=0,
                    is_active=True
                )
                db.add(class1)
                
                class2 = Class(
                    category_id=category2.id,
                    coach_id=coach2.id,
                    room_id=room2.id,
                    name="动感单车",
                    description="高强度有氧训练，燃烧卡路里",
                    class_date=class_date,
                    start_time=time(9, 30),
                    end_time=time(10, 30),
                    capacity=30,
                    booked_count=0,
                    is_active=True
                )
                db.add(class2)
                
                class3 = Class(
                    category_id=category3.id,
                    coach_id=coach3.id,
                    room_id=room1.id,
                    name="普拉提核心",
                    description="专注核心肌群训练，塑造完美身材",
                    class_date=class_date,
                    start_time=time(14, 0),
                    end_time=time(15, 0),
                    capacity=15,
                    booked_count=0,
                    is_active=True
                )
                db.add(class3)
                
                class4 = Class(
                    category_id=category4.id,
                    coach_id=coach2.id,
                    room_id=room3.id,
                    name="搏击操",
                    description="释放压力的搏击有氧运动",
                    class_date=class_date,
                    start_time=time(19, 0),
                    end_time=time(20, 0),
                    capacity=20,
                    booked_count=0,
                    is_active=True
                )
                db.add(class4)
                
                class5 = Class(
                    category_id=category1.id,
                    coach_id=coach1.id,
                    room_id=room1.id,
                    name="晚间瑜伽",
                    description="舒缓一天的疲劳，助于睡眠",
                    class_date=class_date,
                    start_time=time(20, 30),
                    end_time=time(21, 30),
                    capacity=20,
                    booked_count=0,
                    is_active=True
                )
                db.add(class5)
            else:
                class1 = Class(
                    category_id=category1.id,
                    coach_id=coach1.id,
                    room_id=room1.id,
                    name="周末瑜伽静心",
                    description="周末特别课程，深度放松",
                    class_date=class_date,
                    start_time=time(10, 0),
                    end_time=time(11, 30),
                    capacity=20,
                    booked_count=0,
                    is_active=True
                )
                db.add(class1)
                
                class2 = Class(
                    category_id=category2.id,
                    coach_id=coach2.id,
                    room_id=room2.id,
                    name="周末动感单车挑战",
                    description="高强度挑战课程",
                    class_date=class_date,
                    start_time=time(14, 0),
                    end_time=time(15, 30),
                    capacity=30,
                    booked_count=0,
                    is_active=True
                )
                db.add(class2)
        
        db.commit()
        
        print("Creating coach schedules...")
        
        coach_ids = [coach1.id, coach2.id, coach3.id]
        
        for coach_id in coach_ids:
            for i in range(14):
                schedule_date = today + timedelta(days=i)
                weekday = schedule_date.weekday()
                
                if weekday < 5:
                    slots = [
                        (time(10, 0), time(11, 0)),
                        (time(15, 0), time(16, 0)),
                        (time(16, 0), time(17, 0)),
                        (time(17, 0), time(18, 0)),
                    ]
                else:
                    slots = [
                        (time(9, 0), time(10, 0)),
                        (time(10, 0), time(11, 0)),
                        (time(14, 0), time(15, 0)),
                        (time(15, 0), time(16, 0)),
                        (time(16, 0), time(17, 0)),
                    ]
                
                for start_t, end_t in slots:
                    schedule = CoachSchedule(
                        coach_id=coach_id,
                        schedule_date=schedule_date,
                        start_time=start_t,
                        end_time=end_t,
                        is_available=True,
                        is_booked=False
                    )
                    db.add(schedule)
        
        db.commit()
        
        print("Test data created successfully!")
        print("\n" + "="*50)
        print("Test Accounts:")
        print("="*50)
        print(f"Admin: username='admin', password='admin123'")
        print(f"Coach 1: username='coach1', password='coach123' (李教练)")
        print(f"Coach 2: username='coach2', password='coach123' (王教练)")
        print(f"Coach 3: username='coach3', password='coach123' (张教练)")
        print(f"Member 1: username='member1', password='member123' (张三)")
        print(f"Member 2: username='member2', password='member123' (李四)")
        print("="*50)
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Creating test data...")
    create_test_data()
    print("Done!")
