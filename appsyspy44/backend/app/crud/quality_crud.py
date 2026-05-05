from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.quality import QualityData, ProductStrength
from app.schemas.quality import QualityDataCreate, QualityDataUpdate, ProductStrengthCreate, ProductStrengthUpdate

class QualityDataCRUD:
    @staticmethod
    def get_by_id(db: Session, data_id: int) -> Optional[QualityData]:
        return db.query(QualityData).filter(QualityData.id == data_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[QualityData]:
        return db.query(QualityData).order_by(QualityData.inspection_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_date_range(db: Session, start_date: date, end_date: date) -> List[QualityData]:
        return db.query(QualityData).filter(
            QualityData.inspection_date >= start_date,
            QualityData.inspection_date <= end_date
        ).order_by(QualityData.inspection_date).all()

    @staticmethod
    def create(db: Session, data: QualityDataCreate) -> QualityData:
        db_data = QualityData(**data.model_dump())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data

    @staticmethod
    def update(db: Session, data_id: int, data: QualityDataUpdate) -> Optional[QualityData]:
        db_data = QualityDataCRUD.get_by_id(db, data_id)
        if db_data:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(db_data, key, value)
            db.commit()
            db.refresh(db_data)
        return db_data

    @staticmethod
    def delete(db: Session, data_id: int) -> bool:
        db_data = QualityDataCRUD.get_by_id(db, data_id)
        if db_data:
            db.delete(db_data)
            db.commit()
            return True
        return False

    @staticmethod
    def get_quality_trend(db: Session, start_date: date, end_date: date):
        data = db.query(QualityData).filter(
            QualityData.inspection_date >= start_date,
            QualityData.inspection_date <= end_date
        ).order_by(QualityData.inspection_date).all()
        
        daily_stats = {}
        total_samples = 0
        total_passed = 0
        
        for d in data:
            day_key = d.inspection_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "total": 0,
                    "passed": 0,
                    "materials": set()
                }
            daily_stats[day_key]["total"] += d.total_samples
            daily_stats[day_key]["passed"] += d.passed_samples
            daily_stats[day_key]["materials"].add(d.material_name)
            total_samples += d.total_samples
            total_passed += d.passed_samples
        
        avg_pass_rate = 0.0
        if total_samples > 0:
            avg_pass_rate = round((total_passed / total_samples) * 100, 2)
        
        trend_data = []
        for day, stats in daily_stats.items():
            pass_rate = 0.0
            if stats["total"] > 0:
                pass_rate = round((stats["passed"] / stats["total"]) * 100, 2)
            
            materials_list = list(stats["materials"])
            material_name = materials_list[0] if materials_list else None
            
            trend_data.append({
                "date": day,
                "pass_rate": pass_rate,
                "material_name": material_name,
                "total_samples": stats["total"],
                "passed_samples": stats["passed"]
            })
        
        trend_data.sort(key=lambda x: x["date"])
        
        return {
            "period": f"{start_date} 至 {end_date}",
            "avg_pass_rate": avg_pass_rate,
            "total_samples": total_samples,
            "total_passed": total_passed,
            "data": trend_data
        }

class ProductStrengthCRUD:
    @staticmethod
    def get_by_id(db: Session, data_id: int) -> Optional[ProductStrength]:
        return db.query(ProductStrength).filter(ProductStrength.id == data_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ProductStrength]:
        return db.query(ProductStrength).order_by(ProductStrength.test_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_date_range(db: Session, start_date: date, end_date: date) -> List[ProductStrength]:
        return db.query(ProductStrength).filter(
            ProductStrength.test_date >= start_date,
            ProductStrength.test_date <= end_date
        ).order_by(ProductStrength.test_date).all()

    @staticmethod
    def create(db: Session, data: ProductStrengthCreate) -> ProductStrength:
        db_data = ProductStrength(**data.model_dump())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data

    @staticmethod
    def update(db: Session, data_id: int, data: ProductStrengthUpdate) -> Optional[ProductStrength]:
        db_data = ProductStrengthCRUD.get_by_id(db, data_id)
        if db_data:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(db_data, key, value)
            db.commit()
            db.refresh(db_data)
        return db_data

    @staticmethod
    def delete(db: Session, data_id: int) -> bool:
        db_data = ProductStrengthCRUD.get_by_id(db, data_id)
        if db_data:
            db.delete(db_data)
            db.commit()
            return True
        return False

    @staticmethod
    def get_strength_trend(db: Session, start_date: date, end_date: date):
        data = db.query(ProductStrength).filter(
            ProductStrength.test_date >= start_date,
            ProductStrength.test_date <= end_date
        ).order_by(ProductStrength.test_date).all()
        
        daily_stats = {}
        total_test = 0
        total_pass = 0
        
        for d in data:
            day_key = d.test_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "avg_strength": [],
                    "standard": d.strength_standard,
                    "test_count": 0,
                    "pass_count": 0,
                    "product": d.product_name
                }
            daily_stats[day_key]["avg_strength"].append(d.strength_actual)
            daily_stats[day_key]["test_count"] += d.test_count
            daily_stats[day_key]["pass_count"] += d.pass_count
            total_test += d.test_count
            total_pass += d.pass_count
        
        avg_pass_rate = 0.0
        if total_test > 0:
            avg_pass_rate = round((total_pass / total_test) * 100, 2)
        
        trend_data = []
        for day, stats in daily_stats.items():
            avg_actual = round(sum(stats["avg_strength"]) / len(stats["avg_strength"]), 2) if stats["avg_strength"] else 0
            pass_rate = round((stats["pass_count"] / stats["test_count"]) * 100, 2) if stats["test_count"] > 0 else 0
            strength_ratio = round((avg_actual / stats["standard"]) * 100, 2) if stats["standard"] > 0 else 0
            
            trend_data.append({
                "date": day,
                "avg_actual_strength": avg_actual,
                "standard_strength": stats["standard"],
                "pass_rate": pass_rate,
                "product_name": stats["product"]
            })
        
        trend_data.sort(key=lambda x: x["date"])
        
        avg_strength_ratio = 0.0
        if trend_data:
            ratios = [d["pass_rate"] for d in trend_data]
            avg_strength_ratio = round(sum(ratios) / len(ratios), 2)
        
        return {
            "period": f"{start_date} 至 {end_date}",
            "avg_pass_rate": avg_pass_rate,
            "avg_strength_ratio": avg_strength_ratio,
            "data": trend_data
        }
