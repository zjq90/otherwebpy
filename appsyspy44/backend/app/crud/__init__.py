from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.production import ProductionData, ProductionTask
from app.schemas.production import ProductionDataCreate, ProductionDataUpdate, ProductionTaskCreate, ProductionTaskUpdate

class ProductionDataCRUD:
    @staticmethod
    def get_by_id(db: Session, data_id: int) -> Optional[ProductionData]:
        return db.query(ProductionData).filter(ProductionData.id == data_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ProductionData]:
        return db.query(ProductionData).order_by(ProductionData.production_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_date_range(db: Session, start_date: date, end_date: date) -> List[ProductionData]:
        return db.query(ProductionData).filter(
            ProductionData.production_date >= start_date,
            ProductionData.production_date <= end_date
        ).order_by(ProductionData.production_date).all()

    @staticmethod
    def create(db: Session, data: ProductionDataCreate) -> ProductionData:
        db_data = ProductionData(**data.model_dump())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data

    @staticmethod
    def update(db: Session, data_id: int, data: ProductionDataUpdate) -> Optional[ProductionData]:
        db_data = ProductionDataCRUD.get_by_id(db, data_id)
        if db_data:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(db_data, key, value)
            db.commit()
            db.refresh(db_data)
        return db_data

    @staticmethod
    def delete(db: Session, data_id: int) -> bool:
        db_data = ProductionDataCRUD.get_by_id(db, data_id)
        if db_data:
            db.delete(db_data)
            db.commit()
            return True
        return False

    @staticmethod
    def get_daily_report(db: Session, report_date: date):
        data = db.query(ProductionData).filter(
            ProductionData.production_date == report_date
        ).all()
        
        total_planned = sum(d.planned_quantity for d in data)
        total_actual = sum(d.actual_quantity for d in data)
        total_qualified = sum(d.qualified_quantity for d in data)
        
        avg_completion = 0.0
        if total_planned > 0:
            avg_completion = round((total_actual / total_planned) * 100, 2)
        
        avg_pass = 0.0
        if total_actual > 0:
            avg_pass = round((total_qualified / total_actual) * 100, 2)
        
        daily_data = []
        for d in data:
            daily_data.append({
                "date": report_date.isoformat(),
                "actual_quantity": d.actual_quantity,
                "planned_quantity": d.planned_quantity,
                "completion_rate": d.completion_rate,
                "qualified_quantity": d.qualified_quantity,
                "pass_rate": d.pass_rate,
                "product_name": d.product_name
            })
        
        return {
            "period": f"日报 - {report_date}",
            "total_planned": total_planned,
            "total_actual": total_actual,
            "total_qualified": total_qualified,
            "avg_completion_rate": avg_completion,
            "avg_pass_rate": avg_pass,
            "data": daily_data
        }

    @staticmethod
    def get_weekly_report(db: Session, week_start: date):
        week_end = week_start + timedelta(days=6)
        data = db.query(ProductionData).filter(
            ProductionData.production_date >= week_start,
            ProductionData.production_date <= week_end
        ).order_by(ProductionData.production_date).all()
        
        daily_stats = {}
        for d in data:
            day_key = d.production_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "planned": 0,
                    "actual": 0,
                    "qualified": 0
                }
            daily_stats[day_key]["planned"] += d.planned_quantity
            daily_stats[day_key]["actual"] += d.actual_quantity
            daily_stats[day_key]["qualified"] += d.qualified_quantity
        
        total_planned = sum(s["planned"] for s in daily_stats.values())
        total_actual = sum(s["actual"] for s in daily_stats.values())
        total_qualified = sum(s["qualified"] for s in daily_stats.values())
        
        avg_completion = 0.0
        if total_planned > 0:
            avg_completion = round((total_actual / total_planned) * 100, 2)
        
        avg_pass = 0.0
        if total_actual > 0:
            avg_pass = round((total_qualified / total_actual) * 100, 2)
        
        weekly_data = []
        for day, stats in daily_stats.items():
            completion = 0.0
            if stats["planned"] > 0:
                completion = round((stats["actual"] / stats["planned"]) * 100, 2)
            
            pass_rate = 0.0
            if stats["actual"] > 0:
                pass_rate = round((stats["qualified"] / stats["actual"]) * 100, 2)
            
            weekly_data.append({
                "date": day,
                "actual_quantity": stats["actual"],
                "planned_quantity": stats["planned"],
                "completion_rate": completion,
                "qualified_quantity": stats["qualified"],
                "pass_rate": pass_rate
            })
        
        weekly_data.sort(key=lambda x: x["date"])
        
        return {
            "period": f"周报 - {week_start} 至 {week_end}",
            "total_planned": total_planned,
            "total_actual": total_actual,
            "total_qualified": total_qualified,
            "avg_completion_rate": avg_completion,
            "avg_pass_rate": avg_pass,
            "data": weekly_data
        }

    @staticmethod
    def get_monthly_report(db: Session, year: int, month: int):
        import calendar
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        data = db.query(ProductionData).filter(
            ProductionData.production_date >= start_date,
            ProductionData.production_date <= end_date
        ).order_by(ProductionData.production_date).all()
        
        daily_stats = {}
        for d in data:
            day_key = d.production_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "planned": 0,
                    "actual": 0,
                    "qualified": 0
                }
            daily_stats[day_key]["planned"] += d.planned_quantity
            daily_stats[day_key]["actual"] += d.actual_quantity
            daily_stats[day_key]["qualified"] += d.qualified_quantity
        
        total_planned = sum(s["planned"] for s in daily_stats.values())
        total_actual = sum(s["actual"] for s in daily_stats.values())
        total_qualified = sum(s["qualified"] for s in daily_stats.values())
        
        avg_completion = 0.0
        if total_planned > 0:
            avg_completion = round((total_actual / total_planned) * 100, 2)
        
        avg_pass = 0.0
        if total_actual > 0:
            avg_pass = round((total_qualified / total_actual) * 100, 2)
        
        monthly_data = []
        for day, stats in daily_stats.items():
            completion = 0.0
            if stats["planned"] > 0:
                completion = round((stats["actual"] / stats["planned"]) * 100, 2)
            
            pass_rate = 0.0
            if stats["actual"] > 0:
                pass_rate = round((stats["qualified"] / stats["actual"]) * 100, 2)
            
            monthly_data.append({
                "date": day,
                "actual_quantity": stats["actual"],
                "planned_quantity": stats["planned"],
                "completion_rate": completion,
                "qualified_quantity": stats["qualified"],
                "pass_rate": pass_rate
            })
        
        monthly_data.sort(key=lambda x: x["date"])
        
        return {
            "period": f"月报 - {year}年{month}月",
            "total_planned": total_planned,
            "total_actual": total_actual,
            "total_qualified": total_qualified,
            "avg_completion_rate": avg_completion,
            "avg_pass_rate": avg_pass,
            "data": monthly_data
        }

class ProductionTaskCRUD:
    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Optional[ProductionTask]:
        return db.query(ProductionTask).filter(ProductionTask.id == task_id).first()

    @staticmethod
    def get_by_task_no(db: Session, task_no: str) -> Optional[ProductionTask]:
        return db.query(ProductionTask).filter(ProductionTask.task_no == task_no).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ProductionTask]:
        return db.query(ProductionTask).order_by(ProductionTask.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, task: ProductionTaskCreate) -> ProductionTask:
        db_task = ProductionTask(**task.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def update(db: Session, task_id: int, task: ProductionTaskUpdate) -> Optional[ProductionTask]:
        db_task = ProductionTaskCRUD.get_by_id(db, task_id)
        if db_task:
            for key, value in task.model_dump(exclude_unset=True).items():
                setattr(db_task, key, value)
            db.commit()
            db.refresh(db_task)
        return db_task

    @staticmethod
    def delete(db: Session, task_id: int) -> bool:
        db_task = ProductionTaskCRUD.get_by_id(db, task_id)
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False
