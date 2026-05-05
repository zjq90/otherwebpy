"""
系统初始化数据脚本
用于初始化角色、权限、管理员用户和测试数据
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .config import settings
from .database import Base
from .models.user_models import User, Role, Permission, user_role, role_permission
from .models.business_models import (
    ProductionTask, ProductionRecord,
    MaterialInspection, QualityReport, QualityAlert,
    MaterialInventory, PurchaseRequest, Supplier,
    Vehicle, TransportTask
)
from .utils.security import get_password_hash


# 定义角色数据
ROLES_DATA = [
    {"name": "管理员", "code": "admin", "description": "系统管理员，拥有全部权限"},
    {"name": "拌合站操作员", "code": "mixer_operator", "description": "负责生产任务执行和记录提交"},
    {"name": "试验检测员", "code": "quality_inspector", "description": "负责原材料检验和质量报告"},
    {"name": "物资采购员", "code": "material_purchaser", "description": "负责库存管理和采购申请"},
    {"name": "资源调度员", "code": "resource_scheduler", "description": "负责车辆调度和运输任务安排"},
]

# 定义权限数据
PERMISSIONS_DATA = [
    # 用户管理权限
    {"name": "用户查看", "code": "user:view", "description": "查看用户列表", "module": "用户管理"},
    {"name": "用户创建", "code": "user:create", "description": "创建新用户", "module": "用户管理"},
    {"name": "用户编辑", "code": "user:edit", "description": "编辑用户信息", "module": "用户管理"},
    {"name": "用户删除", "code": "user:delete", "description": "删除用户", "module": "用户管理"},
    {"name": "角色管理", "code": "role:manage", "description": "管理角色权限", "module": "用户管理"},
    
    # 生产管理权限
    {"name": "生产任务查看", "code": "production:view", "description": "查看生产任务", "module": "生产管理"},
    {"name": "生产任务创建", "code": "production:create", "description": "创建生产任务", "module": "生产管理"},
    {"name": "生产任务编辑", "code": "production:edit", "description": "编辑生产任务", "module": "生产管理"},
    {"name": "生产记录提交", "code": "production:record", "description": "提交生产记录", "module": "生产管理"},
    
    # 质量检测权限
    {"name": "原材料检验", "code": "quality:inspection", "description": "录入原材料检验数据", "module": "质量管理"},
    {"name": "质量报告查看", "code": "quality:report:view", "description": "查看质量报告", "module": "质量管理"},
    {"name": "质量报告创建", "code": "quality:report:create", "description": "创建质量报告", "module": "质量管理"},
    {"name": "质量预警发起", "code": "quality:alert", "description": "发起质量预警", "module": "质量管理"},
    {"name": "质量预警处理", "code": "quality:alert:handle", "description": "处理质量预警", "module": "质量管理"},
    
    # 物资采购权限
    {"name": "库存查看", "code": "material:inventory:view", "description": "查看原材料库存", "module": "物资管理"},
    {"name": "库存编辑", "code": "material:inventory:edit", "description": "编辑库存信息", "module": "物资管理"},
    {"name": "采购申请", "code": "material:purchase", "description": "提交采购申请", "module": "物资管理"},
    {"name": "采购审批", "code": "material:approve", "description": "审批采购申请", "module": "物资管理"},
    {"name": "供应商管理", "code": "material:supplier", "description": "管理供应商信息", "module": "物资管理"},
    
    # 资源调度权限
    {"name": "车辆查看", "code": "transport:vehicle:view", "description": "查看车辆信息", "module": "资源调度"},
    {"name": "车辆管理", "code": "transport:vehicle:manage", "description": "管理车辆信息", "module": "资源调度"},
    {"name": "运输任务安排", "code": "transport:task:create", "description": "安排运输任务", "module": "资源调度"},
    {"name": "运输进度更新", "code": "transport:task:update", "description": "更新运输进度", "module": "资源调度"},
    
    # 流程审批权限
    {"name": "流程审批", "code": "process:approve", "description": "审批关键流程", "module": "流程管理"},
]

# 角色权限分配
ROLE_PERMISSIONS = {
    "admin": [p["code"] for p in PERMISSIONS_DATA],  # 管理员拥有全部权限
    "mixer_operator": [
        "production:view", "production:record"
    ],
    "quality_inspector": [
        "quality:inspection", "quality:report:view", "quality:report:create", 
        "quality:alert"
    ],
    "material_purchaser": [
        "material:inventory:view", "material:inventory:edit",
        "material:purchase", "material:supplier"
    ],
    "resource_scheduler": [
        "transport:vehicle:view", "transport:task:create", "transport:task:update"
    ],
}


async def init_roles_and_permissions(db: AsyncSession):
    """
    初始化角色和权限数据
    """
    # 检查是否已有数据
    result = await db.execute(select(Role))
    existing_roles = result.scalars().all()
    if existing_roles:
        print("角色数据已存在，跳过初始化")
        return
    
    # 创建权限
    permissions_map = {}
    for perm_data in PERMISSIONS_DATA:
        perm = Permission(**perm_data)
        db.add(perm)
        permissions_map[perm_data["code"]] = perm
    
    await db.flush()
    
    # 创建角色并分配权限
    for role_data in ROLES_DATA:
        role = Role(**role_data)
        perm_codes = ROLE_PERMISSIONS.get(role_data["code"], [])
        role.permissions = [permissions_map[code] for code in perm_codes if code in permissions_map]
        db.add(role)
    
    await db.commit()
    print("角色和权限数据初始化完成")


async def init_admin_user(db: AsyncSession):
    """
    初始化管理员用户
    """
    result = await db.execute(
        select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
    )
    existing_admin = result.scalar_one_or_none()
    if existing_admin:
        print("管理员用户已存在，跳过初始化")
        return
    
    # 查询管理员角色
    result = await db.execute(
        select(Role).where(Role.code == "admin")
    )
    admin_role = result.scalar_one_or_none()
    
    if not admin_role:
        print("管理员角色不存在，请先初始化角色数据")
        return
    
    # 创建管理员用户
    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
        phone=settings.DEFAULT_ADMIN_PHONE,
        real_name="系统管理员",
        is_verified=True,
        is_first_login=False,
        roles=[admin_role]
    )
    db.add(admin)
    await db.commit()
    print(f"管理员用户初始化完成：用户名={settings.DEFAULT_ADMIN_USERNAME}, 密码={settings.DEFAULT_ADMIN_PASSWORD}")


async def init_test_users(db: AsyncSession):
    """
    初始化测试用户
    """
    # 检查是否已有测试用户
    result = await db.execute(select(User).where(User.phone == "13900000001"))
    if result.scalar_one_or_none():
        print("测试用户已存在，跳过初始化")
        return
    
    # 查询所有角色
    result = await db.execute(select(Role))
    roles = {r.code: r for r in result.scalars().all()}
    
    # 创建测试用户
    test_users = [
        {
            "username": "operator1",
            "password": "123456",
            "phone": "13900000001",
            "real_name": "张操作员",
            "role_code": "mixer_operator"
        },
        {
            "username": "inspector1",
            "password": "123456",
            "phone": "13900000002",
            "real_name": "李检测员",
            "role_code": "quality_inspector"
        },
        {
            "username": "purchaser1",
            "password": "123456",
            "phone": "13900000003",
            "real_name": "王采购员",
            "role_code": "material_purchaser"
        },
        {
            "username": "scheduler1",
            "password": "123456",
            "phone": "13900000004",
            "real_name": "赵调度员",
            "role_code": "resource_scheduler"
        },
    ]
    
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            phone=user_data["phone"],
            real_name=user_data["real_name"],
            is_verified=True,
            is_first_login=False,
            roles=[roles[user_data["role_code"]]] if user_data["role_code"] in roles else []
        )
        db.add(user)
    
    await db.commit()
    print("测试用户初始化完成，密码均为：123456")


async def init_test_business_data(db: AsyncSession):
    """
    初始化业务测试数据
    """
    # 检查是否已有业务数据
    result = await db.execute(select(MaterialInventory).limit(1))
    if result.scalar_one_or_none():
        print("业务测试数据已存在，跳过初始化")
        return
    
    # 创建原材料库存数据
    inventory_items = [
        MaterialInventory(
            material_code="MAT001",
            material_name="PO42.5水泥",
            material_type="水泥",
            specification="PO42.5",
            unit="吨",
            quantity=500,
            min_warning=100,
            supplier="海螺水泥",
            warehouse="一号仓库"
        ),
        MaterialInventory(
            material_code="MAT002",
            material_name="中砂",
            material_type="砂石",
            specification="中砂",
            unit="立方米",
            quantity=800,
            min_warning=200,
            supplier="本地砂石场",
            warehouse="二号仓库"
        ),
        MaterialInventory(
            material_code="MAT003",
            material_name="5-25mm碎石",
            material_type="砂石",
            specification="5-25mm",
            unit="立方米",
            quantity=600,
            min_warning=150,
            supplier="本地砂石场",
            warehouse="三号仓库"
        ),
        MaterialInventory(
            material_code="MAT004",
            material_name="聚羧酸减水剂",
            material_type="外加剂",
            specification="PC-1",
            unit="吨",
            quantity=50,
            min_warning=10,
            supplier="科之杰",
            warehouse="四号仓库"
        ),
    ]
    for item in inventory_items:
        db.add(item)
    
    # 创建供应商数据
    suppliers = [
        Supplier(
            supplier_code="SUP001",
            supplier_name="海螺水泥有限公司",
            contact_person="张经理",
            phone="13800000001",
            address="安徽省芜湖市",
            business_scope="水泥生产销售",
            credit_rating="A"
        ),
        Supplier(
            supplier_code="SUP002",
            supplier_name="本地砂石场",
            contact_person="李老板",
            phone="13800000002",
            address="本地郊区",
            business_scope="砂石开采销售",
            credit_rating="B"
        ),
        Supplier(
            supplier_code="SUP003",
            supplier_name="科之杰新材料",
            contact_person="王经理",
            phone="13800000003",
            address="福建省厦门市",
            business_scope="外加剂生产销售",
            credit_rating="A"
        ),
    ]
    for supplier in suppliers:
        db.add(supplier)
    
    # 创建车辆数据
    vehicles = [
        Vehicle(
            vehicle_no="京A12345",
            vehicle_type="搅拌车",
            load_capacity=12,
            volume_capacity=8,
            driver_name="王师傅",
            driver_phone="13700000001",
            status="idle",
            current_location="拌合站停车场"
        ),
        Vehicle(
            vehicle_no="京A12346",
            vehicle_type="搅拌车",
            load_capacity=12,
            volume_capacity=8,
            driver_name="李师傅",
            driver_phone="13700000002",
            status="idle",
            current_location="拌合站停车场"
        ),
        Vehicle(
            vehicle_no="京A12347",
            vehicle_type="泵车",
            load_capacity=20,
            driver_name="张师傅",
            driver_phone="13700000003",
            status="idle",
            current_location="拌合站停车场"
        ),
    ]
    for vehicle in vehicles:
        db.add(vehicle)
    
    await db.commit()
    print("业务测试数据初始化完成")


async def init_all_data():
    """
    初始化所有数据
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        await init_roles_and_permissions(session)
        await init_admin_user(session)
        await init_test_users(session)
        await init_test_business_data(session)
    
    await engine.dispose()
    print("所有数据初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_all_data())
