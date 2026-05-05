from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import (
    Formula, FormulaAdjustment, FormulaStatus,
    ProductionPlan, ProductionOrder, ProductionStatus,
    Resource, ResourceAllocation, ResourceType, ResourceStatus,
    ProductionLog, ProductionAlert, ProductionStage,
    AlertLevel, AlertStatus, ProductionStatusHistory
)


def init_formulas(db: Session):
    """初始化配方测试数据"""
    formulas = [
        {
            "formula_code": "FM-C30-001",
            "formula_name": "C30普通混凝土",
            "concrete_type": "普通混凝土",
            "strength_grade": "C30",
            "description": "标准C30混凝土配合比，适用于一般结构工程",
            "cement": 320.0,
            "sand": 780.0,
            "gravel": 1050.0,
            "water": 175.0,
            "admixture": 8.0,
            "fly_ash": 80.0,
            "mineral_powder": 0.0,
            "water_cement_ratio": 0.55,
            "slump": 120.0,
            "status": FormulaStatus.ACTIVE,
            "is_standard": True,
            "version": 1,
            "created_by": "system"
        },
        {
            "formula_code": "FM-C25-001",
            "formula_name": "C25泵送混凝土",
            "concrete_type": "泵送混凝土",
            "strength_grade": "C25",
            "description": "C25泵送混凝土，适用于高层建筑泵送施工",
            "cement": 280.0,
            "sand": 820.0,
            "gravel": 1020.0,
            "water": 180.0,
            "admixture": 9.5,
            "fly_ash": 90.0,
            "mineral_powder": 30.0,
            "water_cement_ratio": 0.64,
            "slump": 160.0,
            "status": FormulaStatus.ACTIVE,
            "is_standard": True,
            "version": 1,
            "created_by": "system"
        },
        {
            "formula_code": "FM-C35-001",
            "formula_name": "C35高强度混凝土",
            "concrete_type": "普通混凝土",
            "strength_grade": "C35",
            "description": "C35高强度混凝土，适用于重要结构部位",
            "cement": 380.0,
            "sand": 750.0,
            "gravel": 1080.0,
            "water": 168.0,
            "admixture": 10.0,
            "fly_ash": 70.0,
            "mineral_powder": 40.0,
            "water_cement_ratio": 0.44,
            "slump": 100.0,
            "status": FormulaStatus.ACTIVE,
            "is_standard": True,
            "version": 1,
            "created_by": "system"
        },
        {
            "formula_code": "FM-C40-001",
            "formula_name": "C40高性能混凝土",
            "concrete_type": "高性能混凝土",
            "strength_grade": "C40",
            "description": "C40高性能混凝土，适用于大跨度桥梁等特殊工程",
            "cement": 420.0,
            "sand": 720.0,
            "gravel": 1100.0,
            "water": 160.0,
            "admixture": 12.0,
            "fly_ash": 80.0,
            "mineral_powder": 50.0,
            "water_cement_ratio": 0.38,
            "slump": 180.0,
            "status": FormulaStatus.ACTIVE,
            "is_standard": True,
            "version": 1,
            "created_by": "system"
        },
        {
            "formula_code": "FM-C20-001",
            "formula_name": "C20垫层混凝土",
            "concrete_type": "普通混凝土",
            "strength_grade": "C20",
            "description": "C20垫层混凝土，适用于基础垫层、地坪等",
            "cement": 240.0,
            "sand": 850.0,
            "gravel": 1000.0,
            "water": 185.0,
            "admixture": 6.0,
            "fly_ash": 60.0,
            "mineral_powder": 0.0,
            "water_cement_ratio": 0.77,
            "slump": 80.0,
            "status": FormulaStatus.ACTIVE,
            "is_standard": True,
            "version": 1,
            "created_by": "system"
        }
    ]
    
    for formula_data in formulas:
        existing = db.query(Formula).filter(Formula.formula_code == formula_data["formula_code"]).first()
        if not existing:
            formula = Formula(**formula_data)
            formula.created_at = datetime.utcnow()
            formula.updated_at = datetime.utcnow()
            db.add(formula)
    
    db.commit()


def init_resources(db: Session):
    """初始化资源测试数据"""
    resources = [
        {
            "resource_code": "TRK-001",
            "resource_name": "三一搅拌车1号",
            "resource_type": ResourceType.MIXER_TRUCK,
            "model": "SY5250GJB1E",
            "capacity": 12.0,
            "capacity_unit": "m³",
            "license_plate": "京A·12345",
            "manufacture_year": 2020,
            "status": ResourceStatus.AVAILABLE,
            "remarks": "状态良好"
        },
        {
            "resource_code": "TRK-002",
            "resource_name": "三一搅拌车2号",
            "resource_type": ResourceType.MIXER_TRUCK,
            "model": "SY5250GJB1E",
            "capacity": 12.0,
            "capacity_unit": "m³",
            "license_plate": "京A·12346",
            "manufacture_year": 2020,
            "status": ResourceStatus.AVAILABLE,
            "remarks": "状态良好"
        },
        {
            "resource_code": "TRK-003",
            "resource_name": "中联重科搅拌车",
            "resource_type": ResourceType.MIXER_TRUCK,
            "model": "ZLJ5253GJBH",
            "capacity": 10.0,
            "capacity_unit": "m³",
            "license_plate": "京A·12347",
            "manufacture_year": 2019,
            "status": ResourceStatus.AVAILABLE,
            "remarks": "状态良好"
        },
        {
            "resource_code": "FLT-001",
            "resource_name": "龙工铲车1号",
            "resource_type": ResourceType.FORKLIFT,
            "model": "LG855N",
            "capacity": 5.0,
            "capacity_unit": "吨",
            "license_plate": "",
            "manufacture_year": 2021,
            "status": ResourceStatus.AVAILABLE,
            "remarks": "用于砂石装卸"
        },
        {
            "resource_code": "FLT-002",
            "resource_name": "柳工铲车",
            "resource_type": ResourceType.FORKLIFT,
            "model": "CLG856H",
            "capacity": 5.0,
            "capacity_unit": "吨",
            "license_plate": "",
            "manufacture_year": 2020,
            "status": ResourceStatus.MAINTENANCE,
            "remarks": "定期维护中"
        },
        {
            "resource_code": "PMP-001",
            "resource_name": "三一泵车",
            "resource_type": ResourceType.PUMP,
            "model": "SY5419THB",
            "capacity": 47.0,
            "capacity_unit": "米",
            "license_plate": "京A·12348",
            "manufacture_year": 2022,
            "status": ResourceStatus.AVAILABLE,
            "remarks": "47米泵车，状态极佳"
        }
    ]
    
    for resource_data in resources:
        existing = db.query(Resource).filter(Resource.resource_code == resource_data["resource_code"]).first()
        if not existing:
            resource = Resource(**resource_data)
            resource.created_at = datetime.utcnow()
            resource.updated_at = datetime.utcnow()
            db.add(resource)
    
    db.commit()


def init_production_plans(db: Session):
    """初始化生产计划测试数据"""
    now = datetime.utcnow()
    
    plans = [
        {
            "plan_code": "PLN-2024-001",
            "plan_name": "XX商业中心项目",
            "project_name": "XX商业中心",
            "project_location": "北京市朝阳区XX路88号",
            "contact_person": "张经理",
            "contact_phone": "13800138001",
            "planned_start_date": now - timedelta(days=2),
            "planned_end_date": now + timedelta(days=5),
            "total_volume": 1500.0,
            "completed_volume": 450.0,
            "status": ProductionStatus.IN_PROGRESS,
            "priority": 3,
            "remarks": "重要商业项目，需保证质量",
            "created_by": "调度员"
        },
        {
            "plan_code": "PLN-2024-002",
            "plan_name": "YY住宅小区项目",
            "project_name": "YY住宅小区",
            "project_location": "北京市海淀区YY路168号",
            "contact_person": "李工",
            "contact_phone": "13800138002",
            "planned_start_date": now + timedelta(days=1),
            "planned_end_date": now + timedelta(days=10),
            "total_volume": 3000.0,
            "completed_volume": 0.0,
            "status": ProductionStatus.PENDING,
            "priority": 2,
            "remarks": "大型住宅项目，分多批次供应",
            "created_by": "调度员"
        },
        {
            "plan_code": "PLN-2024-003",
            "plan_name": "ZZ市政道路工程",
            "project_name": "ZZ市政道路",
            "project_location": "北京市丰台区ZZ路",
            "contact_person": "王工",
            "contact_phone": "13800138003",
            "planned_start_date": now - timedelta(days=5),
            "planned_end_date": now - timedelta(days=1),
            "total_volume": 800.0,
            "completed_volume": 800.0,
            "status": ProductionStatus.COMPLETED,
            "priority": 1,
            "remarks": "已完成，客户满意",
            "created_by": "调度员"
        }
    ]
    
    for plan_data in plans:
        existing = db.query(ProductionPlan).filter(ProductionPlan.plan_code == plan_data["plan_code"]).first()
        if not existing:
            plan = ProductionPlan(**plan_data)
            plan.created_at = datetime.utcnow()
            plan.updated_at = datetime.utcnow()
            if plan.status == ProductionStatus.COMPLETED:
                plan.actual_start_date = plan_data["planned_start_date"]
                plan.actual_end_date = plan_data["planned_end_date"]
            db.add(plan)
    
    db.commit()


def init_production_orders(db: Session):
    """初始化生产任务单测试数据"""
    now = datetime.utcnow()
    
    formulas = db.query(Formula).all()
    plans = db.query(ProductionPlan).all()
    
    formula_map = {f.formula_code: f for f in formulas}
    plan_map = {p.plan_code: p for p in plans}
    
    orders = [
        {
            "order_code": "ORD-2024-001",
            "plan_code": "PLN-2024-001",
            "formula_code": "FM-C30-001",
            "batch_number": "B20240501-001",
            "volume": 150.0,
            "pouring_location": "商业中心1号楼-3层梁板",
            "pouring_method": "泵送",
            "scheduled_time": now - timedelta(hours=4),
            "actual_start_time": now - timedelta(hours=3),
            "status": ProductionStatus.IN_PROGRESS,
            "current_stage": ProductionStage.MIXING,
            "progress": 45.0,
            "remarks": "正常生产中"
        },
        {
            "order_code": "ORD-2024-002",
            "order_code": "ORD-2024-002",
            "plan_code": "PLN-2024-001",
            "formula_code": "FM-C25-001",
            "batch_number": "B20240501-002",
            "volume": 100.0,
            "pouring_location": "商业中心2号楼-垫层",
            "pouring_method": "自卸",
            "scheduled_time": now - timedelta(hours=8),
            "actual_start_time": now - timedelta(hours=7),
            "actual_end_time": now - timedelta(hours=2),
            "status": ProductionStatus.COMPLETED,
            "current_stage": ProductionStage.COMPLETED,
            "progress": 100.0,
            "remarks": "已完成"
        },
        {
            "order_code": "ORD-2024-003",
            "plan_code": "PLN-2024-001",
            "formula_code": "FM-C30-001",
            "batch_number": "B20240501-003",
            "volume": 200.0,
            "pouring_location": "商业中心地下车库",
            "pouring_method": "泵送",
            "scheduled_time": now + timedelta(hours=2),
            "status": ProductionStatus.PENDING,
            "current_stage": ProductionStage.BATCHING,
            "progress": 0.0,
            "remarks": "待生产"
        },
        {
            "order_code": "ORD-2024-004",
            "plan_code": "PLN-2024-003",
            "formula_code": "FM-C20-001",
            "batch_number": "B20240428-001",
            "volume": 800.0,
            "pouring_location": "市政道路基层",
            "pouring_method": "自卸",
            "scheduled_time": now - timedelta(days=3),
            "actual_start_time": now - timedelta(days=3),
            "actual_end_time": now - timedelta(days=2),
            "status": ProductionStatus.COMPLETED,
            "current_stage": ProductionStage.COMPLETED,
            "progress": 100.0,
            "remarks": "已完成验收"
        }
    ]
    
    for order_data in orders:
        existing = db.query(ProductionOrder).filter(ProductionOrder.order_code == order_data["order_code"]).first()
        if not existing:
            order = ProductionOrder()
            order.order_code = order_data["order_code"]
            order.batch_number = order_data["batch_number"]
            order.volume = order_data["volume"]
            order.pouring_location = order_data["pouring_location"]
            order.pouring_method = order_data["pouring_method"]
            order.scheduled_time = order_data["scheduled_time"]
            order.actual_start_time = order_data.get("actual_start_time")
            order.actual_end_time = order_data.get("actual_end_time")
            order.status = order_data["status"]
            order.current_stage = order_data["current_stage"]
            order.progress = order_data["progress"]
            order.remarks = order_data["remarks"]
            order.created_at = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            
            formula = formula_map.get(order_data["formula_code"])
            if formula:
                order.formula_id = formula.id
            
            plan = plan_map.get(order_data["plan_code"])
            if plan:
                order.plan_id = plan.id
            
            db.add(order)
    
    db.commit()


def init_production_logs(db: Session):
    """初始化生产日志测试数据"""
    now = datetime.utcnow()
    orders = db.query(ProductionOrder).all()
    
    if not orders:
        return
    
    logs = []
    for order in orders[:2]:
        logs.extend([
            {
                "order_id": order.id,
                "stage": ProductionStage.BATCHING,
                "batch_weight_cement": 320.0 * 0.5,
                "batch_weight_sand": 780.0 * 0.5,
                "batch_weight_gravel": 1050.0 * 0.5,
                "batch_weight_water": 175.0 * 0.5,
                "batch_weight_admixture": 8.0 * 0.5,
                "batch_weight_fly_ash": 80.0 * 0.5,
                "batch_weight_mineral_powder": 0.0,
                "temperature": 25.5,
                "humidity": 65.0,
                "log_message": "配料开始，材料称重完成",
                "created_at": now - timedelta(hours=3)
            },
            {
                "order_id": order.id,
                "stage": ProductionStage.MIXING,
                "mixing_time": 120,
                "mixing_speed": 30.0,
                "temperature": 26.0,
                "humidity": 64.0,
                "log_message": "搅拌中，转速30rpm",
                "created_at": now - timedelta(hours=2)
            }
        ])
    
    for log_data in logs:
        log = ProductionLog(**log_data)
        db.add(log)
    
    db.commit()


def init_production_alerts(db: Session):
    """初始化生产预警测试数据"""
    now = datetime.utcnow()
    orders = db.query(ProductionOrder).all()
    
    if not orders:
        return
    
    alerts = [
        {
            "order_id": orders[0].id if orders else None,
            "alert_code": "ALT-001",
            "alert_title": "砂料含水率偏高",
            "alert_message": "检测到砂料含水率超出正常范围，建议调整用水量",
            "alert_level": AlertLevel.WARNING,
            "alert_status": AlertStatus.OPEN,
            "related_stage": ProductionStage.BATCHING,
            "created_at": now - timedelta(hours=1)
        },
        {
            "order_id": orders[0].id if orders else None,
            "alert_code": "ALT-002",
            "alert_title": "搅拌温度正常",
            "alert_message": "搅拌温度在正常范围内",
            "alert_level": AlertLevel.INFO,
            "alert_status": AlertStatus.RESOLVED,
            "related_stage": ProductionStage.MIXING,
            "acknowledged_at": now - timedelta(hours=2),
            "acknowledged_by": "操作员A",
            "resolved_at": now - timedelta(hours=1),
            "resolved_by": "操作员A",
            "resolution_notes": "已确认正常",
            "created_at": now - timedelta(hours=3)
        }
    ]
    
    for alert_data in alerts:
        alert = ProductionAlert(**alert_data)
        db.add(alert)
    
    db.commit()


def init_all_test_data():
    """初始化所有测试数据"""
    db: Session = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        
        print("初始化配方数据...")
        init_formulas(db)
        
        print("初始化资源数据...")
        init_resources(db)
        
        print("初始化生产计划数据...")
        init_production_plans(db)
        
        print("初始化生产任务数据...")
        init_production_orders(db)
        
        print("初始化生产日志数据...")
        init_production_logs(db)
        
        print("初始化生产预警数据...")
        init_production_alerts(db)
        
        print("测试数据初始化完成！")
        
    except Exception as e:
        print(f"初始化测试数据失败: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    init_all_test_data()
