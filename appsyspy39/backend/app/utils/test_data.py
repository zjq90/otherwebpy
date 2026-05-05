"""
测试数据生成模块 - 用于生成测试数据辅助功能测试
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User,
    Task,
    Formula,
    FormulaAdjustment,
    FeedingRecord,
    MixingRecord
)
from app.core.auth import get_password_hash


async def generate_test_users() -> List[dict]:
    """
    生成测试用户数据
    
    Returns:
        List[dict]: 用户信息列表
    """
    users = [
        {
            "username": "admin",
            "password": "admin123",
            "real_name": "系统管理员",
            "phone": "13800138000",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "operator1",
            "password": "123456",
            "real_name": "张操作员",
            "phone": "13800138001",
            "role": "operator",
            "is_active": True
        },
        {
            "username": "operator2",
            "password": "123456",
            "real_name": "李操作员",
            "phone": "13800138002",
            "role": "operator",
            "is_active": True
        },
        {
            "username": "operator3",
            "password": "123456",
            "real_name": "王操作员",
            "phone": "13800138003",
            "role": "operator",
            "is_active": True
        }
    ]
    return users


async def generate_test_formulas() -> List[dict]:
    """
    生成测试配方数据
    
    Returns:
        List[dict]: 配方信息列表
    """
    formulas = [
        {
            "formula_name": "C15普通混凝土配合比",
            "formula_code": "FORM-C15-001",
            "concrete_grade": "C15",
            "water_cement_ratio": 0.65,
            "slump": 120,
            "cement": 250,
            "water": 162.5,
            "sand": 800,
            "stone": 1150,
            "admixture": 5.0,
            "admixture_type": "萘系高效减水剂",
            "fly_ash": 50,
            "mineral_powder": 30,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于垫层、基础等低强度要求部位"
        },
        {
            "formula_name": "C20普通混凝土配合比",
            "formula_code": "FORM-C20-001",
            "concrete_grade": "C20",
            "water_cement_ratio": 0.58,
            "slump": 120,
            "cement": 280,
            "water": 162.4,
            "sand": 780,
            "stone": 1140,
            "admixture": 5.6,
            "admixture_type": "聚羧酸系高效减水剂",
            "fly_ash": 60,
            "mineral_powder": 40,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于一般结构构件"
        },
        {
            "formula_name": "C25普通混凝土配合比",
            "formula_code": "FORM-C25-001",
            "concrete_grade": "C25",
            "water_cement_ratio": 0.52,
            "slump": 140,
            "cement": 310,
            "water": 161.2,
            "sand": 760,
            "stone": 1120,
            "admixture": 6.2,
            "admixture_type": "聚羧酸系高效减水剂",
            "fly_ash": 70,
            "mineral_powder": 50,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于梁、板、柱等主要结构构件"
        },
        {
            "formula_name": "C30普通混凝土配合比",
            "formula_code": "FORM-C30-001",
            "concrete_grade": "C30",
            "water_cement_ratio": 0.47,
            "slump": 160,
            "cement": 340,
            "water": 159.8,
            "sand": 740,
            "stone": 1100,
            "admixture": 6.8,
            "admixture_type": "聚羧酸系高效减水剂",
            "fly_ash": 80,
            "mineral_powder": 60,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于高层建筑、桥梁等重要结构"
        },
        {
            "formula_name": "C35高强度混凝土配合比",
            "formula_code": "FORM-C35-001",
            "concrete_grade": "C35",
            "water_cement_ratio": 0.43,
            "slump": 160,
            "cement": 370,
            "water": 159.1,
            "sand": 720,
            "stone": 1080,
            "admixture": 7.4,
            "admixture_type": "聚羧酸系高性能减水剂",
            "fly_ash": 90,
            "mineral_powder": 70,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于大跨度、重载结构"
        },
        {
            "formula_name": "C40高强度混凝土配合比",
            "formula_code": "FORM-C40-001",
            "concrete_grade": "C40",
            "water_cement_ratio": 0.40,
            "slump": 180,
            "cement": 400,
            "water": 160.0,
            "sand": 700,
            "stone": 1060,
            "admixture": 8.0,
            "admixture_type": "聚羧酸系高性能减水剂",
            "fly_ash": 100,
            "mineral_powder": 80,
            "is_active": True,
            "is_standard": True,
            "remarks": "适用于超高层建筑、大型桥梁"
        },
        {
            "formula_name": "C30泵送混凝土配合比",
            "formula_code": "FORM-C30-PUMP-001",
            "concrete_grade": "C30",
            "water_cement_ratio": 0.48,
            "slump": 200,
            "cement": 330,
            "water": 158.4,
            "sand": 780,
            "stone": 1060,
            "admixture": 7.26,
            "admixture_type": "聚羧酸系泵送剂",
            "fly_ash": 85,
            "mineral_powder": 65,
            "is_active": True,
            "is_standard": True,
            "remarks": "高流动性泵送混凝土，适用于长距离泵送"
        },
        {
            "formula_name": "C30早强混凝土配合比",
            "formula_code": "FORM-C30-EARLY-001",
            "concrete_grade": "C30",
            "water_cement_ratio": 0.45,
            "slump": 120,
            "cement": 360,
            "water": 162.0,
            "sand": 740,
            "stone": 1100,
            "admixture": 9.0,
            "admixture_type": "早强型减水剂",
            "fly_ash": 50,
            "mineral_powder": 40,
            "is_active": True,
            "is_standard": True,
            "remarks": "早强混凝土，适用于紧急抢修工程"
        }
    ]
    return formulas


async def generate_test_tasks(formula_ids: List[int], user_ids: List[int]) -> List[dict]:
    """
    生成测试任务数据
    
    Args:
        formula_ids: 可用的配方ID列表
        user_ids: 可用的用户ID列表（操作员）
    
    Returns:
        List[dict]: 任务信息列表
    """
    now = datetime.now()
    
    tasks = [
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-001",
            "concrete_grade": "C30",
            "quantity": 50.0,
            "delivery_time": now + timedelta(hours=4),
            "project_name": "阳光花园住宅小区1号楼",
            "project_address": "北京市朝阳区建国路88号",
            "customer_name": "北京建工集团",
            "formula_id": formula_ids[3] if len(formula_ids) > 3 else formula_ids[0],
            "status": "pending",
            "operator_id": None,
            "remarks": "泵送混凝土，坍落度要求160±20mm"
        },
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-002",
            "concrete_grade": "C25",
            "quantity": 30.0,
            "delivery_time": now + timedelta(hours=6),
            "project_name": "阳光花园住宅小区地下车库",
            "project_address": "北京市朝阳区建国路88号",
            "customer_name": "北京建工集团",
            "formula_id": formula_ids[2] if len(formula_ids) > 2 else formula_ids[0],
            "status": "accepted",
            "operator_id": user_ids[1] if len(user_ids) > 1 else user_ids[0],
            "accepted_at": now - timedelta(minutes=30),
            "remarks": "底板混凝土，抗渗等级P6"
        },
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-003",
            "concrete_grade": "C35",
            "quantity": 80.0,
            "delivery_time": now + timedelta(hours=8),
            "project_name": "国贸中心三期扩建工程",
            "project_address": "北京市朝阳区国贸商圈",
            "customer_name": "中国建筑股份",
            "formula_id": formula_ids[4] if len(formula_ids) > 4 else formula_ids[0],
            "status": "in_progress",
            "operator_id": user_ids[1] if len(user_ids) > 1 else user_ids[0],
            "accepted_at": now - timedelta(hours=2),
            "started_at": now - timedelta(hours=1),
            "remarks": "高强度混凝土，用于主体结构柱"
        },
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-004",
            "concrete_grade": "C40",
            "quantity": 120.0,
            "delivery_time": now + timedelta(hours=12),
            "project_name": "京张高铁清河站改造",
            "project_address": "北京市海淀区清河",
            "customer_name": "中铁建设集团",
            "formula_id": formula_ids[5] if len(formula_ids) > 5 else formula_ids[0],
            "status": "pending",
            "operator_id": None,
            "remarks": "高性能混凝土，耐久性要求高"
        },
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-005",
            "concrete_grade": "C20",
            "quantity": 25.0,
            "delivery_time": now - timedelta(days=1),
            "project_name": "市政道路修补工程",
            "project_address": "北京市西城区长安街沿线",
            "customer_name": "北京市政工程",
            "formula_id": formula_ids[1] if len(formula_ids) > 1 else formula_ids[0],
            "status": "completed",
            "operator_id": user_ids[2] if len(user_ids) > 2 else user_ids[0],
            "accepted_at": now - timedelta(days=1, hours=2),
            "started_at": now - timedelta(days=1, hours=1),
            "completed_at": now - timedelta(days=1),
            "remarks": "路面修补，已完成"
        },
        {
            "task_no": f"TASK-{now.strftime('%Y%m%d')}-006",
            "concrete_grade": "C15",
            "quantity": 40.0,
            "delivery_time": now + timedelta(days=1),
            "project_name": "工业园区围墙基础",
            "project_address": "北京市亦庄经济开发区",
            "customer_name": "北京开发区建设",
            "formula_id": formula_ids[0],
            "status": "pending",
            "operator_id": None,
            "remarks": "垫层混凝土，强度要求较低"
        }
    ]
    return tasks


async def generate_test_feeding_records(task_id: int, formula: Formula, batch_count: int = 5) -> List[dict]:
    """
    生成测试投料记录数据
    
    Args:
        task_id: 任务ID
        formula: 配方对象
        batch_count: 盘数
    
    Returns:
        List[dict]: 投料记录列表
    """
    now = datetime.now()
    records = []
    
    for i in range(1, batch_count + 1):
        batch_quantity = 2.0  # 每盘2立方米
        
        # 理论用量
        cement_theory = formula.cement * batch_quantity
        water_theory = formula.water * batch_quantity
        sand_theory = formula.sand * batch_quantity
        stone_theory = formula.stone * batch_quantity
        admixture_theory = (formula.admixture or 0) * batch_quantity
        
        # 实际用量（带少量随机偏差）
        import random
        deviation_factor = random.uniform(-0.03, 0.03)  # ±3%偏差
        
        # 第3盘故意制造大偏差用于测试预警
        if i == 3:
            deviation_factor = random.uniform(0.06, 0.12)  # 6%-12%偏差
        
        cement_actual = round(cement_theory * (1 + deviation_factor), 2)
        water_actual = round(water_theory * (1 + random.uniform(-0.02, 0.02)), 2)
        sand_actual = round(sand_theory * (1 + random.uniform(-0.02, 0.02)), 2)
        stone_actual = round(stone_theory * (1 + random.uniform(-0.02, 0.02)), 2)
        admixture_actual = round(admixture_theory * (1 + random.uniform(-0.02, 0.02)), 2)
        
        # 计算偏差百分比
        def calc_dev(theory, actual):
            if theory == 0:
                return 0
            return round(((actual - theory) / theory) * 100, 2)
        
        cement_deviation = calc_dev(cement_theory, cement_actual)
        water_deviation = calc_dev(water_theory, water_actual)
        sand_deviation = calc_dev(sand_theory, sand_actual)
        stone_deviation = calc_dev(stone_theory, stone_actual)
        admixture_deviation = calc_dev(admixture_theory, admixture_actual)
        
        # 检查预警
        has_warning = False
        warning_level = None
        warning_messages = []
        
        deviations = [
            ("水泥", cement_deviation),
            ("水", water_deviation),
            ("砂子", sand_deviation),
            ("石子", stone_deviation),
            ("外加剂", admixture_deviation)
        ]
        
        for material, dev in deviations:
            abs_dev = abs(dev)
            if abs_dev >= 10:
                has_warning = True
                warning_level = "critical"
                warning_messages.append(f"{material}偏差{dev:.2f}%（严重）")
            elif abs_dev >= 5:
                has_warning = True
                if not warning_level:
                    warning_level = "warning"
                warning_messages.append(f"{material}偏差{dev:.2f}%（警告）")
        
        records.append({
            "task_id": task_id,
            "batch_no": i,
            "batch_quantity": batch_quantity,
            "feeding_method": "scan" if i % 2 == 0 else "manual",
            "cement_barcode": f"CM{100000 + i}",
            "cement_lot": f"LOT-CM-{now.strftime('%Y%m%d')}",
            "cement_actual": cement_actual,
            "water_actual": water_actual,
            "sand_barcode": f"SD{200000 + i}",
            "sand_lot": f"LOT-SD-{now.strftime('%Y%m%d')}",
            "sand_actual": sand_actual,
            "stone_barcode": f"ST{300000 + i}",
            "stone_lot": f"LOT-ST-{now.strftime('%Y%m%d')}",
            "stone_actual": stone_actual,
            "admixture_barcode": f"AD{400000 + i}",
            "admixture_lot": f"LOT-AD-{now.strftime('%Y%m%d')}",
            "admixture_actual": admixture_actual,
            "fly_ash_actual": formula.fly_ash * batch_quantity if formula.fly_ash else 0,
            "mineral_powder_actual": formula.mineral_powder * batch_quantity if formula.mineral_powder else 0,
            
            # 理论用量
            "cement_theory": cement_theory,
            "water_theory": water_theory,
            "sand_theory": sand_theory,
            "stone_theory": stone_theory,
            "admixture_theory": admixture_theory,
            
            # 偏差
            "cement_deviation": cement_deviation,
            "water_deviation": water_deviation,
            "sand_deviation": sand_deviation,
            "stone_deviation": stone_deviation,
            "admixture_deviation": admixture_deviation,
            
            # 预警
            "has_warning": has_warning,
            "warning_level": warning_level,
            "warning_message": "; ".join(warning_messages) if warning_messages else None,
            
            "created_at": now + timedelta(minutes=i * 15)
        })
    
    return records


async def generate_test_mixing_records(task_id: int, feeding_records_count: int) -> List[dict]:
    """
    生成测试搅拌记录数据
    
    Args:
        task_id: 任务ID
        feeding_records_count: 投料记录数量
    
    Returns:
        List[dict]: 搅拌记录列表
    """
    now = datetime.now()
    records = []
    
    for i in range(1, feeding_records_count + 1):
        # 随机决定是否异常
        import random
        is_abnormal = i == 3  # 第3盘设为异常用于测试
        
        records.append({
            "task_id": task_id,
            "batch_no": i,
            "mixing_time_seconds": random.randint(120, 180),
            "rotation_speed": random.randint(28, 32),
            "current_temperature": round(random.uniform(18, 28), 1),
            "status": "abnormal" if is_abnormal else "completed",
            "is_abnormal": is_abnormal,
            "abnormal_type": "equipment_fault" if is_abnormal else None,
            "abnormal_description": "搅拌机电流异常波动，检查后发现皮带轻微打滑" if is_abnormal else None,
            "handling_measures": "紧急停机检查，调整皮带张紧度后恢复生产" if is_abnormal else None,
            "slump_actual": round(random.uniform(150, 170), 1) if not is_abnormal else None,
            "temperature_actual": round(random.uniform(20, 25), 1) if not is_abnormal else None,
            "quality_status": "qualified" if not is_abnormal else None,
            "created_at": now + timedelta(minutes=i * 15 + 5),
            "completed_at": now + timedelta(minutes=i * 15 + 8)
        })
    
    return records


async def populate_test_data(db: AsyncSession):
    """
    填充测试数据到数据库
    
    Args:
        db: 数据库会话
    """
    # 1. 创建测试用户
    user_data_list = await generate_test_users()
    created_users = []
    
    for user_data in user_data_list:
        # 检查用户是否已存在
        from sqlalchemy import select
        existing = await db.execute(
            select(User).where(User.username == user_data["username"])
        )
        if existing.scalar_one_or_none():
            continue
        
        new_user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            real_name=user_data["real_name"],
            phone=user_data["phone"],
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        db.add(new_user)
        created_users.append(new_user)
    
    await db.commit()
    
    # 获取所有用户ID
    users_result = await db.execute(select(User))
    all_users = users_result.scalars().all()
    user_ids = [u.id for u in all_users]
    operator_ids = [u.id for u in all_users if u.role == "operator"]
    
    # 2. 创建测试配方
    formula_data_list = await generate_test_formulas()
    created_formulas = []
    
    for formula_data in formula_data_list:
        existing = await db.execute(
            select(Formula).where(Formula.formula_code == formula_data["formula_code"])
        )
        if existing.scalar_one_or_none():
            continue
        
        new_formula = Formula(**formula_data)
        db.add(new_formula)
        created_formulas.append(new_formula)
    
    await db.commit()
    
    # 获取所有配方
    formulas_result = await db.execute(select(Formula))
    all_formulas = formulas_result.scalars().all()
    formula_ids = [f.id for f in all_formulas]
    
    # 3. 创建测试任务
    task_data_list = await generate_test_tasks(formula_ids, operator_ids)
    created_tasks = []
    
    for task_data in task_data_list:
        existing = await db.execute(
            select(Task).where(Task.task_no == task_data["task_no"])
        )
        if existing.scalar_one_or_none():
            continue
        
        new_task = Task(**task_data)
        db.add(new_task)
        created_tasks.append(new_task)
    
    await db.commit()
    
    # 获取所有任务
    tasks_result = await db.execute(select(Task))
    all_tasks = tasks_result.scalars().all()
    
    # 4. 为进行中的任务创建投料记录和搅拌记录
    for task in all_tasks:
        if task.status == "in_progress":
            # 获取任务配方
            formula = None
            if task.formula_id:
                formula_result = await db.execute(
                    select(Formula).where(Formula.id == task.formula_id)
                )
                formula = formula_result.scalar_one_or_none()
            
            if not formula and all_formulas:
                # 找匹配的标号
                for f in all_formulas:
                    if f.concrete_grade == task.concrete_grade:
                        formula = f
                        break
                if not formula:
                    formula = all_formulas[0]
            
            if formula:
                # 创建投料记录
                feeding_records_data = await generate_test_feeding_records(task.id, formula, 5)
                created_feeding_ids = []
                
                for fr_data in feeding_records_data:
                    new_feeding = FeedingRecord(**fr_data)
                    if operator_ids:
                        new_feeding.operator_id = operator_ids[0]
                    db.add(new_feeding)
                    created_feeding_ids.append(new_feeding)
                
                await db.commit()
                
                # 创建搅拌记录
                mixing_records_data = await generate_test_mixing_records(task.id, 5)
                
                for i, mr_data in enumerate(mixing_records_data):
                    new_mixing = MixingRecord(**mr_data)
                    if operator_ids:
                        new_mixing.operator_id = operator_ids[0]
                    db.add(new_mixing)
                
                await db.commit()
    
    return {
        "users_created": len(created_users),
        "formulas_created": len(created_formulas),
        "tasks_created": len(created_tasks),
        "message": "测试数据生成成功"
    }
