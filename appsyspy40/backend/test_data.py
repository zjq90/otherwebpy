"""
测试数据生成脚本
用于生成系统测试数据
"""
import sys
import os
from datetime import datetime, timedelta
import random
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db
from core.security import get_password_hash
from models.models import (
    User, Material, MaterialInspection, ProductionFormula,
    ProductionRecord, QualityAlert, InspectionReport, FeedingRecord
)


def generate_random_date(days_before=30):
    """生成随机日期
    """
    now = datetime.now()
    days = random.randint(0, days_before)
    return now - timedelta(days=days)


def create_test_users(db):
    """创建测试用户"""
    print("正在创建测试用户...")
    
    users_data = [
        {"username": "admin", "password": "admin123", "real_name": "系统管理员", "role": "admin", "phone": "13800138000"},
        {"username": "inspector1", "password": "123456", "real_name": "张三", "role": "inspector", "phone": "13800138001"},
        {"username": "inspector2", "password": "123456", "real_name": "李四", "role": "inspector", "phone": "13800138002"},
        {"username": "admin2", "password": "123456", "real_name": "王管理员", "role": "admin", "phone": "13800138003"},
    ]
    
    for user_data in users_data:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            real_name=user_data["real_name"],
            role=user_data["role"],
            phone=user_data["phone"]
        )
        db.add(user)
    
    db.commit()
    print(f"测试用户创建完成")


def create_test_materials(db):
    """创建测试原材料"""
    print("正在创建测试原材料...")
    
    materials_data = [
        {"material_code": "CEM001", "material_name": "P.O42.5普通硅酸盐水泥", "material_type": "cement", "supplier": "海螺水泥", "specification": "P.O42.5"},
        {"material_code": "CEM002", "material_name": "P.O52.5普通硅酸盐水泥", "material_type": "cement", "supplier": "海螺水泥", "specification": "P.O52.5"},
        {"material_code": "AGG001", "material_name": "粗骨料(碎石)", "material_type": "aggregate", "supplier": "本地砂石场", "specification": "5-25mm"},
        {"material_code": "AGG002", "material_name": "细骨料(河砂)", "material_type": "aggregate", "supplier": "本地砂石场", "specification": "中砂"},
        {"material_code": "ADM001", "material_name": "聚羧酸高效减水剂", "material_type": "admixture", "supplier": "江苏博特", "specification": "PCA-1"},
        {"material_code": "ADM002", "material_name": "萘系高效减水剂", "material_type": "admixture", "supplier": "江苏博特", "specification": "FDN"},
    ]
    
    created_count = 0
    for mat_data in materials_data:
        existing = db.query(Material).filter(Material.material_code == mat_data["material_code"]).first()
        if not existing:
            material = Material(**mat_data)
            db.add(material)
            created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试原材料")


def create_test_formulas(db):
    """创建测试生产配方"""
    print("正在创建测试生产配方...")
    
    formulas_data = [
        {
            "formula_code": "C30-001", 
            "formula_name": "C30普通混凝土",
            "concrete_grade": "C30",
            "description": "适用于一般结构",
            "cement_amount": 350,
            "sand_amount": 700,
            "stone_amount": 1050,
            "water_amount": 180,
            "admixture_amount": 8.75,
            "fly_ash_amount": 70,
            "cement_tolerance": 2.0,
            "aggregate_tolerance": 3.0,
            "water_tolerance": 1.0
        },
        {
            "formula_code": "C40-001", 
            "formula_name": "C40高强度混凝土",
            "concrete_grade": "C40",
            "description": "适用于高强度要求结构",
            "cement_amount": 420,
            "sand_amount": 650,
            "stone_amount": 1100,
            "water_amount": 170,
            "admixture_amount": 10.5,
            "fly_ash_amount": 60,
            "cement_tolerance": 2.0,
            "aggregate_tolerance": 3.0,
            "water_tolerance": 1.0
        },
        {
            "formula_code": "C25-001", 
            "formula_name": "C25泵送混凝土",
            "concrete_grade": "C25",
            "description": "适用于泵送施工",
            "cement_amount": 300,
            "sand_amount": 750,
            "stone_amount": 1000,
            "water_amount": 185,
            "admixture_amount": 7.5,
            "fly_ash_amount": 80,
            "cement_tolerance": 2.0,
            "aggregate_tolerance": 3.0,
            "water_tolerance": 1.0
        },
    ]
    
    created_count = 0
    for formula_data in formulas_data:
        existing = db.query(ProductionFormula).filter(
            ProductionFormula.formula_code == formula_data["formula_code"]
        ).first()
        if not existing:
            formula = ProductionFormula(**formula_data)
            db.add(formula)
            created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试生产配方")


def create_test_inspections(db):
    """创建测试原材料检验记录"""
    print("正在创建测试原材料检验记录...")
    
    users = db.query(User).all()
    materials = db.query(Material).all()
    
    if not users or not materials:
        print("用户或原材料数据不足，跳过检验记录创建")
        return
    
    created_count = 0
    for i in range(10):
        material = random.choice(materials)
        inspector = random.choice(users)
        arrival_date = generate_random_date()
        batch_no = f"BATCH-{random.randint(10000, 99999)}"
        
        # 根据材料类型生成检验数据
        inspection_data = {
            "inspection_no": f"INS{arrival_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
            "material_id": material.id,
            "batch_no": batch_no,
            "arrival_date": arrival_date,
            "inspector_id": inspector.id,
            "inspection_date": arrival_date,
        }
        
        # 根据材料类型设置检验指标
        is_qualified = random.choice([True, True, True, False])  # 75%合格
        
        if material.material_type == "cement":
            inspection_data.update({
                "cement_strength_3d": 25.0 + random.uniform(-5, 5) if is_qualified else 15.0,
                "cement_strength_28d": 50.0 + random.uniform(-5, 5) if is_qualified else 35.0,
                "cement_fineness": 5.0 + random.uniform(0, 5) if is_qualified else 12.0,
                "water_content": random.uniform(0.5, 2.0),
                "impurity_content": random.uniform(0.1, 0.5),
            })
        elif material.material_type == "aggregate":
            # 骨料级配数据（JSON格式）
            gradation = {
                "0.15mm": random.uniform(0, 5),
                "0.3mm": random.uniform(5, 15),
                "0.6mm": random.uniform(15, 30),
                "1.18mm": random.uniform(30, 50),
                "2.36mm": random.uniform(50, 70),
                "4.75mm": random.uniform(70, 90),
                "9.5mm": random.uniform(90, 100),
            }
            inspection_data.update({
                "aggregate_gradation": json.dumps(gradation, ensure_ascii=False),
                "water_content": random.uniform(2.0, 4.0),
                "impurity_content": random.uniform(0.3, 0.8) if is_qualified else 1.5,
            })
        elif material.material_type == "admixture":
            # 外加剂性能数据
            performance = {
                "减水率": 20 + random.uniform(-5, 5),
                "含气量": random.uniform(2.0, 4.0),
                "凝结时间差": random.uniform(-60, 120),
            }
            inspection_data.update({
                "admixture_performance": json.dumps(performance, ensure_ascii=False),
                "water_content": random.uniform(1.0, 3.0),
            })
        
        inspection_data.update({
            "is_qualified": is_qualified,
            "status": "合格" if is_qualified else "禁用",
            "remarks": "自动生成测试数据" if is_qualified else "检验不合格，禁用",
        })
        
        inspection = MaterialInspection(**inspection_data)
        db.add(inspection)
        created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试检验记录")


def create_test_productions(db):
    """创建测试生产记录"""
    print("正在创建测试生产记录...")
    
    formulas = db.query(ProductionFormula).all()
    users = db.query(User).all()
    
    if not formulas or not users:
        print("配方或用户数据不足，跳过生产记录创建")
        return
    
    trucks = ["豫A-12345", "豫A-12346", "豫A-12347", "豫A-12348", "豫A-12349"]
    
    created_count = 0
    for i in range(15):
        formula = random.choice(formulas)
        operator = random.choice(users)
        truck_no = random.choice(trucks)
        production_date = generate_random_date()
        
        # 生成二维码
        qr_code = f"QR{production_date.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # 随机决定是否有异常
        has_issue = random.choice([True, False, False, False])  # 25%概率有问题
        target_duration = random.randint(60, 120)
        actual_duration = target_duration - random.randint(0, 30) if has_issue else target_duration
        
        production = ProductionRecord(
            production_no=f"PRO{production_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
            formula_id=formula.id,
            qr_code=qr_code,
            truck_no=truck_no,
            mix_volume=random.uniform(6, 12),
            mix_duration=actual_duration,
            target_mix_duration=target_duration,
            production_date=production_date,
            status="异常" if has_issue else "正常",
            operator_id=operator.id
        )
        db.add(production)
        db.flush()
        
        # 创建投料记录
        create_feeding_records(db, production, formula, has_issue)
        created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试生产记录")


def create_feeding_records(db, production, formula, has_issue):
    """创建投料记录"""
    materials = ["cement", "sand", "stone", "water", "admixture"]
    volume = production.mix_volume
    
    # 目标用量（按配方比例计算
    targets = {
        "cement": formula.cement_amount * volume,
        "sand": formula.sand_amount * volume,
        "stone": formula.stone_amount * volume,
        "water": formula.water_amount * volume,
        "admixture": formula.admixture_amount * volume if formula.admixture_amount else 0,
    }
    
    for mat_type in materials:
        target = targets.get(mat_type, 0)
        if target == 0:
            continue
        
        # 计算实际用量
        if has_issue and random.choice([True, False]):
            # 有偏差的情况
            deviation_percent = random.choice([-5, 5, -8, 8, -3])  # 超过允许偏差
        else:
            # 正常偏差
            deviation_percent = random.uniform(-1.5, 1.5)
        
        actual = target * (1 + deviation_percent / 100)
        deviation = actual - target
        
        feeding = FeedingRecord(
            production_id=production.id,
            material_type=mat_type,
            target_amount=target,
            actual_amount=actual,
            deviation=deviation,
            deviation_percent=deviation_percent,
            feeding_time=production.production_date
        )
        db.add(feeding)


def create_test_alerts(db):
    """创建测试质量预警"""
    print("正在创建测试质量预警...")
    
    productions = db.query(ProductionRecord).filter(ProductionRecord.status == "异常").all()
    
    if not productions:
        print("没有异常生产记录，跳过预警创建")
        return
    
    created_count = 0
    for prod in productions:
        # 搅拌时间不足预警
        if prod.mix_duration < prod.target_mix_duration:
            shortage = prod.target_mix_duration - prod.mix_duration
            alert = QualityAlert(
                alert_no=f"ALT{datetime.now().strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                production_id=prod.id,
                alert_type="mix_time_short",
                alert_level="严重" if shortage > 10 else "一般",
                description=f"搅拌时间不足：目标{prod.target_mix_duration}秒，实际{prod.mix_duration}秒，短缺{shortage}秒",
                deviation_data=json.dumps({
                    "target_duration": prod.target_mix_duration,
                    "actual_duration": prod.mix_duration,
                    "shortage": shortage
                }),
                status=random.choice(["待处理", "处理中", "已处理"])
            )
            if alert.status == "已处理":
                alert.handle_time = datetime.now()
                alert.handle_result = "已安排复检，结果合格"
            db.add(alert)
            created_count += 1
        
        # 配比偏差预警
        feedings = db.query(FeedingRecord).filter(FeedingRecord.production_id == prod.id).all()
        for feeding in feedings:
            if abs(feeding.deviation_percent) > 2:
                alert = QualityAlert(
                    alert_no=f"ALT{datetime.now().strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                    production_id=prod.id,
                    alert_type="mix_ratio_deviation",
                    alert_level="严重" if abs(feeding.deviation_percent) > 5 else "一般",
                    description=f"配比偏差：{feeding.material_type}目标用量{feeding.target_amount:.2f}kg，实际{feeding.actual_amount:.2f}kg，偏差{feeding.deviation_percent:.2f}%",
                    deviation_data=json.dumps({
                        "material_type": feeding.material_type,
                        "target_amount": feeding.target_amount,
                        "actual_amount": feeding.actual_amount,
                        "deviation_percent": feeding.deviation_percent
                    }),
                    status=random.choice(["待处理", "处理中", "已处理"])
                )
                if alert.status == "已处理":
                    alert.handle_time = datetime.now()
                    alert.handle_result = "已调整配比，重新生产"
                db.add(alert)
                created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试质量预警")


def create_test_reports(db):
    """创建测试检验报告"""
    print("正在创建测试检验报告...")
    
    productions = db.query(ProductionRecord).all()
    users = db.query(User).all()
    
    if not productions or not users:
        print("生产记录或用户数据不足，跳过检验报告创建")
        return
    
    created_count = 0
    for prod in productions[:5]:
        inspector = random.choice(users)
        
        report = InspectionReport(
            report_no=f"RPT{datetime.now().strftime('%Y%m%d')}{random.randint(100000, 999999)}",
            production_id=prod.id,
            report_type=random.choice(["factory", "site"]),
            inspection_date=prod.production_date,
            inspector_id=inspector.id,
            slump=random.uniform(120, 180),
            air_content=random.uniform(2.0, 4.0),
            temperature=random.uniform(15, 30),
            strength_7d=random.uniform(25, 35),
            strength_28d=random.uniform(35, 50),
            is_qualified=random.choice([True, True, True, False])
        )
        db.add(report)
        created_count += 1
    
    db.commit()
    print(f"创建了 {created_count} 个测试检验报告")


def main():
    """主函数"""
    print("=" * 50)
    print("混凝土质量追溯系统 - 测试数据生成")
    print("=" * 50)
    
    # 初始化数据库
    init_db()
    
    db = SessionLocal()
    
    try:
        create_test_users(db)
        create_test_materials(db)
        create_test_formulas(db)
        create_test_inspections(db)
        create_test_productions(db)
        create_test_alerts(db)
        create_test_reports(db)
        
        print("=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        print("测试账号：")
        print("  管理员: admin / admin123")
        print("  检验员: inspector1 / 123456")
        print("  检验员: inspector2 / 123456")
        print("=" * 50)
        
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
