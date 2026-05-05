from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class QualityData(Base):
    __tablename__ = "quality_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inspection_date = Column(Date, nullable=False, index=True)
    inspection_type = Column(String(50), nullable=False)
    material_name = Column(String(100), nullable=False)
    batch_no = Column(String(50))
    supplier = Column(String(100))
    total_samples = Column(Integer, default=0)
    passed_samples = Column(Integer, default=0)
    failed_samples = Column(Integer, default=0)
    inspector = Column(String(50))
    inspection_result = Column(String(20))
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @property
    def pass_rate(self):
        if self.total_samples > 0:
            return round((self.passed_samples / self.total_samples) * 100, 2)
        return 0.0

class ProductStrength(Base):
    __tablename__ = "product_strength"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_date = Column(Date, nullable=False, index=True)
    product_name = Column(String(100), nullable=False)
    batch_no = Column(String(50))
    strength_standard = Column(Float, default=0.0)
    strength_actual = Column(Float, default=0.0)
    test_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    tester = Column(String(50))
    is_qualified = Column(String(10), default="合格")
    remarks = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @property
    def pass_rate(self):
        if self.test_count > 0:
            return round((self.pass_count / self.test_count) * 100, 2)
        return 0.0
