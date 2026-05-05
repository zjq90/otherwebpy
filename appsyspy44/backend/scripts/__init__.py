import sys
import os
from datetime import date, datetime, timedelta
from random import randint, uniform, choice
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.production import ProductionData, ProductionTask
from app.models.quality import QualityData, ProductStrength
from app.models.equipment import Equipment, EquipmentRuntime, EquipmentFault, EquipmentMaintenance

def generate_test_data():
    db: Session = SessionLocal()
    
    try:
        print("开始生成测试数据...")
        
        products = ["水泥A类", "水泥B类", "水泥C类", "混凝土C30", "混凝土C40", "混凝土C50"]
        shifts = ["早班", "中班", "晚班"]
        operators = ["张三", "李四", "王五", "赵六", "钱七"]
        materials = ["石灰石", "粘土", "铁矿粉", "石膏", "粉煤灰"]
        suppliers = ["供应商A", "供应商B", "供应商C", "供应商D"]
        inspectors = ["质检员1", "质检员2", "质检员3"]
        equipment_types = ["球磨机", "回转窑", "破碎机", "输送机", "包装机"]
        equipment_status = ["正常", "运行中", "待维修", "停用"]
        fault_types = ["机械故障", "电气故障", "润滑故障", "磨损故障"]
        fault_levels = ["轻微", "一般", "严重"]
        maintenance_types = ["日常保养", "一级保养", "二级保养", "大修"]
        
        start_date = date.today() - timedelta(days=90)
        
        print("创建设备数据...")
        equipments = []
        for i in range(10):
            equipment = Equipment(
                equipment_no=f"EQ{2026001 + i:06d}",
                equipment_name=f"{choice(equipment_types)}-{i+1}",
                equipment_type=choice(equipment_types),
                model=f"Model-{randint(100, 999)}",
                location=f"车间{randint(1, 5)}区",
                purchase_date=start_date - timedelta(days=randint(365, 1000)),
                status=choice(equipment_status),
                responsible_person=choice(operators)
            )
            db.add(equipment)
            equipments.append(equipment)
        db.commit()
        
        print("创建生产数据...")
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            for shift in shifts:
                for _ in range(2):
                    planned = randint(800, 1200)
                    actual = int(planned * uniform(0.85, 1.05))
                    qualified = int(actual * uniform(0.92, 0.99))
                    
                    production = ProductionData(
                        production_date=current_date,
                        shift=shift,
                        product_name=choice(products),
                        planned_quantity=planned,
                        actual_quantity=actual,
                        qualified_quantity=qualified,
                        work_hours=uniform(7.5, 8.5),
                        operator=choice(operators),
                        remarks="自动生成测试数据"
                    )
                    db.add(production)
        db.commit()
        
        print("创建生产任务数据...")
        for i in range(20):
            task_date = start_date + timedelta(days=randint(0, 80))
            task = ProductionTask(
                task_no=f"TASK{2026001 + i:06d}",
                product_name=choice(products),
                planned_quantity=randint(5000, 20000),
                start_date=task_date,
                end_date=task_date + timedelta(days=randint(3, 10)),
                priority=randint(1, 3),
                status=choice(["pending", "in_progress", "completed"]),
                assigned_to=choice(operators),
                description=f"生产任务 {i+1}"
            )
            db.add(task)
        db.commit()
        
        print("创建质量检验数据...")
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            for _ in range(3):
                total = randint(50, 200)
                passed = int(total * uniform(0.88, 0.98))
                failed = total - passed
                
                quality = QualityData(
                    inspection_date=current_date,
                    inspection_type=choice(["原材料检验", "半成品检验", "成品检验"]),
                    material_name=choice(materials),
                    batch_no=f"B{2026001 + i:06d}",
                    supplier=choice(suppliers),
                    total_samples=total,
                    passed_samples=passed,
                    failed_samples=failed,
                    inspector=choice(inspectors),
                    inspection_result="合格" if passed / total > 0.95 else "不合格",
                    remarks="自动生成测试数据"
                )
                db.add(quality)
        db.commit()
        
        print("创建产品强度数据...")
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            for _ in range(2):
                standard = uniform(40.0, 60.0)
                actual = standard * uniform(0.95, 1.1)
                test_count = randint(10, 30)
                pass_count = int(test_count * uniform(0.9, 1.0))
                
                strength = ProductStrength(
                    test_date=current_date,
                    product_name=choice(products),
                    batch_no=f"SB{2026001 + i:06d}",
                    strength_standard=round(standard, 2),
                    strength_actual=round(actual, 2),
                    test_count=test_count,
                    pass_count=pass_count,
                    tester=choice(inspectors),
                    is_qualified="合格" if pass_count / test_count > 0.9 else "不合格",
                    remarks="自动生成测试数据"
                )
                db.add(strength)
        db.commit()
        
        print("创建设备运行数据...")
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            for equipment in equipments:
                planned = 24.0
                actual = uniform(18.0, 24.0)
                downtime = planned - actual
                standby = uniform(0.0, 2.0)
                
                runtime = EquipmentRuntime(
                    equipment_id=equipment.id,
                    record_date=current_date,
                    planned_runtime=planned,
                    actual_runtime=round(actual, 2),
                    downtime=round(downtime, 2),
                    standby_time=round(standby, 2),
                    operator=choice(operators),
                    remarks="自动生成测试数据"
                )
                db.add(runtime)
        db.commit()
        
        print("创建设备故障数据...")
        for i in range(50):
            fault_date = start_date + timedelta(days=randint(0, 89))
            equipment = choice(equipments)
            
            fault = EquipmentFault(
                equipment_id=equipment.id,
                fault_date=fault_date,
                fault_type=choice(fault_types),
                fault_description=f"设备故障描述 {i+1}",
                fault_level=choice(fault_levels),
                downtime_duration=uniform(0.5, 8.0),
                repair_person=choice(operators),
                repair_cost=uniform(500.0, 5000.0),
                status="已修复",
                remarks="自动生成测试数据"
            )
            db.add(fault)
        db.commit()
        
        print("创建设备保养数据...")
        for i in range(60):
            plan_date = start_date + timedelta(days=randint(0, 89))
            equipment = choice(equipments)
            is_completed = randint(0, 1)
            
            maintenance = EquipmentMaintenance(
                equipment_id=equipment.id,
                plan_date=plan_date,
                actual_date=plan_date + timedelta(days=randint(-1, 2)) if is_completed else None,
                maintenance_type=choice(maintenance_types),
                maintenance_content=f"保养内容 {i+1}",
                maintenance_person=choice(operators),
                status="已完成" if is_completed else "待执行",
                is_completed=is_completed,
                remarks="自动生成测试数据"
            )
            db.add(maintenance)
        db.commit()
        
        print("测试数据生成完成！")
        
    except Exception as e:
        print(f"生成数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    generate_test_data()
