from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class ProductionData(Base):
    __tablename__ = "production_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    production_date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=False)
    product_name = Column(String(100), nullable=False)
    planned_quantity = Column(Integer, default=0)
    actual_quantity = Column(Integer, default=0)
    qualified_quantity = Column(Integer, default=0)
    work_hours = Column(Float, default=0.0)
    operator = Column(String(50))
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @property
    def completion_rate(self):
        if self.planned_quantity > 0:
            return round((self.actual_quantity / self.planned_quantity) * 100, 2)
        return 0.0
    
    @property
    def pass_rate(self):
        if self.actual_quantity > 0:
            return round((self.qualified_quantity / self.actual_quantity) * 100, 2)
        return 0.0
    
    @property
    def efficiency(self):
        if self.work_hours > 0:
            return round(self.actual_quantity / self.work_hours, 2)
        return 0.0

class ProductionTask(Base):
    __tablename__ = "production_tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_no = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(100), nullable=False)
    planned_quantity = Column(Integer, default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    priority = Column(Integer, default=1)
    status = Column(String(20), default="pending")
    assigned_to = Column(String(50))
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
