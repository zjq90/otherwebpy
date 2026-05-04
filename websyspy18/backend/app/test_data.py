"""
测试数据生成模块
用于生成系统测试数据，辅助功能测试
"""
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import random
import json

from app.database import SessionLocal
from app.models.equipment import (
    Equipment, InspectionPlan, InspectionRecord,
    MaintenancePlan, MaintenanceRecord, FaultRecord
)
from app.models.decoration import (
    DecorationApplication, DecorationDeposit, DecorationInspection
)
from app.models.contract import (
    Supplier, Contract, ContractPayment, ServiceEvaluation
)

def generate_equipment_data(db: Session):
    """
    生成设备台账测试数据
    """
    equipments = [
        {
            "name": "1号电梯",
            "code": "ELEV-001",
            "category": "电梯",
            "model": "OTIS-3200",
            "manufacturer": "奥的斯电梯",
            "purchase_date": date(2020, 3, 15),
            "warranty_expiry": date(2025, 3, 15),
            "location": "A栋1-15层",
            "status": "正常",
            "description": "载客电梯，载重1000kg"
        },
        {
            "name": "2号电梯",
            "code": "ELEV-002",
            "category": "电梯",
            "model": "OTIS-3200",
            "manufacturer": "奥的斯电梯",
            "purchase_date": date(2020, 3, 15),
            "warranty_expiry": date(2025, 3, 15),
            "location": "A栋1-15层",
            "status": "正常",
            "description": "载货电梯，载重1600kg"
        },
        {
            "name": "生活水泵1号",
            "code": "PUMP-001",
            "category": "水泵",
            "model": "Grundfos-CR10",
            "manufacturer": "格兰富",
            "purchase_date": date(2019, 6, 20),
            "warranty_expiry": date(2024, 6, 20),
            "location": "地下室水泵房",
            "status": "正常",
            "description": "生活供水主泵"
        },
        {
            "name": "消防水泵1号",
            "code": "PUMP-002",
            "category": "水泵",
            "model": "XBD8.0/30",
            "manufacturer": "上海凯泉",
            "purchase_date": date(2019, 6, 20),
            "warranty_expiry": date(2024, 6, 20),
            "location": "地下室水泵房",
            "status": "故障",
            "description": "消防专用水泵"
        },
        {
            "name": "中央空调主机",
            "code": "AC-001",
            "category": "空调",
            "model": "Carrier-30XW",
            "manufacturer": "开利",
            "purchase_date": date(2021, 4, 10),
            "warranty_expiry": date(2026, 4, 10),
            "location": "楼顶机房",
            "status": "正常",
            "description": "水冷螺杆式冷水机组"
        },
        {
            "name": "发电机",
            "code": "GEN-001",
            "category": "发电机",
            "model": "Cummins-KTA38",
            "manufacturer": "康明斯",
            "purchase_date": date(2018, 11, 5),
            "warranty_expiry": date(2023, 11, 5),
            "location": "地下室发电机房",
            "status": "维修中",
            "description": "备用发电机组，功率500KW"
        }
    ]
    
    for eq in equipments:
        db_equipment = Equipment(**eq)
        db.add(db_equipment)
    
    db.commit()
    print(f"已生成 {len(equipments)} 条设备台账数据")

def generate_inspection_plans(db: Session):
    """
    生成巡检计划测试数据
    """
    equipments = db.query(Equipment).all()
    
    cycles = ["每日", "每周", "每月", "季度"]
    inspectors = ["张三", "李四", "王五", "赵六"]
    
    for i, eq in enumerate(equipments):
        plan = InspectionPlan(
            equipment_id=eq.id,
            plan_name=f"{eq.name}巡检计划",
            cycle=cycles[i % len(cycles)],
            next_inspection_date=date.today() + timedelta(days=random.randint(1, 30)),
            inspector=random.choice(inspectors),
            items=json.dumps([
                {"name": "外观检查", "required": True},
                {"name": "运行状态", "required": True},
                {"name": "噪音检测", "required": False},
                {"name": "温度检测", "required": False}
            ], ensure_ascii=False),
            status="待执行"
        )
        db.add(plan)
    
    db.commit()
    print(f"已生成 {len(equipments)} 条巡检计划数据")

def generate_maintenance_plans(db: Session):
    """
    生成保养计划测试数据
    """
    equipments = db.query(Equipment).all()
    
    cycles = ["每月", "季度", "半年", "年度"]
    maintainers = ["维保公司A", "维保公司B", "厂家售后"]
    
    for i, eq in enumerate(equipments):
        plan = MaintenancePlan(
            equipment_id=eq.id,
            plan_name=f"{eq.name}保养计划",
            cycle=cycles[i % len(cycles)],
            next_maintenance_date=date.today() + timedelta(days=random.randint(7, 60)),
            maintainer=random.choice(maintainers),
            items=json.dumps([
                {"name": "清洁保养", "estimated_time": "2小时"},
                {"name": "润滑保养", "estimated_time": "1小时"},
                {"name": "易损件检查", "estimated_time": "1小时"}
            ], ensure_ascii=False),
            estimated_cost=random.randint(500, 5000),
            status="待执行"
        )
        db.add(plan)
    
    db.commit()
    print(f"已生成 {len(equipments)} 条保养计划数据")

def generate_fault_records(db: Session):
    """
    生成故障维修记录测试数据
    """
    equipments = db.query(Equipment).all()
    
    fault_types = ["机械故障", "电气故障", "传感器故障", "通信故障", "其他"]
    statuses = ["待处理", "处理中", "已完成", "已关闭"]
    reporters = ["物业前台", "业主投诉", "巡检发现", "自动报警"]
    
    for i in range(10):
        eq = random.choice(equipments)
        status = random.choice(statuses)
        
        fault = FaultRecord(
            equipment_id=eq.id,
            fault_code=f"FAULT-{2024001 + i}",
            fault_type=random.choice(fault_types),
            fault_description=f"{eq.name}出现异常运行情况，需要维修处理。",
            reporter=random.choice(reporters),
            assign_to="维修工程师" + ["甲", "乙", "丙"][i % 3],
            labor_cost=random.randint(200, 2000) if status in ["已完成", "已关闭"] else 0,
            parts_cost=random.randint(100, 3000) if status in ["已完成", "已关闭"] else 0,
            total_cost=0,
            status=status,
            satisfaction=random.randint(3, 5) if status in ["已完成", "已关闭"] else None
        )
        fault.total_cost = fault.labor_cost + fault.parts_cost
        db.add(fault)
    
    db.commit()
    print(f"已生成 10 条故障维修记录数据")

def generate_decoration_applications(db: Session):
    """
    生成装修申请测试数据
    """
    rooms = ["A栋101", "A栋205", "A栋308", "B栋502", "B栋701", "C栋1203", "C栋1506"]
    owners = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九"]
    phones = ["13800138001", "13800138002", "13800138003", "13800138004"]
    companies = ["诚信装修公司", "家美装饰", "雅居装修", "尚品装饰"]
    decoration_types = ["简装", "精装", "豪装"]
    statuses = ["待审批", "已通过", "已驳回", "已完成"]
    
    for i, room in enumerate(rooms):
        app = DecorationApplication(
            application_no=f"DEC-{2024001 + i}",
            room_number=room,
            owner_name=owners[i],
            owner_phone=random.choice(phones),
            decoration_company=random.choice(companies),
            company_contact="装修负责人" + ["A", "B", "C"][i % 3],
            company_phone=random.choice(phones),
            decoration_type=random.choice(decoration_types),
            estimated_start_date=date.today() - timedelta(days=random.randint(0, 60)),
            estimated_end_date=date.today() + timedelta(days=random.randint(30, 90)),
            decoration_scope="室内装修，包括水电改造、墙面地面处理",
            status=random.choice(statuses),
            approved_by="物业经理" if i % 2 == 0 else None,
            approval_date=date.today() - timedelta(days=random.randint(1, 30)) if i % 2 == 0 else None
        )
        db.add(app)
    
    db.commit()
    print(f"已生成 {len(rooms)} 条装修申请数据")

def generate_decoration_deposits(db: Session):
    """
    生成装修押金测试数据
    """
    applications = db.query(DecorationApplication).all()
    deposit_types = ["装修押金", "垃圾清运费", "出入证押金"]
    statuses = ["待缴纳", "已缴纳", "已退还"]
    
    for app in applications:
        for dtype in deposit_types[:2]:
            deposit = DecorationDeposit(
                application_id=app.id,
                deposit_type=dtype,
                amount=2000 if dtype == "装修押金" else 500,
                paid_date=date.today() - timedelta(days=random.randint(1, 30)),
                paid_by=app.owner_name,
                receipt_no=f"RCP-{random.randint(10000, 99999)}",
                status=random.choice(statuses)
            )
            db.add(deposit)
    
    db.commit()
    print(f"已生成装修押金数据")

def generate_suppliers(db: Session):
    """
    生成供应商测试数据
    """
    suppliers_data = [
        {
            "name": "洁净保洁服务公司",
            "code": "SUP-001",
            "category": "保洁",
            "contact_person": "王经理",
            "contact_phone": "13900139001",
            "address": "北京市朝阳区建国路88号",
            "business_license": "91110000MA001ABC1",
            "qualification_level": "一级",
            "status": "合作中"
        },
        {
            "name": "安保护卫有限公司",
            "code": "SUP-002",
            "category": "安保",
            "contact_person": "李队长",
            "contact_phone": "13900139002",
            "address": "北京市海淀区中关村大街1号",
            "business_license": "91110000MA002DEF2",
            "qualification_level": "一级",
            "status": "合作中"
        },
        {
            "name": "绿苑园林绿化公司",
            "code": "SUP-003",
            "category": "绿化",
            "contact_person": "张工程师",
            "contact_phone": "13900139003",
            "address": "北京市丰台区丰台路5号",
            "business_license": "91110000MA003GHI3",
            "qualification_level": "二级",
            "status": "合作中"
        },
        {
            "name": "迅捷设备维修公司",
            "code": "SUP-004",
            "category": "维修",
            "contact_person": "刘技师",
            "contact_phone": "13900139004",
            "address": "北京市通州区通州路10号",
            "business_license": "91110000MA004JKL4",
            "qualification_level": "一级",
            "status": "合作中"
        }
    ]
    
    for sup in suppliers_data:
        db_supplier = Supplier(**sup)
        db.add(db_supplier)
    
    db.commit()
    print(f"已生成 {len(suppliers_data)} 条供应商数据")

def generate_contracts(db: Session):
    """
    生成合同测试数据
    """
    suppliers = db.query(Supplier).all()
    contract_types = ["保洁服务", "安保服务", "绿化服务", "设备维修"]
    statuses = ["待执行", "执行中", "已到期", "已终止"]
    payment_cycles = ["月付", "季付", "年付"]
    
    for i, sup in enumerate(suppliers):
        contract = Contract(
            contract_no=f"CTR-{2024001 + i}",
            supplier_id=sup.id,
            contract_name=f"{sup.name}{contract_types[i % len(contract_types)]}服务合同",
            contract_type=contract_types[i % len(contract_types)],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            total_amount=random.randint(50000, 300000),
            payment_method="银行转账",
            payment_cycle=random.choice(payment_cycles),
            contract_content="详细的服务条款和质量要求...",
            sign_date=date(2023, 12, 20),
            signatory_party_a="物业公司",
            signatory_party_b=sup.contact_person,
            status="执行中"
        )
        db.add(contract)
    
    db.commit()
    print(f"已生成 {len(suppliers)} 条合同数据")

def generate_contract_payments(db: Session):
    """
    生成合同付款测试数据
    """
    contracts = db.query(Contract).all()
    statuses = ["待付款", "已付款", "已逾期"]
    
    for contract in contracts:
        for i in range(3):
            payment = ContractPayment(
                contract_id=contract.id,
                payment_no=f"PAY-{2024001 + i + contract.id * 10}",
                payment_period=f"2024年第{i+1}季度",
                amount=contract.total_amount / 4,
                due_date=date(2024, 3 * (i + 1), 1),
                actual_date=date(2024, 3 * (i + 1), 5) if i < 2 else None,
                status="已付款" if i < 2 else "待付款"
            )
            db.add(payment)
    
    db.commit()
    print(f"已生成合同付款数据")

def generate_service_evaluations(db: Session):
    """
    生成服务质量评估测试数据
    """
    suppliers = db.query(Supplier).all()
    periods = ["2024年第一季度", "2024年第二季度"]
    evaluators = ["物业经理", "品质主管", "客服主管"]
    levels = ["优秀", "良好", "合格", "不合格"]
    
    for sup in suppliers:
        for period in periods:
            scores = [random.randint(3, 5) for _ in range(5)]
            total_score = sum(scores) / len(scores)
            
            evaluation = ServiceEvaluation(
                supplier_id=sup.id,
                evaluation_date=date(2024, periods.index(period) * 3 + 3, 15),
                evaluation_period=period,
                evaluator=random.choice(evaluators),
                service_quality_score=scores[0],
                response_speed_score=scores[1],
                personnel_quality_score=scores[2],
                compliance_score=scores[3],
                cost_effectiveness_score=scores[4],
                total_score=round(total_score, 2),
                level="优秀" if total_score >= 4.5 else "良好" if total_score >= 3.5 else "合格",
                advantages="服务态度好、响应及时",
                disadvantages="部分细节仍需改进",
                improvement_suggestions="加强人员培训"
            )
            db.add(evaluation)
    
    db.commit()
    print(f"已生成服务质量评估数据")

def generate_all_test_data():
    """
    生成所有测试数据
    """
    db = SessionLocal()
    try:
        print("=" * 50)
        print("开始生成测试数据...")
        print("=" * 50)
        
        # 工程维保模块
        generate_equipment_data(db)
        generate_inspection_plans(db)
        generate_maintenance_plans(db)
        generate_fault_records(db)
        
        # 装修管理模块
        generate_decoration_applications(db)
        generate_decoration_deposits(db)
        
        # 合同与供应商模块
        generate_suppliers(db)
        generate_contracts(db)
        generate_contract_payments(db)
        generate_service_evaluations(db)
        
        print("=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_all_test_data()
