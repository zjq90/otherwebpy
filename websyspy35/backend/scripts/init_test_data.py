"""
测试数据初始化脚本
用于生成系统测试所需的测试数据
运行方式: python -m scripts.init_test_data
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

# 添加父目录到路径，以便导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, init_db
from app.models.equipment import Equipment, Sensor
from app.models.monitoring import SensorData, OperationLog, ControlSystemStatus
from app.models.maintenance import MaintenancePlan, MaintenanceTask, MaintenanceRecord


def create_equipment_data(db: Session):
    """
    创建设备档案测试数据
    """
    print("正在创建设备档案测试数据...")
    
    equipment_list = [
        {
            "equipment_code": "EQ-001",
            "name": "搅拌主机1号",
            "equipment_type": "搅拌主机",
            "model": "JS2000",
            "specification": "2000L",
            "manufacturer": "三一重工",
            "production_date": date(2023, 1, 15),
            "installation_date": date(2023, 3, 20),
            "location": "生产车间A区-1号生产线",
            "status": "运行中",
            "responsible_person": "张三",
            "contact_phone": "13800138001",
            "description": "主要搅拌设备，用于混凝土生产"
        },
        {
            "equipment_code": "EQ-002",
            "name": "搅拌主机2号",
            "equipment_type": "搅拌主机",
            "model": "JS3000",
            "specification": "3000L",
            "manufacturer": "中联重科",
            "production_date": date(2023, 2, 20),
            "installation_date": date(2023, 4, 15),
            "location": "生产车间A区-2号生产线",
            "status": "运行中",
            "responsible_person": "李四",
            "contact_phone": "13800138002",
            "description": "备用搅拌设备"
        },
        {
            "equipment_code": "EQ-003",
            "name": "皮带秤1号",
            "equipment_type": "皮带秤",
            "model": "ICS-17A",
            "specification": "精度±0.5%",
            "manufacturer": "赛摩电气",
            "production_date": date(2023, 3, 10),
            "installation_date": date(2023, 4, 1),
            "location": "原料输送区-1号线",
            "status": "运行中",
            "responsible_person": "王五",
            "contact_phone": "13800138003",
            "description": "砂石原料计量皮带秤"
        },
        {
            "equipment_code": "EQ-004",
            "name": "皮带秤2号",
            "equipment_type": "皮带秤",
            "model": "ICS-17A",
            "specification": "精度±0.5%",
            "manufacturer": "赛摩电气",
            "production_date": date(2023, 3, 12),
            "installation_date": date(2023, 4, 2),
            "location": "原料输送区-2号线",
            "status": "维护中",
            "responsible_person": "赵六",
            "contact_phone": "13800138004",
            "description": "水泥原料计量皮带秤"
        },
        {
            "equipment_code": "EQ-005",
            "name": "空压机1号",
            "equipment_type": "空压机",
            "model": "GA-110",
            "specification": "110kW",
            "manufacturer": "阿特拉斯科普柯",
            "production_date": date(2023, 4, 5),
            "installation_date": date(2023, 5, 10),
            "location": "动力车间-1号机组",
            "status": "运行中",
            "responsible_person": "钱七",
            "contact_phone": "13800138005",
            "description": "提供压缩空气"
        },
        {
            "equipment_code": "EQ-006",
            "name": "空压机2号",
            "equipment_type": "空压机",
            "model": "GA-110",
            "specification": "110kW",
            "manufacturer": "阿特拉斯科普柯",
            "production_date": date(2023, 4, 8),
            "installation_date": date(2023, 5, 12),
            "location": "动力车间-2号机组",
            "status": "停机",
            "responsible_person": "孙八",
            "contact_phone": "13800138006",
            "description": "备用空压机"
        }
    ]
    
    created_count = 0
    for eq_data in equipment_list:
        existing = db.query(Equipment).filter(
            Equipment.equipment_code == eq_data["equipment_code"]
        ).first()
        if not existing:
            equipment = Equipment(**eq_data)
            db.add(equipment)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条设备记录")


def create_sensor_data(db: Session):
    """
    创建传感器测试数据
    """
    print("正在创建传感器测试数据...")
    
    # 获取所有设备
    equipments = db.query(Equipment).all()
    
    sensor_list = []
    
    for equipment in equipments:
        # 根据设备类型添加不同的传感器
        if equipment.equipment_type == "搅拌主机":
            # 搅拌主机：电流、温度、振动传感器
            sensor_list.extend([
                {
                    "sensor_code": f"S-{equipment.equipment_code}-CUR",
                    "name": f"{equipment.name}-电流传感器",
                    "sensor_type": "电流",
                    "equipment_id": equipment.id,
                    "installation_location": "主电机",
                    "unit": "A",
                    "min_value": 50.0,
                    "max_value": 150.0,
                    "warning_threshold": 140.0,
                    "alarm_threshold": 160.0,
                    "status": "正常",
                    "description": "主电机工作电流监测"
                },
                {
                    "sensor_code": f"S-{equipment.equipment_code}-TMP",
                    "name": f"{equipment.name}-温度传感器",
                    "sensor_type": "温度",
                    "equipment_id": equipment.id,
                    "installation_location": "轴承部位",
                    "unit": "℃",
                    "min_value": 20.0,
                    "max_value": 80.0,
                    "warning_threshold": 70.0,
                    "alarm_threshold": 90.0,
                    "status": "正常",
                    "description": "轴承温度监测"
                },
                {
                    "sensor_code": f"S-{equipment.equipment_code}-VIB",
                    "name": f"{equipment.name}-振动传感器",
                    "sensor_type": "振动",
                    "equipment_id": equipment.id,
                    "installation_location": "搅拌轴",
                    "unit": "mm/s",
                    "min_value": 0.0,
                    "max_value": 4.5,
                    "warning_threshold": 3.5,
                    "alarm_threshold": 5.0,
                    "status": "正常",
                    "description": "搅拌轴振动监测"
                }
            ])
        elif equipment.equipment_type == "皮带秤":
            # 皮带秤：电流、速度、张力传感器
            sensor_list.extend([
                {
                    "sensor_code": f"S-{equipment.equipment_code}-CUR",
                    "name": f"{equipment.name}-电流传感器",
                    "sensor_type": "电流",
                    "equipment_id": equipment.id,
                    "installation_location": "驱动电机",
                    "unit": "A",
                    "min_value": 10.0,
                    "max_value": 50.0,
                    "warning_threshold": 45.0,
                    "alarm_threshold": 55.0,
                    "status": "正常",
                    "description": "驱动电机电流监测"
                },
                {
                    "sensor_code": f"S-{equipment.equipment_code}-SPD",
                    "name": f"{equipment.name}-速度传感器",
                    "sensor_type": "速度",
                    "equipment_id": equipment.id,
                    "installation_location": "皮带滚筒",
                    "unit": "m/s",
                    "min_value": 0.8,
                    "max_value": 2.5,
                    "warning_threshold": 2.3,
                    "alarm_threshold": 3.0,
                    "status": "正常",
                    "description": "皮带运行速度监测"
                }
            ])
        elif equipment.equipment_type == "空压机":
            # 空压机：电流、压力、温度传感器
            sensor_list.extend([
                {
                    "sensor_code": f"S-{equipment.equipment_code}-CUR",
                    "name": f"{equipment.name}-电流传感器",
                    "sensor_type": "电流",
                    "equipment_id": equipment.id,
                    "installation_location": "主电机",
                    "unit": "A",
                    "min_value": 100.0,
                    "max_value": 200.0,
                    "warning_threshold": 185.0,
                    "alarm_threshold": 210.0,
                    "status": "正常",
                    "description": "主电机工作电流监测"
                },
                {
                    "sensor_code": f"S-{equipment.equipment_code}-PRS",
                    "name": f"{equipment.name}-压力传感器",
                    "sensor_type": "压力",
                    "equipment_id": equipment.id,
                    "installation_location": "出气口",
                    "unit": "MPa",
                    "min_value": 0.6,
                    "max_value": 0.8,
                    "warning_threshold": 0.85,
                    "alarm_threshold": 1.0,
                    "status": "正常",
                    "description": "出气压力监测"
                },
                {
                    "sensor_code": f"S-{equipment.equipment_code}-TMP",
                    "name": f"{equipment.name}-温度传感器",
                    "sensor_type": "温度",
                    "equipment_id": equipment.id,
                    "installation_location": "主机排气端",
                    "unit": "℃",
                    "min_value": 60.0,
                    "max_value": 100.0,
                    "warning_threshold": 95.0,
                    "alarm_threshold": 110.0,
                    "status": "正常",
                    "description": "排气温度监测"
                }
            ])
    
    created_count = 0
    for sensor_data in sensor_list:
        existing = db.query(Sensor).filter(
            Sensor.sensor_code == sensor_data["sensor_code"]
        ).first()
        if not existing:
            sensor = Sensor(**sensor_data)
            db.add(sensor)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条传感器记录")


def create_sensor_data_records(db: Session):
    """
    创建传感器数据记录（历史数据）
    """
    print("正在创建传感器数据历史记录...")
    
    sensors = db.query(Sensor).filter(Sensor.status == "正常").all()
    
    created_count = 0
    now = datetime.now()
    
    for sensor in sensors:
        # 为每个传感器生成过去24小时的数据（每15分钟一条）
        for i in range(96):
            time_offset = timedelta(minutes=15 * (96 - i - 1))
            collected_at = now - time_offset
            
            # 生成正常值范围内的随机数据
            # 偶尔生成预警或报警数据
            rand = random.random()
            
            if rand < 0.95:
                # 95%概率为正常值
                value = random.uniform(sensor.min_value, sensor.max_value * 0.8)
                status = "正常"
                is_abnormal = False
            elif rand < 0.98:
                # 3%概率为预警值
                value = random.uniform(sensor.max_value * 0.8, sensor.warning_threshold)
                status = "预警"
                is_abnormal = True
            else:
                # 2%概率为报警值
                value = random.uniform(sensor.warning_threshold, sensor.alarm_threshold)
                status = "报警"
                is_abnormal = True
            
            # 四舍五入保留2位小数
            value = round(value, 2)
            
            sensor_data_record = SensorData(
                sensor_id=sensor.id,
                value=value,
                status=status,
                is_abnormal=is_abnormal,
                collected_at=collected_at,
                description=f"自动生成的测试数据 - {'正常' if not is_abnormal else status}"
            )
            db.add(sensor_data_record)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条传感器数据记录")


def create_operation_logs(db: Session):
    """
    创建运行日志测试数据
    """
    print("正在创建运行日志测试数据...")
    
    equipments = db.query(Equipment).all()
    
    log_templates = [
        {
            "log_type": "运行状态变更",
            "level": "信息",
            "title": "设备启动",
            "content": "设备正常启动，进入运行状态"
        },
        {
            "log_type": "运行状态变更",
            "level": "信息",
            "title": "设备停机",
            "content": "设备按计划停机"
        },
        {
            "log_type": "维护记录",
            "level": "信息",
            "title": "设备维护",
            "content": "设备进行例行维护"
        },
        {
            "log_type": "故障事件",
            "level": "警告",
            "title": "传感器预警",
            "content": "传感器数据超出预警范围"
        },
        {
            "log_type": "故障事件",
            "level": "错误",
            "title": "设备故障",
            "content": "设备出现故障，需要检修"
        }
    ]
    
    created_count = 0
    now = datetime.now()
    
    for equipment in equipments:
        # 为每个设备生成5-10条日志
        log_count = random.randint(5, 10)
        for i in range(log_count):
            template = random.choice(log_templates)
            time_offset = timedelta(hours=random.randint(0, 72))
            recorded_at = now - time_offset
            
            log = OperationLog(
                equipment_id=equipment.id,
                log_type=template["log_type"],
                level=template["level"],
                title=template["title"],
                content=f"{template['content']} - 测试数据",
                from_status=equipment.status,
                to_status=equipment.status,
                recorded_at=recorded_at
            )
            db.add(log)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条运行日志记录")


def create_control_system_status(db: Session):
    """
    创建控制系统监控项测试数据
    """
    print("正在创建控制系统监控项测试数据...")
    
    control_items = [
        {
            "monitor_item": "主电源断电保护",
            "monitor_type": "断电保护",
            "current_value": "正常",
            "numeric_value": None,
            "unit": None,
            "normal_status": "正常",
            "status": "正常",
            "is_enabled": True,
            "description": "主电源断电保护系统状态监控"
        },
        {
            "monitor_item": "备用电源断电保护",
            "monitor_type": "断电保护",
            "current_value": "正常",
            "numeric_value": None,
            "unit": None,
            "normal_status": "正常",
            "status": "正常",
            "is_enabled": True,
            "description": "备用电源断电保护系统状态监控"
        },
        {
            "monitor_item": "生产数据隔离",
            "monitor_type": "数据隔离",
            "current_value": "已启用",
            "numeric_value": None,
            "unit": None,
            "normal_status": "已启用",
            "status": "正常",
            "is_enabled": True,
            "description": "生产数据与办公网络隔离状态"
        },
        {
            "monitor_item": "控制网络隔离",
            "monitor_type": "数据隔离",
            "current_value": "已启用",
            "numeric_value": None,
            "unit": None,
            "normal_status": "已启用",
            "status": "正常",
            "is_enabled": True,
            "description": "控制网络与外部网络隔离状态"
        },
        {
            "monitor_item": "电磁抗干扰能力",
            "monitor_type": "抗干扰能力",
            "current_value": "良好",
            "numeric_value": 95.5,
            "unit": "dB",
            "normal_status": "≥90dB",
            "status": "正常",
            "is_enabled": True,
            "description": "电磁干扰防护等级"
        },
        {
            "monitor_item": "电压稳定度",
            "monitor_type": "电压稳定",
            "current_value": "±1.2%",
            "numeric_value": 1.2,
            "unit": "%",
            "normal_status": "±5%以内",
            "status": "正常",
            "is_enabled": True,
            "description": "主电源电压波动范围"
        },
        {
            "monitor_item": "频率稳定度",
            "monitor_type": "电压稳定",
            "current_value": "±0.1Hz",
            "numeric_value": 0.1,
            "unit": "Hz",
            "normal_status": "±0.5Hz以内",
            "status": "正常",
            "is_enabled": True,
            "description": "电源频率波动范围"
        },
        {
            "monitor_item": "UPS电池状态",
            "monitor_type": "断电保护",
            "current_value": "100%",
            "numeric_value": 100.0,
            "unit": "%",
            "normal_status": "≥80%",
            "status": "正常",
            "is_enabled": True,
            "description": "UPS备用电池电量"
        }
    ]
    
    created_count = 0
    for item_data in control_items:
        existing = db.query(ControlSystemStatus).filter(
            ControlSystemStatus.monitor_item == item_data["monitor_item"]
        ).first()
        if not existing:
            item = ControlSystemStatus(**item_data)
            db.add(item)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条控制系统监控记录")


def create_maintenance_plans(db: Session):
    """
    创建保养计划测试数据
    """
    print("正在创建保养计划测试数据...")
    
    plans = [
        {
            "plan_code": "MP-001",
            "name": "搅拌主机日常保养",
            "maintenance_type": "日常保养",
            "cycle_days": 1,
            "cycle_description": "每日一次",
            "content": "1. 检查搅拌叶片磨损情况\n2. 检查润滑系统\n3. 清理搅拌缸内积料\n4. 检查各连接螺栓紧固情况",
            "standard": "叶片磨损量≤5mm，润滑系统正常，螺栓无松动",
            "estimated_hours": 1.0,
            "responsible_person": "张三",
            "status": "启用",
            "description": "搅拌主机日常保养计划"
        },
        {
            "plan_code": "MP-002",
            "name": "搅拌主机月度保养",
            "maintenance_type": "月度保养",
            "cycle_days": 30,
            "cycle_description": "每月一次",
            "content": "1. 更换齿轮油\n2. 检查电机绝缘\n3. 校准传感器\n4. 检查安全防护装置",
            "standard": "齿轮油符合规格，电机绝缘≥0.5MΩ",
            "estimated_hours": 4.0,
            "responsible_person": "李四",
            "status": "启用",
            "description": "搅拌主机月度保养计划"
        },
        {
            "plan_code": "MP-003",
            "name": "皮带秤日常检查",
            "maintenance_type": "日常保养",
            "cycle_days": 1,
            "cycle_description": "每日一次",
            "content": "1. 检查皮带张紧度\n2. 清洁称重传感器\n3. 检查托辊转动情况",
            "standard": "皮带张紧适中，传感器无积料",
            "estimated_hours": 0.5,
            "responsible_person": "王五",
            "status": "启用",
            "description": "皮带秤日常检查计划"
        },
        {
            "plan_code": "MP-004",
            "name": "空压机日常保养",
            "maintenance_type": "日常保养",
            "cycle_days": 1,
            "cycle_description": "每日一次",
            "content": "1. 检查油位\n2. 检查排气温度\n3. 检查空气过滤器\n4. 排放冷凝水",
            "standard": "油位在正常范围，排气温度≤100℃",
            "estimated_hours": 0.5,
            "responsible_person": "钱七",
            "status": "启用",
            "description": "空压机日常保养计划"
        },
        {
            "plan_code": "MP-005",
            "name": "空压机季度保养",
            "maintenance_type": "季度保养",
            "cycle_days": 90,
            "cycle_description": "每季度一次",
            "content": "1. 更换润滑油\n2. 更换空气过滤器\n3. 更换油过滤器\n4. 检查电机轴承",
            "standard": "所有过滤器更换完毕，润滑油符合规格",
            "estimated_hours": 3.0,
            "responsible_person": "钱七",
            "status": "启用",
            "description": "空压机季度保养计划"
        }
    ]
    
    created_count = 0
    for plan_data in plans:
        existing = db.query(MaintenancePlan).filter(
            MaintenancePlan.plan_code == plan_data["plan_code"]
        ).first()
        if not existing:
            plan = MaintenancePlan(**plan_data)
            db.add(plan)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条保养计划记录")


def create_maintenance_tasks(db: Session):
    """
    创建保养任务测试数据
    """
    print("正在创建保养任务测试数据...")
    
    equipments = db.query(Equipment).all()
    plans = db.query(MaintenancePlan).all()
    
    today = date.today()
    created_count = 0
    
    # 为每个计划创建一些任务
    for plan in plans:
        for i in range(3):
            # 选择一个设备
            equipment = random.choice(equipments)
            
            # 随机生成日期（过去30天到未来30天）
            day_offset = random.randint(-30, 30)
            plan_date = today + timedelta(days=day_offset)
            
            # 确定状态
            if day_offset < -7:
                status = "已完成"
                actual_date = plan_date
            elif day_offset < 0:
                status = "已逾期"
                actual_date = None
            elif day_offset == 0:
                status = "执行中"
                actual_date = None
            else:
                status = "待执行"
                actual_date = None
            
            task_code = f"MT-{plan.plan_code.replace('MP', '')}-{i+1:03d}"
            
            existing = db.query(MaintenanceTask).filter(
                MaintenanceTask.task_code == task_code
            ).first()
            
            if not existing:
                task = MaintenanceTask(
                    task_code=task_code,
                    plan_id=plan.id,
                    equipment_id=equipment.id,
                    name=f"{plan.name} - {equipment.name}",
                    maintenance_type=plan.maintenance_type,
                    plan_date=plan_date,
                    actual_date=actual_date,
                    content=plan.content,
                    standard=plan.standard,
                    responsible_person=plan.responsible_person,
                    executor=plan.responsible_person if status == "已完成" else None,
                    status=status,
                    description=f"自动生成的测试任务 - {plan.name}"
                )
                db.add(task)
                created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条保养任务记录")


def create_maintenance_records(db: Session):
    """
    创建保养记录测试数据
    """
    print("正在创建保养记录测试数据...")
    
    # 获取已完成的任务
    completed_tasks = db.query(MaintenanceTask).filter(
        MaintenanceTask.status == "已完成"
    ).all()
    
    created_count = 0
    
    for i, task in enumerate(completed_tasks):
        record_code = f"MR-{task.task_code.replace('MT', '')}"
        
        existing = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.record_code == record_code
        ).first()
        
        if not existing:
            has_issues = random.choice([True, False, False, False])  # 25%概率有问题
            
            record = MaintenanceRecord(
                record_code=record_code,
                task_id=task.id,
                execution_date=task.actual_date or date.today(),
                executor=task.executor or "测试人员",
                work_hours=round(random.uniform(0.5, 4.0), 1),
                content=task.content,
                result="保养完成，设备运行正常" if not has_issues else "保养完成，但发现部分问题",
                has_issues=has_issues,
                issue_description="发现皮带轻微磨损，建议下次保养时更换" if has_issues else None,
                treatment_measures="已调整张紧度，观察运行情况" if has_issues else None,
                replaced_parts=None,
                next_maintenance_suggestion="建议按计划进行下次保养",
                inspector="质检人员",
                inspection_date=task.actual_date or date.today(),
                inspection_result="合格",
                description=f"自动生成的保养记录 - 测试数据 #{i+1}"
            )
            db.add(record)
            created_count += 1
    
    db.commit()
    print(f"✓ 已创建 {created_count} 条保养记录")


def main():
    """
    主函数：初始化数据库并生成测试数据
    """
    print("=" * 50)
    print("开始初始化测试数据...")
    print("=" * 50)
    
    # 初始化数据库表
    print("\n正在初始化数据库表...")
    init_db()
    print("✓ 数据库表初始化完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 按顺序创建测试数据
        create_equipment_data(db)
        create_sensor_data(db)
        create_sensor_data_records(db)
        create_operation_logs(db)
        create_control_system_status(db)
        create_maintenance_plans(db)
        create_maintenance_tasks(db)
        create_maintenance_records(db)
        
        print("\n" + "=" * 50)
        print("✓ 测试数据初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
