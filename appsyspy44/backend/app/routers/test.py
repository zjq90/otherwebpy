from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.production import ProductionDataCreate
from app.schemas.quality import QualityDataCreate
from app.schemas.equipment import EquipmentCreate
from app.crud.production_crud import ProductionDataCRUD
import json

router = APIRouter()

@router.post("/test/generate-data")
def generate_test_data_endpoint(
    days: int = Query(90, description="生成多少天的数据"),
    db: Session = Depends(get_db)
):
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        from scripts.generate_test_data import generate_test_data
        generate_test_data()
        
        return {
            "success": True,
            "message": f"已成功生成 {days} 天的测试数据",
            "note": "如果未能成功生成，请直接运行: python scripts/generate_test_data.py",
            "timestamp": datetime.now().isoformat()
        }
    except ImportError as e:
        return {
            "success": False,
            "message": f"导入失败: {str(e)}",
            "note": "请直接运行: python scripts/generate_test_data.py 来生成测试数据",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"生成数据失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/test/connection")
def test_connection(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        
        return {
            "success": True,
            "message": "数据库连接正常",
            "result": row._asdict() if row else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"数据库连接失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/test/api-status")
def test_api_status():
    return {
        "success": True,
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "production": [
                "GET /api/v1/production/production-data",
                "POST /api/v1/production/production-data",
                "GET /api/v1/production/report/daily",
                "GET /api/v1/production/report/weekly",
                "GET /api/v1/production/report/monthly"
            ],
            "quality": [
                "GET /api/v1/quality/quality-data",
                "GET /api/v1/quality/quality-trend",
                "GET /api/v1/quality/chart/quality-pass-rate"
            ],
            "equipment": [
                "GET /api/v1/equipment/equipment",
                "GET /api/v1/equipment/operating-rate-chart",
                "GET /api/v1/equipment/downtime-chart"
            ],
            "test": [
                "POST /api/v1/test/generate-data",
                "GET /api/v1/test/connection",
                "GET /api/v1/test/run-all"
            ]
        }
    }

@router.get("/test/run-all")
def run_all_tests(
    db: Session = Depends(get_db)
):
    test_results = []
    
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        test_results.append({
            "test": "数据库连接",
            "status": "passed",
            "message": "数据库连接正常"
        })
    except Exception as e:
        test_results.append({
            "test": "数据库连接",
            "status": "failed",
            "message": str(e)
        })
    
    try:
        from app.models.production import ProductionData
        count = db.query(ProductionData).count()
        test_results.append({
            "test": "生产数据表",
            "status": "passed",
            "message": f"表存在，数据条数: {count}"
        })
    except Exception as e:
        test_results.append({
            "test": "生产数据表",
            "status": "failed",
            "message": str(e)
        })
    
    try:
        from app.models.quality import QualityData
        count = db.query(QualityData).count()
        test_results.append({
            "test": "质量数据表",
            "status": "passed",
            "message": f"表存在，数据条数: {count}"
        })
    except Exception as e:
        test_results.append({
            "test": "质量数据表",
            "status": "failed",
            "message": str(e)
        })
    
    try:
        from app.models.equipment import Equipment
        count = db.query(Equipment).count()
        test_results.append({
            "test": "设备数据表",
            "status": "passed",
            "message": f"表存在，数据条数: {count}"
        })
    except Exception as e:
        test_results.append({
            "test": "设备数据表",
            "status": "failed",
            "message": str(e)
        })
    
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")
    total = len(test_results)
    
    return {
        "success": True,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round((passed / total) * 100, 2) if total > 0 else 0
        },
        "results": test_results,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test/sample-data")
def get_sample_data(
    data_type: str = Query("all", description="数据类型: all, production, quality, equipment"),
    limit: int = Query(10, description="返回数据条数"),
    db: Session = Depends(get_db)
):
    sample_data = {}
    
    if data_type in ["all", "production"]:
        from app.models.production import ProductionData
        production_data = db.query(ProductionData).order_by(
            ProductionData.production_date.desc()
        ).limit(limit).all()
        
        sample_data["production"] = [
            {
                "id": d.id,
                "production_date": d.production_date.isoformat() if d.production_date else None,
                "product_name": d.product_name,
                "planned_quantity": d.planned_quantity,
                "actual_quantity": d.actual_quantity,
                "qualified_quantity": d.qualified_quantity,
                "completion_rate": d.completion_rate,
                "pass_rate": d.pass_rate
            }
            for d in production_data
        ]
    
    if data_type in ["all", "quality"]:
        from app.models.quality import QualityData
        quality_data = db.query(QualityData).order_by(
            QualityData.inspection_date.desc()
        ).limit(limit).all()
        
        sample_data["quality"] = [
            {
                "id": d.id,
                "inspection_date": d.inspection_date.isoformat() if d.inspection_date else None,
                "material_name": d.material_name,
                "total_samples": d.total_samples,
                "passed_samples": d.passed_samples,
                "pass_rate": d.pass_rate
            }
            for d in quality_data
        ]
    
    if data_type in ["all", "equipment"]:
        from app.models.equipment import Equipment, EquipmentRuntime
        equipment = db.query(Equipment).limit(limit).all()
        
        sample_data["equipment"] = [
            {
                "id": e.id,
                "equipment_no": e.equipment_no,
                "equipment_name": e.equipment_name,
                "status": e.status,
                "location": e.location
            }
            for e in equipment
        ]
    
    return {
        "success": True,
        "data_type": data_type,
        "sample_data": sample_data,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test/dashboard-stats")
def get_dashboard_test_stats(
    db: Session = Depends(get_db)
):
    from app.models.production import ProductionData
    from app.models.quality import QualityData
    from app.models.equipment import Equipment, EquipmentRuntime
    
    today = date.today()
    
    production_today = db.query(ProductionData).filter(
        ProductionData.production_date == today
    ).all()
    
    total_actual = sum(d.actual_quantity for d in production_today)
    total_planned = sum(d.planned_quantity for d in production_today)
    total_qualified = sum(d.qualified_quantity for d in production_today)
    
    completion_rate = 0.0
    if total_planned > 0:
        completion_rate = round((total_actual / total_planned) * 100, 2)
    
    pass_rate = 0.0
    if total_actual > 0:
        pass_rate = round((total_qualified / total_actual) * 100, 2)
    
    quality_data = db.query(QualityData).filter(
        QualityData.inspection_date == today
    ).all()
    
    quality_pass_rate = 0.0
    if quality_data:
        total_samples = sum(d.total_samples for d in quality_data)
        total_passed = sum(d.passed_samples for d in quality_data)
        if total_samples > 0:
            quality_pass_rate = round((total_passed / total_samples) * 100, 2)
    
    equipment_count = db.query(Equipment).count()
    runtime_today = db.query(EquipmentRuntime).filter(
        EquipmentRuntime.record_date == today
    ).all()
    
    equipment_rate = 0.0
    if runtime_today:
        total_planned = sum(r.planned_runtime for r in runtime_today)
        total_actual = sum(r.actual_runtime for r in runtime_today)
        if total_planned > 0:
            equipment_rate = round((total_actual / total_planned) * 100, 2)
    
    return {
        "success": True,
        "dashboard_stats": {
            "today": today.isoformat(),
            "production": {
                "total_actual": total_actual,
                "total_planned": total_planned,
                "completion_rate": completion_rate,
                "pass_rate": pass_rate
            },
            "quality": {
                "pass_rate_today": quality_pass_rate
            },
            "equipment": {
                "total_count": equipment_count,
                "operating_rate_today": equipment_rate
            }
        },
        "timestamp": datetime.now().isoformat()
    }
