from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.equipment import Equipment, EquipmentRuntime, EquipmentFault, EquipmentMaintenance
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate,
    EquipmentRuntimeCreate, EquipmentRuntimeUpdate,
    EquipmentFaultCreate, EquipmentFaultUpdate,
    EquipmentMaintenanceCreate, EquipmentMaintenanceUpdate
)

class EquipmentCRUD:
    @staticmethod
    def get_by_id(db: Session, equipment_id: int) -> Optional[Equipment]:
        return db.query(Equipment).filter(Equipment.id == equipment_id).first()

    @staticmethod
    def get_by_no(db: Session, equipment_no: str) -> Optional[Equipment]:
        return db.query(Equipment).filter(Equipment.equipment_no == equipment_no).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Equipment]:
        return db.query(Equipment).order_by(Equipment.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, equipment: EquipmentCreate) -> Equipment:
        db_equipment = Equipment(**equipment.model_dump())
        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)
        return db_equipment

    @staticmethod
    def update(db: Session, equipment_id: int, equipment: EquipmentUpdate) -> Optional[Equipment]:
        db_equipment = EquipmentCRUD.get_by_id(db, equipment_id)
        if db_equipment:
            for key, value in equipment.model_dump(exclude_unset=True).items():
                setattr(db_equipment, key, value)
            db.commit()
            db.refresh(db_equipment)
        return db_equipment

    @staticmethod
    def delete(db: Session, equipment_id: int) -> bool:
        db_equipment = EquipmentCRUD.get_by_id(db, equipment_id)
        if db_equipment:
            db.delete(db_equipment)
            db.commit()
            return True
        return False

    @staticmethod
    def get_operating_rate_by_date_range(db: Session, start_date: date, end_date: date):
        runtime_data = db.query(EquipmentRuntime, Equipment).join(
            Equipment, Equipment.id == EquipmentRuntime.equipment_id
        ).filter(
            EquipmentRuntime.record_date >= start_date,
            EquipmentRuntime.record_date <= end_date
        ).order_by(EquipmentRuntime.record_date).all()
        
        daily_stats = {}
        total_planned = 0
        total_actual = 0
        total_downtime = 0
        
        for runtime, equipment in runtime_data:
            day_key = runtime.record_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "planned": 0,
                    "actual": 0,
                    "downtime": 0,
                    "equipment": equipment.equipment_name
                }
            daily_stats[day_key]["planned"] += runtime.planned_runtime
            daily_stats[day_key]["actual"] += runtime.actual_runtime
            daily_stats[day_key]["downtime"] += runtime.downtime
            total_planned += runtime.planned_runtime
            total_actual += runtime.actual_runtime
            total_downtime += runtime.downtime
        
        avg_operating_rate = 0.0
        if total_planned > 0:
            avg_operating_rate = round((total_actual / total_planned) * 100, 2)
        
        trend_data = []
        for day, stats in daily_stats.items():
            rate = 0.0
            if stats["planned"] > 0:
                rate = round((stats["actual"] / stats["planned"]) * 100, 2)
            
            trend_data.append({
                "date": day,
                "equipment_name": stats["equipment"],
                "operating_rate": rate,
                "actual_runtime": stats["actual"],
                "downtime": stats["downtime"]
            })
        
        trend_data.sort(key=lambda x: x["date"])
        
        return {
            "period": f"{start_date} 至 {end_date}",
            "avg_operating_rate": avg_operating_rate,
            "total_downtime": total_downtime,
            "data": trend_data
        }

    @staticmethod
    def get_maintenance_rate_by_date_range(db: Session, start_date: date, end_date: date):
        maintenance = db.query(EquipmentMaintenance).filter(
            EquipmentMaintenance.plan_date >= start_date,
            EquipmentMaintenance.plan_date <= end_date
        ).order_by(EquipmentMaintenance.plan_date).all()
        
        daily_stats = {}
        total_planned = 0
        total_completed = 0
        
        for m in maintenance:
            day_key = m.plan_date.isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "planned": 0,
                    "completed": 0
                }
            daily_stats[day_key]["planned"] += 1
            total_planned += 1
            if m.is_completed:
                daily_stats[day_key]["completed"] += 1
                total_completed += 1
        
        avg_completion_rate = 0.0
        if total_planned > 0:
            avg_completion_rate = round((total_completed / total_planned) * 100, 2)
        
        trend_data = []
        for day, stats in daily_stats.items():
            rate = 0.0
            if stats["planned"] > 0:
                rate = round((stats["completed"] / stats["planned"]) * 100, 2)
            
            trend_data.append({
                "date": day,
                "planned_count": stats["planned"],
                "completed_count": stats["completed"],
                "completion_rate": rate
            })
        
        trend_data.sort(key=lambda x: x["date"])
        
        return {
            "period": f"{start_date} 至 {end_date}",
            "total_planned": total_planned,
            "total_completed": total_completed,
            "avg_completion_rate": avg_completion_rate,
            "data": trend_data
        }
