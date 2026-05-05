# 数据模型包
from .user_models import User, Role, Permission, VerificationCode, user_role, role_permission
from .business_models import (
    ProductionTask, ProductionRecord,
    MaterialInspection, QualityReport, QualityAlert,
    MaterialInventory, PurchaseRequest, Supplier,
    Vehicle, TransportTask
)

# 导出所有模型供数据库初始化使用
__all__ = [
    'User', 'Role', 'Permission', 'VerificationCode', 'user_role', 'role_permission',
    'ProductionTask', 'ProductionRecord',
    'MaterialInspection', 'QualityReport', 'QualityAlert',
    'MaterialInventory', 'PurchaseRequest', 'Supplier',
    'Vehicle', 'TransportTask'
]
