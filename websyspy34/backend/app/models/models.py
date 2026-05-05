from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class FormulaStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class ProductionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class ResourceType(str, enum.Enum):
    MIXER_TRUCK = "mixer_truck"
    FORKLIFT = "forklift"
    PUMP = "pump"
    OTHER = "other"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class AlertLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class ProductionStage(str, enum.Enum):
    BATCHING = "batching"
    MIXING = "mixing"
    DISCHARGING = "discharging"
    COMPLETED = "completed"


class Formula(Base):
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True)
    formula_code = Column(String(50), unique=True, index=True, nullable=False)
    formula_name = Column(String(100), nullable=False)
    concrete_type = Column(String(50), nullable=False)
    strength_grade = Column(String(20))
    description = Column(Text)
    
    cement = Column(Float, default=0.0)
    sand = Column(Float, default=0.0)
    gravel = Column(Float, default=0.0)
    water = Column(Float, default=0.0)
    admixture = Column(Float, default=0.0)
    fly_ash = Column(Float, default=0.0)
    mineral_powder = Column(Float, default=0.0)
    
    water_cement_ratio = Column(Float)
    slump = Column(Float)
    
    status = Column(SQLEnum(FormulaStatus), default=FormulaStatus.ACTIVE)
    is_standard = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50))
    updated_by = Column(String(50))
    
    adjustments = relationship("FormulaAdjustment", back_populates="formula")
    production_orders = relationship("ProductionOrder", back_populates="formula")


class FormulaAdjustment(Base):
    __tablename__ = "formula_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    formula_id = Column(Integer, ForeignKey("formulas.id"), nullable=False)
    
    original_cement = Column(Float)
    adjusted_cement = Column(Float)
    original_sand = Column(Float)
    adjusted_sand = Column(Float)
    original_gravel = Column(Float)
    adjusted_gravel = Column(Float)
    original_water = Column(Float)
    adjusted_water = Column(Float)
    original_admixture = Column(Float)
    adjusted_admixture = Column(Float)
    original_fly_ash = Column(Float)
    adjusted_fly_ash = Column(Float)
    original_mineral_powder = Column(Float)
    adjusted_mineral_powder = Column(Float)
    
    adjustment_reason = Column(Text)
    project_name = Column(String(100))
    project_requirements = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    adjusted_by = Column(String(50))
    
    formula = relationship("Formula", back_populates="adjustments")


class ProductionPlan(Base):
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_code = Column(String(50), unique=True, index=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    
    project_name = Column(String(100))
    project_location = Column(String(200))
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    
    total_volume = Column(Float, default=0.0)
    completed_volume = Column(Float, default=0.0)
    
    status = Column(SQLEnum(ProductionStatus), default=ProductionStatus.PENDING)
    priority = Column(Integer, default=1)
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50))
    
    orders = relationship("ProductionOrder", back_populates="plan")
    resource_allocations = relationship("ResourceAllocation", back_populates="plan")


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(50), unique=True, index=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("production_plans.id"), nullable=True)
    formula_id = Column(Integer, ForeignKey("formulas.id"), nullable=False)
    
    batch_number = Column(String(50))
    volume = Column(Float, nullable=False)
    unit = Column(String(10), default="m³")
    
    pouring_location = Column(String(200))
    pouring_method = Column(String(50))
    
    scheduled_time = Column(DateTime)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    status = Column(SQLEnum(ProductionStatus), default=ProductionStatus.PENDING)
    current_stage = Column(SQLEnum(ProductionStage), default=ProductionStage.BATCHING)
    
    progress = Column(Float, default=0.0)
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plan = relationship("ProductionPlan", back_populates="orders")
    formula = relationship("Formula", back_populates="production_orders")
    resource_allocations = relationship("ResourceAllocation", back_populates="order")
    production_logs = relationship("ProductionLog", back_populates="order")
    production_alerts = relationship("ProductionAlert", back_populates="order")
    status_history = relationship("ProductionStatusHistory", back_populates="order")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_code = Column(String(50), unique=True, index=True, nullable=False)
    resource_name = Column(String(100), nullable=False)
    
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    
    model = Column(String(100))
    capacity = Column(Float)
    capacity_unit = Column(String(20), default="m³")
    
    license_plate = Column(String(20))
    manufacture_year = Column(Integer)
    
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.AVAILABLE)
    
    current_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    allocations = relationship("ResourceAllocation", back_populates="resource")


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("production_plans.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    
    allocation_start_time = Column(DateTime)
    allocation_end_time = Column(DateTime)
    
    allocated_by = Column(String(50))
    allocation_reason = Column(Text)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resource = relationship("Resource", back_populates="allocations")
    plan = relationship("ProductionPlan", back_populates="resource_allocations")
    order = relationship("ProductionOrder", back_populates="resource_allocations")


class ProductionLog(Base):
    __tablename__ = "production_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    
    stage = Column(SQLEnum(ProductionStage))
    
    batch_weight_cement = Column(Float)
    batch_weight_sand = Column(Float)
    batch_weight_gravel = Column(Float)
    batch_weight_water = Column(Float)
    batch_weight_admixture = Column(Float)
    batch_weight_fly_ash = Column(Float)
    batch_weight_mineral_powder = Column(Float)
    
    mixing_time = Column(Integer)
    mixing_speed = Column(Float)
    
    discharge_volume = Column(Float)
    discharge_duration = Column(Integer)
    
    temperature = Column(Float)
    humidity = Column(Float)
    
    log_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("ProductionOrder", back_populates="production_logs")


class ProductionAlert(Base):
    __tablename__ = "production_alerts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    
    alert_code = Column(String(50))
    alert_title = Column(String(200), nullable=False)
    alert_message = Column(Text)
    
    alert_level = Column(SQLEnum(AlertLevel), default=AlertLevel.WARNING)
    alert_status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN)
    
    related_stage = Column(SQLEnum(ProductionStage))
    
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(50))
    resolved_at = Column(DateTime)
    resolved_by = Column(String(50))
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("ProductionOrder", back_populates="production_alerts")


class ProductionStatusHistory(Base):
    __tablename__ = "production_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    
    previous_status = Column(SQLEnum(ProductionStatus))
    new_status = Column(SQLEnum(ProductionStatus))
    
    previous_stage = Column(SQLEnum(ProductionStage))
    new_stage = Column(SQLEnum(ProductionStage))
    
    changed_by = Column(String(50))
    change_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("ProductionOrder", back_populates="status_history")
