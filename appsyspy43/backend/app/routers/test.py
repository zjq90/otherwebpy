"""
测试辅助功能路由模块
提供测试数据生成、系统状态检查等辅助功能
注意：此模块仅用于开发环境测试，生产环境应禁用
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.database import get_db, init_db
from app.models.user import User, UserRole, UserStatus
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.models.transport_task import TransportTask, TaskStatus
from app.models.location_record import LocationRecord
from app.models.task_update import TaskUpdate
from app.schemas.common import ApiResponse, MessageResponse
from app.utils.security import get_password_hash
from app.config import settings

router = APIRouter(
    prefix="/api/test",
    tags=["测试辅助功能"],
    responses={404: {"description": "未找到"}},
)

# 测试数据
TEST_ADDRESSES = [
    {"name": "北京市朝阳区钢材仓库", "lat": 39.9042, "lon": 116.4074},
    {"name": "北京市海淀区建筑工地", "lat": 39.9542, "lon": 116.3074},
    {"name": "北京市丰台区物流中心", "lat": 39.8542, "lon": 116.2874},
    {"name": "北京市大兴区工业园", "lat": 39.7542, "lon": 116.3574},
    {"name": "北京市通州区货运站", "lat": 39.9242, "lon": 116.6074},
    {"name": "北京市顺义区配送中心", "lat": 40.1242, "lon": 116.6574},
    {"name": "北京市昌平区建材市场", "lat": 40.2242, "lon": 116.2374},
    {"name": "北京市房山区钢材市场", "lat": 39.7042, "lon": 116.1374},
]

TEST_CARGO_TYPES = [
    "钢材", "水泥", "砂石", "木材", "瓷砖", "玻璃", "电线电缆", "水管",
    "门窗", "涂料", "保温材料", "防水材料", "钢筋", "钢板", "钢管",
]

TEST_DRIVER_NAMES = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
]

TEST_DISPATCHER_NAMES = [
    "刘调度", "陈调度", "杨调度", "黄调度",
]

TEST_PLATE_NUMBERS = [
    "京A12345", "京B67890", "京C11111", "京D22222", "京E33333",
    "京F44444", "京G55555", "京H66666",
]

TEST_VEHICLE_NAMES = [
    "重型卡车一号", "重型卡车二号", "厢式货车一号", "厢式货车二号",
    "挂车一号", "挂车二号", "轻型货车一号", "轻型货车二号",
]


@router.post("/init-db", response_model=ApiResponse[MessageResponse])
async def initialize_database(
    db: AsyncSession = Depends(get_db),
):
    """
    初始化数据库
    创建所有表结构
    """
    await init_db()
    
    return ApiResponse(
        code=200,
        message="数据库初始化成功",
        data=MessageResponse(message="数据库表已创建", success=True),
    )


@router.post("/generate-test-data", response_model=ApiResponse[dict])
async def generate_test_data(
    db: AsyncSession = Depends(get_db),
):
    """
    生成测试数据
    创建管理员、调度员、司机、车辆、运输任务等测试数据
    """
    # 1. 创建管理员
    admin = User(
        username="admin",
        password_hash=get_password_hash("123456"),
        real_name="系统管理员",
        phone="13800000001",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(admin)
    await db.flush()
    
    # 2. 创建调度员
    dispatchers = []
    for i, name in enumerate(TEST_DISPATCHER_NAMES):
        dispatcher = User(
            username=f"dispatcher{i+1}",
            password_hash=get_password_hash("123456"),
            real_name=name,
            phone=f"1380000100{i+1}",
            role=UserRole.DISPATCHER,
            status=UserStatus.ACTIVE,
        )
        db.add(dispatcher)
        dispatchers.append(dispatcher)
    await db.flush()
    
    # 3. 创建司机
    drivers = []
    for i, name in enumerate(TEST_DRIVER_NAMES):
        driver = User(
            username=f"driver{i+1}",
            password_hash=get_password_hash("123456"),
            real_name=name,
            phone=f"1380000200{i+1}",
            role=UserRole.DRIVER,
            status=UserStatus.IDLE,
            driver_license=f"A12345678{i+1:02d}",
        )
        db.add(driver)
        drivers.append(driver)
    await db.flush()
    
    # 4. 创建车辆
    vehicles = []
    vehicle_types = [VehicleType.TRUCK, VehicleType.VAN, VehicleType.TRAILER, VehicleType.TRUCK]
    for i in range(8):
        vehicle = Vehicle(
            plate_number=TEST_PLATE_NUMBERS[i],
            vehicle_name=TEST_VEHICLE_NAMES[i],
            vehicle_type=vehicle_types[i % len(vehicle_types)],
            load_capacity=Decimal(str(random.randint(10, 30))),
            volume=Decimal(str(random.randint(30, 80))),
            driver_id=drivers[i].id if i < len(drivers) else None,
            status=VehicleStatus.IDLE,
            current_latitude=Decimal(str(TEST_ADDRESSES[i % len(TEST_ADDRESSES)]["lat"])),
            current_longitude=Decimal(str(TEST_ADDRESSES[i % len(TEST_ADDRESSES)]["lon"])),
            current_address=TEST_ADDRESSES[i % len(TEST_ADDRESSES)]["name"],
        )
        db.add(vehicle)
        vehicles.append(vehicle)
    await db.flush()
    
    # 更新司机的车辆关联
    for i, driver in enumerate(drivers):
        if i < len(vehicles):
            driver.vehicle_id = vehicles[i].id
    
    # 5. 创建运输任务
    tasks = []
    now = datetime.utcnow()
    
    # 待分配任务
    for i in range(3):
        loading_addr = random.choice(TEST_ADDRESSES)
        unloading_addr = random.choice([a for a in TEST_ADDRESSES if a != loading_addr])
        
        task = TransportTask(
            task_no=f"TASK{now.strftime('%Y%m%d')}{i+1:04d}",
            task_name=f"{random.choice(TEST_CARGO_TYPES)}运输任务 - {i+1}",
            task_description=f"运输{random.choice(TEST_CARGO_TYPES)}到目的地",
            cargo_name=random.choice(TEST_CARGO_TYPES),
            cargo_weight=Decimal(str(random.randint(5, 25))),
            cargo_volume=Decimal(str(random.randint(10, 50))),
            cargo_quantity=random.randint(10, 100),
            loading_address=loading_addr["name"],
            loading_latitude=Decimal(str(loading_addr["lat"])),
            loading_longitude=Decimal(str(loading_addr["lon"])),
            loading_contact="张经理",
            loading_phone="13800138001",
            unloading_address=unloading_addr["name"],
            unloading_latitude=Decimal(str(unloading_addr["lat"])),
            unloading_longitude=Decimal(str(unloading_addr["lon"])),
            unloading_contact="李工长",
            unloading_phone="13800138002",
            scheduled_departure_time=now + timedelta(hours=random.randint(1, 24)),
            scheduled_arrival_time=now + timedelta(hours=random.randint(3, 48)),
            dispatcher_id=dispatchers[0].id,
            status=TaskStatus.PENDING,
        )
        db.add(task)
        tasks.append(task)
    
    # 已分配任务
    for i in range(2):
        loading_addr = random.choice(TEST_ADDRESSES)
        unloading_addr = random.choice([a for a in TEST_ADDRESSES if a != loading_addr])
        driver_idx = i + 3
        vehicle = vehicles[driver_idx]
        
        task = TransportTask(
            task_no=f"TASK{now.strftime('%Y%m%d')}{100+i+1:04d}",
            task_name=f"{random.choice(TEST_CARGO_TYPES)}运输任务 - 已分配{i+1}",
            task_description=f"运输{random.choice(TEST_CARGO_TYPES)}到目的地",
            cargo_name=random.choice(TEST_CARGO_TYPES),
            cargo_weight=Decimal(str(random.randint(5, 25))),
            cargo_volume=Decimal(str(random.randint(10, 50))),
            cargo_quantity=random.randint(10, 100),
            loading_address=loading_addr["name"],
            loading_latitude=Decimal(str(loading_addr["lat"])),
            loading_longitude=Decimal(str(loading_addr["lon"])),
            loading_contact="张经理",
            loading_phone="13800138001",
            unloading_address=unloading_addr["name"],
            unloading_latitude=Decimal(str(unloading_addr["lat"])),
            unloading_longitude=Decimal(str(unloading_addr["lon"])),
            unloading_contact="李工长",
            unloading_phone="13800138002",
            scheduled_departure_time=now + timedelta(hours=random.randint(1, 24)),
            scheduled_arrival_time=now + timedelta(hours=random.randint(3, 48)),
            vehicle_id=vehicle.id,
            driver_id=drivers[driver_idx].id,
            dispatcher_id=dispatchers[0].id,
            status=TaskStatus.ASSIGNED,
        )
        db.add(task)
        tasks.append(task)
        
        # 更新车辆和司机状态
        vehicle.status = VehicleStatus.IN_TRANSIT
        drivers[driver_idx].status = UserStatus.BUSY
    
    # 进行中任务
    for i in range(2):
        loading_addr = random.choice(TEST_ADDRESSES)
        unloading_addr = random.choice([a for a in TEST_ADDRESSES if a != loading_addr])
        driver_idx = i + 5
        vehicle = vehicles[driver_idx]
        
        task = TransportTask(
            task_no=f"TASK{now.strftime('%Y%m%d')}{200+i+1:04d}",
            task_name=f"{random.choice(TEST_CARGO_TYPES)}运输任务 - 进行中{i+1}",
            task_description=f"运输{random.choice(TEST_CARGO_TYPES)}到目的地",
            cargo_name=random.choice(TEST_CARGO_TYPES),
            cargo_weight=Decimal(str(random.randint(5, 25))),
            cargo_volume=Decimal(str(random.randint(10, 50))),
            cargo_quantity=random.randint(10, 100),
            loading_address=loading_addr["name"],
            loading_latitude=Decimal(str(loading_addr["lat"])),
            loading_longitude=Decimal(str(loading_addr["lon"])),
            loading_contact="张经理",
            loading_phone="13800138001",
            unloading_address=unloading_addr["name"],
            unloading_latitude=Decimal(str(unloading_addr["lat"])),
            unloading_longitude=Decimal(str(unloading_addr["lon"])),
            unloading_contact="李工长",
            unloading_phone="13800138002",
            actual_departure_time=now - timedelta(hours=random.randint(1, 5)),
            estimated_arrival_time=now + timedelta(hours=random.randint(1, 5)),
            vehicle_id=vehicle.id,
            driver_id=drivers[driver_idx].id,
            dispatcher_id=dispatchers[0].id,
            status=TaskStatus.DEPARTED,
        )
        db.add(task)
        tasks.append(task)
        
        # 更新车辆和司机状态
        vehicle.status = VehicleStatus.IN_TRANSIT
        drivers[driver_idx].status = UserStatus.BUSY
        
        # 生成位置记录
        base_lat = loading_addr["lat"]
        base_lon = loading_addr["lon"]
        for j in range(10):
            location = LocationRecord(
                vehicle_id=vehicle.id,
                user_id=drivers[driver_idx].id,
                transport_task_id=task.id,
                latitude=Decimal(str(base_lat + (j * 0.005))),
                longitude=Decimal(str(base_lon + (j * 0.005))),
                address=f"行驶中 - 位置{j+1}",
                speed=Decimal(str(random.randint(40, 80))),
                direction=Decimal(str(random.randint(0, 360))),
                recorded_at=now - timedelta(hours=2 - j * 0.2),
            )
            db.add(location)
    
    # 已完成任务
    for i in range(1):
        loading_addr = random.choice(TEST_ADDRESSES)
        unloading_addr = random.choice([a for a in TEST_ADDRESSES if a != loading_addr])
        driver_idx = i + 7
        vehicle = vehicles[driver_idx]
        
        task = TransportTask(
            task_no=f"TASK{now.strftime('%Y%m%d')}{300+i+1:04d}",
            task_name=f"{random.choice(TEST_CARGO_TYPES)}运输任务 - 已完成{i+1}",
            task_description=f"运输{random.choice(TEST_CARGO_TYPES)}到目的地",
            cargo_name=random.choice(TEST_CARGO_TYPES),
            cargo_weight=Decimal(str(random.randint(5, 25))),
            cargo_volume=Decimal(str(random.randint(10, 50))),
            cargo_quantity=random.randint(10, 100),
            loading_address=loading_addr["name"],
            loading_latitude=Decimal(str(loading_addr["lat"])),
            loading_longitude=Decimal(str(loading_addr["lon"])),
            loading_contact="张经理",
            loading_phone="13800138001",
            unloading_address=unloading_addr["name"],
            unloading_latitude=Decimal(str(unloading_addr["lat"])),
            unloading_longitude=Decimal(str(unloading_addr["lon"])),
            unloading_contact="李工长",
            unloading_phone="13800138002",
            actual_departure_time=now - timedelta(hours=10),
            actual_arrival_time=now - timedelta(hours=6),
            actual_unload_time=now - timedelta(hours=4),
            completed_time=now - timedelta(hours=3),
            vehicle_id=vehicle.id,
            driver_id=drivers[driver_idx].id,
            dispatcher_id=dispatchers[0].id,
            status=TaskStatus.COMPLETED,
        )
        db.add(task)
        tasks.append(task)
        
        # 创建任务更新记录
        status_transitions = [
            (TaskStatus.PENDING, TaskStatus.ASSIGNED, "任务分配", "任务已分配给司机"),
            (TaskStatus.ASSIGNED, TaskStatus.CONFIRMED, "任务确认", "司机已确认接受任务"),
            (TaskStatus.CONFIRMED, TaskStatus.DEPARTED, "已出发", "司机已从装货点出发"),
            (TaskStatus.DEPARTED, TaskStatus.ARRIVED, "已到达", "已到达卸货点"),
            (TaskStatus.ARRIVED, TaskStatus.UNLOADING, "卸料中", "开始卸料"),
            (TaskStatus.UNLOADING, TaskStatus.COMPLETED, "已完成", "卸料完成，任务结束"),
        ]
        
        for j, (old_status, new_status, update_type, desc) in enumerate(status_transitions):
            task_update = TaskUpdate(
                transport_task_id=task.id,
                user_id=drivers[driver_idx].id if j > 0 else dispatchers[0].id,
                old_status=old_status,
                new_status=new_status,
                update_type=update_type,
                description=desc,
                created_at=now - timedelta(hours=12 - j * 2),
            )
            db.add(task_update)
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="测试数据生成成功",
        data={
            "admin_count": 1,
            "dispatcher_count": len(dispatchers),
            "driver_count": len(drivers),
            "vehicle_count": len(vehicles),
            "task_count": len(tasks),
            "login_info": {
                "admin": {"username": "admin", "password": "123456", "role": "管理员"},
                "dispatcher": {"username": "dispatcher1", "password": "123456", "role": "调度员"},
                "driver": {"username": "driver1", "password": "123456", "role": "司机"},
            }
        },
    )


@router.get("/system-status", response_model=ApiResponse[dict])
async def get_system_status(
    db: AsyncSession = Depends(get_db),
):
    """
    获取系统状态
    用于检查系统运行状态和数据统计
    """
    # 统计用户数量
    user_count_query = select(func.count()).select_from(User).where(User.is_deleted == False)
    user_count_result = await db.execute(user_count_query)
    user_count = user_count_result.scalar()
    
    # 按角色统计用户
    role_counts = {}
    for role in UserRole:
        count_query = select(func.count()).select_from(User).where(
            User.is_deleted == False,
            User.role == role,
        )
        count_result = await db.execute(count_query)
        role_counts[role.value] = count_result.scalar()
    
    # 统计车辆数量
    vehicle_count_query = select(func.count()).select_from(Vehicle).where(Vehicle.is_deleted == False)
    vehicle_count_result = await db.execute(vehicle_count_query)
    vehicle_count = vehicle_count_result.scalar()
    
    # 按状态统计车辆
    vehicle_status_counts = {}
    for vs in VehicleStatus:
        count_query = select(func.count()).select_from(Vehicle).where(
            Vehicle.is_deleted == False,
            Vehicle.status == vs,
        )
        count_result = await db.execute(count_query)
        vehicle_status_counts[vs.value] = count_result.scalar()
    
    # 统计任务数量
    task_count_query = select(func.count()).select_from(TransportTask).where(TransportTask.is_deleted == False)
    task_count_result = await db.execute(task_count_query)
    task_count = task_count_result.scalar()
    
    # 按状态统计任务
    task_status_counts = {}
    for ts in TaskStatus:
        count_query = select(func.count()).select_from(TransportTask).where(
            TransportTask.is_deleted == False,
            TransportTask.status == ts,
        )
        count_result = await db.execute(count_query)
        task_status_counts[ts.value] = count_result.scalar()
    
    # 统计位置记录数量
    location_count_query = select(func.count()).select_from(LocationRecord)
    location_count_result = await db.execute(location_count_query)
    location_count = location_count_result.scalar()
    
    return ApiResponse(
        code=200,
        message="系统状态获取成功",
        data={
            "system_info": {
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "debug": settings.DEBUG,
            },
            "statistics": {
                "total_users": user_count,
                "users_by_role": role_counts,
                "total_vehicles": vehicle_count,
                "vehicles_by_status": vehicle_status_counts,
                "total_tasks": task_count,
                "tasks_by_status": task_status_counts,
                "total_location_records": location_count,
            },
        },
    )


@router.delete("/clear-test-data", response_model=ApiResponse[MessageResponse])
async def clear_test_data(
    db: AsyncSession = Depends(get_db),
):
    """
    清除测试数据
    注意：此操作会删除所有数据，请谨慎使用
    """
    # 删除所有数据（按依赖顺序）
    from sqlalchemy import delete
    
    # 删除任务更新记录
    await db.execute(delete(TaskUpdate))
    
    # 删除位置记录
    await db.execute(delete(LocationRecord))
    
    # 删除运输任务
    await db.execute(delete(TransportTask))
    
    # 删除车辆
    await db.execute(delete(Vehicle))
    
    # 删除用户
    await db.execute(delete(User))
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="测试数据已清除",
        data=MessageResponse(message="所有测试数据已清除", success=True),
    )
