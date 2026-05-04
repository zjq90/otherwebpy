"""
测试数据生成器
用于生成测试用的模拟数据
"""
import random
from datetime import datetime, timedelta, date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.member import Member, MemberStatus, RegistrationChannel, VerificationMethod
from app.models.archive import PhysicalTest, FitnessGoal, ConsumptionRecord, CourseParticipation
from app.models.level import MemberLevel, LevelBenefit


class TestDataGenerator:
    """
    测试数据生成器类
    提供生成各类测试数据的方法
    """
    
    # 预设的中文姓名
    CHINESE_NAMES = [
        "张伟", "王芳", "李娜", "刘洋", "陈明",
        "杨丽", "赵强", "黄敏", "周杰", "吴静",
        "孙磊", "马云", "朱婷", "胡歌", "郭靖",
        "林峰", "曹颖", "韩雪", "邓超", "孙俪",
        "何冰", "高峰", "罗琳", "谢霆", "唐嫣",
        "韩磊", "冯小刚", "章子怡", "黄晓明", "范冰冰",
        "郭德纲", "杨幂", "鹿晗", "吴亦凡", "李易峰",
        "杨洋", "张艺兴", "黄子韬", "王俊凯", "王源",
        "易烊千玺", "蔡徐坤", "王一博", "肖战", "李现"
    ]
    
    # 预设的健康状况描述
    HEALTH_STATUSES = [
        "健康状况良好，无重大疾病史",
        "轻度高血压，需定期监测",
        "糖尿病患者，血糖控制良好",
        "关节炎患者，运动需注意保护关节",
        "哮喘患者，需携带急救药物",
        "曾经做过阑尾炎手术，已完全康复",
        "颈椎不适，建议减少长时间低头",
        "腰椎间盘突出，避免剧烈运动",
        "过敏体质，对花粉和海鲜过敏",
        "心脏早搏，建议避免高强度运动"
    ]
    
    # 预设的课程名称
    COURSES = [
        ("瑜伽", "团课"),
        ("动感单车", "团课"),
        ("普拉提", "团课"),
        ("搏击操", "团课"),
        ("爵士舞", "团课"),
        ("拉丁舞", "团课"),
        ("杠铃操", "团课"),
        ("游泳课", "团课"),
        ("增肌训练", "私教"),
        ("减脂训练", "私教"),
        ("塑形训练", "私教"),
        ("康复训练", "私教"),
        ("功能性训练", "私教"),
        ("拳击训练", "私教"),
        ("拉伸放松", "私教")
    ]
    
    # 预设的教练名称
    COACHES = ["张教练", "李教练", "王教练", "刘教练", "陈教练", "杨教练", "赵教练"]
    
    # 消费类型
    CONSUMPTION_TYPES = ["办卡", "续卡", "私教", "团课", "商品", "其他"]
    
    # 运动目标类型
    GOAL_TYPES = ["减肥", "增肌", "塑形", "康复", "其他"]
    
    def __init__(self):
        pass
    
    def generate_phone(self) -> str:
        """
        生成随机手机号
        """
        prefixes = ["138", "139", "136", "137", "150", "151", "152", "158", "159", "186", "187", "188", "130", "131"]
        prefix = random.choice(prefixes)
        suffix = "".join(random.choices("0123456789", k=8))
        return prefix + suffix
    
    def generate_id_card(self) -> str:
        """
        生成随机身份证号（测试用）
        """
        # 地区码（简化）
        area_codes = ["110101", "110102", "110105", "310101", "310104", "440103", "440304", "320102"]
        area = random.choice(area_codes)
        
        # 出生日期（18-60岁）
        today = datetime.now()
        start_date = today - timedelta(days=60 * 365)
        end_date = today - timedelta(days=18 * 365)
        random_days = random.randint(0, (end_date - start_date).days)
        birth_date = start_date + timedelta(days=random_days)
        birth_str = birth_date.strftime("%Y%m%d")
        
        # 顺序码
        sequence = str(random.randint(100, 999))
        
        # 校验码（简化处理，实际需要计算）
        check_digit = str(random.randint(0, 9))
        
        return area + birth_str + sequence + check_digit
    
    def generate_date(self, start_years: int = 5) -> date:
        """
        生成随机日期
        Args:
            start_years: 从几年前开始
        """
        today = datetime.now().date()
        start_date = today - timedelta(days=start_years * 365)
        random_days = random.randint(0, (today - start_date).days)
        return start_date + timedelta(days=random_days)
    
    def generate_member(
        self,
        db: Session,
        status: Optional[MemberStatus] = None,
        registration_channel: Optional[RegistrationChannel] = None,
        is_verified: bool = None
    ) -> Member:
        """
        生成单个会员测试数据
        """
        # 生成唯一手机号
        while True:
            phone = self.generate_phone()
            existing = db.query(Member).filter(Member.phone == phone).first()
            if not existing:
                break
        
        name = random.choice(self.CHINESE_NAMES)
        gender = random.choice(["男", "女"])
        
        member = Member(
            name=name,
            phone=phone,
            id_card=self.generate_id_card(),
            email=f"{name.lower().replace(' ', '')}@example.com" if random.choice([True, False]) else None,
            gender=gender,
            birth_date=self.generate_date(start_years=random.randint(18, 50)),
            address=f"北京市{random.choice(['朝阳区', '海淀区', '西城区', '东城区', '丰台区'])}某街道{random.randint(1, 100)}号",
            health_status=random.choice(self.HEALTH_STATUSES),
            allergies="青霉素过敏" if random.choice([True, False]) else None,
            emergency_contact=random.choice(self.CHINESE_NAMES),
            emergency_phone=self.generate_phone(),
            registration_channel=registration_channel or random.choice([RegistrationChannel.ONLINE, RegistrationChannel.OFFLINE]),
            status=status or MemberStatus.ACTIVE,
            is_verified=1 if is_verified is None or is_verified else 0,
            verification_method=VerificationMethod.PHONE if is_verified or random.choice([True, False]) else None,
            current_level=random.choice(["bronze", "silver", "gold"]),
            total_consumption=random.randint(0, 5000000),  # 0-50000元
            total_visits=random.randint(0, 500),
        )
        
        db.add(member)
        db.commit()
        db.refresh(member)
        
        return member
    
    def generate_members(
        self,
        db: Session,
        count: int = 10
    ) -> List[Member]:
        """
        批量生成会员测试数据
        """
        members = []
        for _ in range(count):
            member = self.generate_member(db)
            members.append(member)
        return members
    
    def generate_physical_test(
        self,
        db: Session,
        member_id: int
    ) -> PhysicalTest:
        """
        生成体测数据
        """
        # 生成基本数据
        height = Decimal(str(round(random.uniform(150.0, 195.0), 2)))
        weight = Decimal(str(round(random.uniform(45.0, 100.0), 2)))
        height_m = height / Decimal("100")
        bmi = weight / (height_m * height_m)
        
        test = PhysicalTest(
            member_id=member_id,
            test_date=self.generate_date(start_years=1),
            height=height,
            weight=weight,
            bmi=Decimal(str(round(bmi, 2))),
            body_fat=Decimal(str(round(random.uniform(10.0, 35.0), 2))),
            muscle_mass=Decimal(str(round(random.uniform(25.0, 60.0), 2))),
            bone_mass=Decimal(str(round(random.uniform(2.0, 5.0), 2))),
            body_water=Decimal(str(round(random.uniform(25.0, 50.0), 2))),
            resting_heart_rate=random.randint(50, 90),
            blood_pressure_systolic=random.randint(100, 150),
            blood_pressure_diastolic=random.randint(60, 95),
            vital_capacity=Decimal(str(round(random.uniform(3.0, 6.0), 2))),
            grip_strength=Decimal(str(round(random.uniform(20.0, 60.0), 2))),
            sit_and_reach=Decimal(str(round(random.uniform(-5.0, 25.0), 1))),
            tester=random.choice(self.COACHES),
            notes="体测数据正常" if random.choice([True, False]) else None
        )
        
        db.add(test)
        db.commit()
        db.refresh(test)
        
        return test
    
    def generate_fitness_goal(
        self,
        db: Session,
        member_id: int
    ) -> FitnessGoal:
        """
        生成运动目标
        """
        goal_type = random.choice(self.GOAL_TYPES)
        start_date = self.generate_date(start_years=1)
        target_date = start_date + timedelta(days=random.randint(30, 365))
        
        if goal_type == "减肥":
            target_value = Decimal(str(random.randint(5, 30)))
            current_value = Decimal(str(random.randint(0, int(target_value))))
            unit = "kg"
        elif goal_type == "增肌":
            target_value = Decimal(str(random.randint(2, 15)))
            current_value = Decimal(str(random.randint(0, int(target_value))))
            unit = "kg"
        else:
            target_value = None
            current_value = None
            unit = None
        
        goal = FitnessGoal(
            member_id=member_id,
            goal_type=goal_type,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
            start_date=start_date,
            target_date=target_date,
            actual_completion_date=target_date if random.choice([True, False]) else None,
            status=random.choice(["active", "achieved", "cancelled"]),
            progress=random.randint(0, 100),
            description=f"完成{goal_type}目标",
            notes=None
        )
        
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        return goal
    
    def generate_consumption_record(
        self,
        db: Session,
        member_id: int,
        member_level: str = "bronze"
    ) -> ConsumptionRecord:
        """
        生成消费记录
        """
        consumption_type = random.choice(self.CONSUMPTION_TYPES)
        
        # 根据消费类型生成金额
        if consumption_type == "办卡":
            item_name = random.choice(["年卡", "半年卡", "季卡", "月卡"])
            amount_map = {"年卡": 360000, "半年卡": 200000, "季卡": 120000, "月卡": 45000}
            amount = amount_map[item_name]
        elif consumption_type == "私教":
            item_name = f"私教课程 x{random.randint(1, 20)}节"
            amount = random.randint(20000, 50000) * (item_name.count("x") if "x" in item_name else 1)
            amount = min(amount, 500000)
        elif consumption_type == "团课":
            item_name = random.choice(["瑜伽月卡", "动感单车月卡", "普拉提月卡"])
            amount = random.randint(30000, 80000)
        elif consumption_type == "商品":
            item_name = random.choice(["运动蛋白粉", "健身手套", "运动水杯", "瑜伽垫", "运动毛巾"])
            amount = random.randint(1000, 50000)
        else:
            item_name = "其他消费"
            amount = random.randint(1000, 100000)
        
        # 计算折扣
        discount_rates = {"bronze": 1.0, "silver": 0.9, "gold": 0.8}
        discount_rate = discount_rates.get(member_level, 1.0)
        discount_amount = int(amount * (1 - discount_rate))
        actual_amount = int(amount * discount_rate)
        
        record = ConsumptionRecord(
            member_id=member_id,
            consumption_type=consumption_type,
            item_name=item_name,
            amount=amount,
            discount_amount=discount_amount,
            actual_amount=actual_amount,
            payment_method=random.choice(["现金", "微信", "支付宝", "刷卡"]),
            transaction_no=f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}",
            operator=random.choice(["前台小美", "前台小张", "管理员"]),
            notes=None,
            consumption_time=datetime.now() - timedelta(days=random.randint(0, 365))
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
    
    def generate_course_participation(
        self,
        db: Session,
        member_id: int
    ) -> CourseParticipation:
        """
        生成课程参与记录
        """
        course_name, course_type = random.choice(self.COURSES)
        participation_date = self.generate_date(start_years=1)
        
        # 随机时间
        hour = random.randint(8, 21)
        minute = random.choice([0, 30])
        start_time = f"{hour:02d}:{minute:02d}"
        duration = random.choice([45, 60, 90])
        end_hour = hour + duration // 60
        end_minute = (minute + duration % 60) % 60
        end_time = f"{end_hour:02d}:{end_minute:02d}"
        
        participation = CourseParticipation(
            member_id=member_id,
            course_name=course_name,
            course_type=course_type,
            coach_name=random.choice(self.COACHES),
            participation_date=participation_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            status=random.choice(["attended", "absent", "cancelled"]),
            rating=random.randint(1, 5) if random.choice([True, False]) else None,
            feedback="教练很专业，课程体验很好" if random.choice([True, False]) else None
        )
        
        db.add(participation)
        db.commit()
        db.refresh(participation)
        
        return participation
    
    def generate_complete_member_data(
        self,
        db: Session,
        member_count: int = 10,
        tests_per_member: int = 3,
        goals_per_member: int = 2,
        consumptions_per_member: int = 5,
        courses_per_member: int = 8
    ) -> dict:
        """
        生成完整的会员测试数据
        包含会员基本信息、体测数据、运动目标、消费记录、课程参与
        """
        result = {
            "members": [],
            "physical_tests": [],
            "fitness_goals": [],
            "consumption_records": [],
            "course_participations": []
        }
        
        for _ in range(member_count):
            # 生成会员
            member = self.generate_member(db)
            result["members"].append(member)
            
            # 生成体测数据
            for _ in range(tests_per_member):
                test = self.generate_physical_test(db, member.id)
                result["physical_tests"].append(test)
            
            # 生成运动目标
            for _ in range(goals_per_member):
                goal = self.generate_fitness_goal(db, member.id)
                result["fitness_goals"].append(goal)
            
            # 生成消费记录
            for _ in range(consumptions_per_member):
                record = self.generate_consumption_record(db, member.id, member.current_level)
                result["consumption_records"].append(record)
            
            # 生成课程参与记录
            for _ in range(courses_per_member):
                participation = self.generate_course_participation(db, member.id)
                result["course_participations"].append(participation)
        
        return result


# 创建全局实例
test_data_generator = TestDataGenerator()
