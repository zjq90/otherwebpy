from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_no = Column(String(50), unique=True, nullable=False, index=True)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50))
    model = Column(String(50))
    location = Column(String(100))
    purchase_date = Column(Date)
    status = Column(String(20), default="正常")
    responsible_person = Column(String(50))
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EquipmentRuntime(Base):
    __tablename__ = "equipment_runtime"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    planned_runtime = Column(Float, default=24.0)
    actual_runtime = Column(Float, default=0.0)
    downtime = Column(Float, default=0.0)
    standby_time = Column(Float, default=0.0)
    operator = Column(String(50))
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @property
    def operating_rate(self):
        if self.planned_runtime > 0:
            return round((self.actual_runtime / self.planned_runtime) * 100, 2)
        return 0.0

class EquipmentFault(Base):
    __tablename__ = "equipment_fault"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False, index=True)
    fault_date = Column(Date, nullable=False, index=True)
    fault_type = Column(String(50))
    fault_description = Column(String(500))
    fault_level = Column(String(20), default="一般")
    downtime_duration = Column(Float, default=0.0)
    repair_person = Column(String(50))
    repair_cost = Column(Float, default=0.0)
    status = Column(String(20), default="已修复")
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EquipmentMaintenance(Base):
    __tablename__ = "equipment_maintenance"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False, index=True)
    plan_date = Column(Date, nullable=False, index=True)
    actual_date = Column(Date)
    maintenance_type = Column(String(50))
    maintenance_content = Column(String(500))
    maintenance_person = Column(String(50))
    status = Column(String(20), default="待执行")
    is_completed = Column(Integer, default=0)
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
