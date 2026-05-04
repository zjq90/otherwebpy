"""
测试数据生成模块
使用Faker库生成模拟测试数据，用于功能测试
"""
import sys
import os

# 设置默认编码为UTF-8，解决Windows下GBK编码问题
if sys.platform == 'win32':
    import io
    # 重新设置stdout/stderr编码
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from faker import Faker
from sqlalchemy.orm import Session
from typing import List
import random
from datetime import datetime, timedelta

from app.config import SessionLocal, engine, Base
from app import models
from app.models import PropertyStatus

# 初始化Faker，使用中文本地化
fake = Faker('zh_CN')

# 预设数据池
HOUSE_TYPES = ['一室一厅', '两室一厅', '两室两厅', '三室一厅', '三室两厅', '四室两厅', '复式', '别墅']
PROPERTY_TYPES = ['商品房', '经济适用房', '回迁房', '公房', '私房', '公寓']
ORIENTATIONS = ['南北通透', '朝南', '朝北', '朝东', '朝西', '东南', '西南']
DECORATIONS = ['毛坯', '简装', '中装', '精装', '豪装']
RELATIONS = ['配偶', '子女', '父母', '兄弟姐妹', '祖父母', '外祖父母', '其他亲属', '非亲属']
VEHICLE_TYPES = ['轿车', 'SUV', 'MPV', '跑车', '货车', '客车', '摩托车', '电动车']
CAR_BRANDS = ['大众', '丰田', '本田', '别克', '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '吉利', '长城', '长安']
CAR_COLORS = ['白色', '黑色', '灰色', '银色', '红色', '蓝色', '棕色', '金色']


def generate_property_projects(db: Session, count: int = 5) -> List[models.PropertyProject]:
    """
    生成物业项目测试数据
    
    Args:
        db: 数据库会话
        count: 生成数量
        
    Returns:
        生成的物业项目列表
    """
    projects = []
    project_prefixes = ['阳光花园', '幸福家园', '锦绣华庭', '翡翠城', '金茂府', '碧桂园', '恒大名都', '万科城', '保利花园', '绿地世纪城']
    
    for i in range(count):
        prefix = random.choice(project_prefixes)
        project = models.PropertyProject(
            name=f"{prefix}{random.randint(1, 10)}期",
            location=fake.address(),
            total_buildings=random.randint(5, 30),
            total_houses=random.randint(100, 1000),
            developer=f"{fake.company()}房地产开发有限公司",
            property_company=f"{fake.company()}物业管理有限公司",
            built_year=random.randint(2000, 2024),
            description=fake.text(max_nb_chars=200)
        )
        db.add(project)
        projects.append(project)
    
    db.commit()
    for project in projects:
        db.refresh(project)
    
    return projects


def generate_properties(
    db: Session, 
    project: models.PropertyProject, 
    count: int = 20
) -> List[models.Property]:
    """
    为指定项目生成房产测试数据
    
    Args:
        db: 数据库会话
        project: 所属物业项目
        count: 生成数量
        
    Returns:
        生成的房产列表
    """
    properties = []
    statuses = [PropertyStatus.VACANT.value, PropertyStatus.RENTED.value, PropertyStatus.OCCUPIED.value]
    
    # 生成楼栋号和房间号
    for i in range(count):
        building_number = str(random.randint(1, project.total_buildings if project.total_buildings > 0 else 10))
        floor = random.randint(1, 30)
        room_number = f"{floor:02d}{random.randint(1, 4):02d}"
        total_floors = random.randint(floor, 35)
        
        property_item = models.Property(
            project_id=project.id,
            building_number=building_number,
            room_number=room_number,
            floor=floor,
            total_floors=total_floors,
            house_type=random.choice(HOUSE_TYPES),
            area=round(random.uniform(30.0, 200.0), 2),
            usable_area=round(random.uniform(25.0, 180.0), 2),
            property_type=random.choice(PROPERTY_TYPES),
            status=random.choices(statuses, weights=[0.3, 0.3, 0.4])[0],
            orientation=random.choice(ORIENTATIONS),
            decoration=random.choice(DECORATIONS),
            remarks=fake.text(max_nb_chars=100) if random.random() > 0.5 else None
        )
        db.add(property_item)
        properties.append(property_item)
    
    db.commit()
    for prop in properties:
        db.refresh(prop)
    
    return properties


def generate_owners(
    db: Session, 
    count: int = 30
) -> List[models.Owner]:
    """
    生成业主/住户测试数据
    
    Args:
        db: 数据库会话
        count: 生成数量
        
    Returns:
        生成的业主/住户列表
    """
    owners = []
    
    for i in range(count):
        is_owner = random.random() > 0.15  # 85%是业主，15%是住户
        owner = models.Owner(
            name=fake.name(),
            id_card=fake.ssn() if random.random() > 0.3 else None,
            phone=fake.phone_number(),
            email=fake.email() if random.random() > 0.5 else None,
            address=fake.address() if random.random() > 0.3 else None,
            is_owner=is_owner
        )
        db.add(owner)
        owners.append(owner)
    
    db.commit()
    for owner in owners:
        db.refresh(owner)
    
    return owners


def generate_family_members(
    db: Session, 
    owner: models.Owner, 
    max_count: int = 5
) -> List[models.FamilyMember]:
    """
    为业主生成家庭成员测试数据
    
    Args:
        db: 数据库会话
        owner: 所属业主
        max_count: 最大生成数量
        
    Returns:
        生成的家庭成员列表
    """
    members = []
    count = random.randint(0, max_count)
    
    for i in range(count):
        is_emergency = random.random() > 0.7
        birth_date = fake.date_of_birth(minimum_age=1, maximum_age=100)
        member = models.FamilyMember(
            owner_id=owner.id,
            name=fake.name(),
            relation=random.choice(RELATIONS),
            phone=fake.phone_number() if random.random() > 0.5 else None,
            id_card=fake.ssn() if random.random() > 0.5 else None,
            gender=random.choice(['男', '女']),
            birth_date=datetime.combine(birth_date, datetime.min.time()),
            is_emergency_contact=is_emergency
        )
        db.add(member)
        members.append(member)
    
    if members:
        db.commit()
        for member in members:
            db.refresh(member)
    
    return members


def generate_vehicles(
    db: Session, 
    owner: models.Owner, 
    max_count: int = 3
) -> List[models.Vehicle]:
    """
    为业主生成车辆测试数据
    
    Args:
        db: 数据库会话
        owner: 所属业主
        max_count: 最大生成数量
        
    Returns:
        生成的车辆列表
    """
    vehicles = []
    count = random.randint(0, max_count)
    
    for i in range(count):
        # 生成车牌号
        provinces = ['京', '沪', '粤', '苏', '浙', '鲁', '豫', '川', '鄂', '湘']
        province = random.choice(provinces)
        letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        plate = f"{province}{random.choice(letters)}{''.join(random.choices('0123456789', k=5))}"
        
        vehicle = models.Vehicle(
            owner_id=owner.id,
            plate_number=plate,
            vehicle_type=random.choice(VEHICLE_TYPES),
            brand=random.choice(CAR_BRANDS),
            model=f"Model{random.randint(1, 10)}",
            color=random.choice(CAR_COLORS),
            parking_space=f"A{random.randint(1, 200)}" if random.random() > 0.3 else None
        )
        db.add(vehicle)
        vehicles.append(vehicle)
    
    if vehicles:
        db.commit()
        for vehicle in vehicles:
            db.refresh(vehicle)
    
    return vehicles


def generate_owner_property_relations(
    db: Session,
    owners: List[models.Owner],
    properties: List[models.Property],
    max_relations_per_owner: int = 3
) -> List[models.OwnerProperty]:
    """
    生成业主与房产的关联关系
    
    Args:
        db: 数据库会话
        owners: 业主列表
        properties: 房产列表
        max_relations_per_owner: 每个业主最大关联数量
        
    Returns:
        生成的关联关系列表
    """
    relations = []
    
    if not owners or not properties:
        return relations
    
    for owner in owners:
        # 只给业主（不是住户）生成房产关联
        if not owner.is_owner:
            continue
            
        relation_count = random.randint(1, max_relations_per_owner)
        selected_properties = random.sample(properties, min(relation_count, len(properties)))
        
        for prop in selected_properties:
            ownership_types = ['全部所有', '共同所有', '按份共有']
            relation = models.OwnerProperty(
                owner_id=owner.id,
                property_id=prop.id,
                ownership_type=random.choice(ownership_types),
                share_ratio=round(random.uniform(10.0, 100.0), 2) if random.random() > 0.7 else 100.0,
                start_date=fake.date_between(start_date='-10y', end_date='today'),
                end_date=None,
                is_primary=random.random() > 0.3
            )
            db.add(relation)
            relations.append(relation)
    
    if relations:
        db.commit()
        for relation in relations:
            db.refresh(relation)
    
    return relations


def generate_all_test_data(db: Session, clear_existing: bool = True):
    """
    生成所有测试数据
    
    Args:
        db: 数据库会话
        clear_existing: 是否清除现有数据
    """
    if clear_existing:
        # 清除现有数据（按依赖关系顺序删除）
        db.query(models.OwnerProperty).delete()
        db.query(models.FamilyMember).delete()
        db.query(models.Vehicle).delete()
        db.query(models.Owner).delete()
        db.query(models.Property).delete()
        db.query(models.PropertyProject).delete()
        db.commit()
        print("已清除现有数据")
    
    print("开始生成测试数据...")
    
    # 1. 生成物业项目
    print("生成物业项目...")
    projects = generate_property_projects(db, count=5)
    print(f"  生成了 {len(projects)} 个物业项目")
    
    # 2. 为每个项目生成房产
    all_properties = []
    for project in projects:
        print(f"为项目 '{project.name}' 生成房产...")
        properties = generate_properties(db, project, count=random.randint(15, 25))
        all_properties.extend(properties)
        print(f"  生成了 {len(properties)} 套房产")
    
    # 3. 生成业主/住户
    print("生成业主/住户...")
    owners = generate_owners(db, count=40)
    print(f"  生成了 {len(owners)} 位业主/住户")
    
    # 4. 为业主生成家庭成员和车辆
    for owner in owners:
        if owner.is_owner:
            # 生成家庭成员
            members = generate_family_members(db, owner, max_count=4)
            if members:
                print(f"  为业主 {owner.name} 生成了 {len(members)} 位家庭成员")
            
            # 生成车辆
            vehicles = generate_vehicles(db, owner, max_count=2)
            if vehicles:
                print(f"  为业主 {owner.name} 生成了 {len(vehicles)} 辆车")
    
    # 5. 生成业主-房产关联
    print("生成业主-房产关联...")
    relations = generate_owner_property_relations(db, owners, all_properties, max_relations_per_owner=2)
    print(f"  生成了 {len(relations)} 个关联关系")
    
    print("\n测试数据生成完成！")
    print(f"  物业项目: {len(projects)} 个")
    print(f"  房产: {len(all_properties)} 套")
    print(f"  业主/住户: {len(owners)} 位")
    print(f"  关联关系: {len(relations)} 个")


if __name__ == "__main__":
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        generate_all_test_data(db, clear_existing=True)
    finally:
        db.close()
