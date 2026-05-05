"""
测试功能路由
用于生成测试数据和功能测试辅助
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import json

from database import get_db
from core.security import get_password_hash
from models.models import (
    User, Material, MaterialInspection, ProductionFormula,
    ProductionRecord, QualityAlert, InspectionReport, FeedingRecord
)
from schemas.schemas import (
    TestDataGenerateRequest, TestDataGenerateResponse,
    TestDataStatusResponse, ApiResponse
)

router = APIRouter()


def generate_random_date(days_before=30):
    """生成随机日期"""
    now = datetime.now()
    days = random.randint(0, days_before)
    return now - timedelta(days=days)


@router.post("/generate", response_model=ApiResponse, summary="生成测试数据")
async def generate_test_data(
    request: TestDataGenerateRequest = None,
    db: Session = Depends(get_db)
):
    """
    生成测试数据
    """
    try:
        result = {
            "users_created": 0,
            "materials_created": 0,
            "formulas_created": 0,
            "inspections_created": 0,
            "productions_created": 0,
            "alerts_created": 0,
            "reports_created": 0
        }
        
        # 创建测试用户
        users_data = [
            {"username": "admin", "password": "admin123", "real_name": "系统管理员", "role": "admin", "phone": "13800138000"},
            {"username": "inspector1", "password": "123456", "real_name": "张三", "role": "inspector", "phone": "13800138001"},
            {"username": "inspector2", "password": "123456", "real_name": "李四", "role": "inspector", "phone": "13800138002"},
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
                result["users_created"] += 1
        
        db.commit()
        
        # 创建测试原材料
        materials_data = [
            {"material_code": "CEM001", "material_name": "P.O42.5普通硅酸盐水泥", "material_type": "cement", "supplier": "海螺水泥", "specification": "P.O42.5"},
            {"material_code": "AGG001", "material_name": "粗骨料(碎石)", "material_type": "aggregate", "supplier": "本地砂石场", "specification": "5-25mm"},
            {"material_code": "AGG002", "material_name": "细骨料(河砂)", "material_type": "aggregate", "supplier": "本地砂石场", "specification": "中砂"},
            {"material_code": "ADM001", "material_name": "聚羧酸高效减水剂", "material_type": "admixture", "supplier": "江苏博特", "specification": "PCA-1"},
        ]
        
        for mat_data in materials_data:
            existing = db.query(Material).filter(Material.material_code == mat_data["material_code"]).first()
            if not existing:
                material = Material(**mat_data)
                db.add(material)
                result["materials_created"] += 1
        
        db.commit()
        
        # 创建测试配方
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
        ]
        
        for formula_data in formulas_data:
            existing = db.query(ProductionFormula).filter(
                ProductionFormula.formula_code == formula_data["formula_code"]
            ).first()
            if not existing:
                formula = ProductionFormula(**formula_data)
                db.add(formula)
                result["formulas_created"] += 1
        
        db.commit()
        
        # 创建测试检验记录
        users = db.query(User).all()
        materials = db.query(Material).all()
        
        if users and materials:
            for i in range(5):
                material = random.choice(materials)
                inspector = random.choice(users)
                arrival_date = generate_random_date()
                batch_no = f"BATCH-{random.randint(10000, 99999)}"
                
                is_qualified = random.choice([True, True, True, False])
                
                inspection_data = {
                    "inspection_no": f"INS{arrival_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                    "material_id": material.id,
                    "batch_no": batch_no,
                    "arrival_date": arrival_date,
                    "inspector_id": inspector.id,
                    "inspection_date": arrival_date,
                    "is_qualified": is_qualified,
                    "status": "合格" if is_qualified else "禁用",
                    "remarks": "自动生成测试数据" if is_qualified else "检验不合格，禁用",
                }
                
                if material.material_type == "cement":
                    inspection_data.update({
                        "cement_strength_3d": 25.0 + random.uniform(-5, 5) if is_qualified else 15.0,
                        "cement_strength_28d": 50.0 + random.uniform(-5, 5) if is_qualified else 35.0,
                        "cement_fineness": 5.0 + random.uniform(0, 5) if is_qualified else 12.0,
                        "water_content": random.uniform(0.5, 2.0),
                        "impurity_content": random.uniform(0.1, 0.5),
                    })
                elif material.material_type == "aggregate":
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
                    performance = {
                        "减水率": 20 + random.uniform(-5, 5),
                        "含气量": random.uniform(2.0, 4.0),
                        "凝结时间差": random.uniform(-60, 120),
                    }
                    inspection_data.update({
                        "admixture_performance": json.dumps(performance, ensure_ascii=False),
                        "water_content": random.uniform(1.0, 3.0),
                    })
                
                inspection = MaterialInspection(**inspection_data)
                db.add(inspection)
                result["inspections_created"] += 1
        
        db.commit()
        
        # 创建测试生产记录
        formulas = db.query(ProductionFormula).all()
        
        if formulas and users:
            trucks = ["豫A-12345", "豫A-12346", "豫A-12347"]
            
            for i in range(8):
                formula = random.choice(formulas)
                operator = random.choice(users)
                truck_no = random.choice(trucks)
                production_date = generate_random_date()
                
                qr_code = f"QR{production_date.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
                
                has_issue = random.choice([True, False, False, False])
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
                materials_feed = ["cement", "sand", "stone", "water", "admixture"]
                volume = production.mix_volume
                
                targets = {
                    "cement": formula.cement_amount * volume,
                    "sand": formula.sand_amount * volume,
                    "stone": formula.stone_amount * volume,
                    "water": formula.water_amount * volume,
                    "admixture": formula.admixture_amount * volume if formula.admixture_amount else 0,
                }
                
                for mat_type in materials_feed:
                    target = targets.get(mat_type, 0)
                    if target == 0:
                        continue
                    
                    if has_issue and random.choice([True, False]):
                        deviation_percent = random.choice([-5, 5, -8, 8, -3])
                    else:
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
                
                result["productions_created"] += 1
        
        db.commit()
        
        # 创建预警
        productions = db.query(ProductionRecord).filter(ProductionRecord.status == "异常").all()
        
        for prod in productions:
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
                result["alerts_created"] += 1
            
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
                    result["alerts_created"] += 1
        
        db.commit()
        
        # 创建检验报告
        productions_all = db.query(ProductionRecord).all()
        
        if productions_all and users:
            for prod in productions_all[:3]:
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
                result["reports_created"] += 1
        
        db.commit()
        
        total_created = sum(result.values())
        
        response_data = TestDataGenerateResponse(
            **result,
            test_accounts={
                "admin": {"username": "admin", "password": "admin123", "role": "管理员"},
                "inspector1": {"username": "inspector1", "password": "123456", "role": "质量检测员"},
                "inspector2": {"username": "inspector2", "password": "123456", "role": "质量检测员"}
            }
        )
        
        return ApiResponse(
            code=200,
            message=f"测试数据生成成功，共创建 {total_created} 条数据",
            data=response_data.model_dump()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成测试数据失败: {str(e)}")


@router.get("/status", response_model=ApiResponse, summary="获取测试数据状态")
async def get_test_data_status(
    db: Session = Depends(get_db)
):
    """
    获取测试数据状态
    """
    try:
        user_count = db.query(User).count()
        material_count = db.query(Material).count()
        formula_count = db.query(ProductionFormula).count()
        inspection_count = db.query(MaterialInspection).count()
        production_count = db.query(ProductionRecord).count()
        alert_count = db.query(QualityAlert).count()
        report_count = db.query(InspectionReport).count()
        
        response_data = TestDataStatusResponse(
            has_test_data=user_count > 0 or material_count > 0,
            user_count=user_count,
            material_count=material_count,
            formula_count=formula_count,
            inspection_count=inspection_count,
            production_count=production_count,
            alert_count=alert_count,
            report_count=report_count
        )
        
        return ApiResponse(
            code=200,
            message="获取状态成功",
            data=response_data.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/clear", response_model=ApiResponse, summary="清除测试数据")
async def clear_test_data(
    db: Session = Depends(get_db)
):
    """
    清除测试数据（谨慎使用）
    """
    try:
        # 按依赖顺序删除
        db.query(FeedingRecord).delete()
        db.query(InspectionReport).delete()
        db.query(QualityAlert).delete()
        db.query(ProductionRecord).delete()
        db.query(ProductionFormula).delete()
        db.query(MaterialInspection).delete()
        db.query(Material).delete()
        db.query(User).filter(User.username != "admin").delete()
        
        db.commit()
        
        return ApiResponse(
            code=200,
            message="测试数据已清除",
            data={"cleared": True}
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清除数据失败: {str(e)}")
