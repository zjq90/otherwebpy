"""
数据模型包
包含所有数据库表的ORM模型定义
"""
from app.models.equipment import (
    Equipment, InspectionPlan, InspectionRecord,
    MaintenancePlan, MaintenanceRecord, FaultRecord
)
from app.models.decoration import (
    DecorationApplication, DecorationDeposit, DecorationInspection
)
from app.models.contract import (
    Supplier, Contract, ContractPayment, ServiceEvaluation
)

__all__ = [
    "Equipment", "InspectionPlan", "InspectionRecord",
    "MaintenancePlan", "MaintenanceRecord", "FaultRecord",
    "DecorationApplication", "DecorationDeposit", "DecorationInspection",
    "Supplier", "Contract", "ContractPayment", "ServiceEvaluation"
]
