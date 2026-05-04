"""
工程维保管理模块 - CRUD操作
包含设备台账、巡检计划、保养计划、故障维修记录等CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.equipment import (
    Equipment, InspectionPlan, InspectionRecord,
    MaintenancePlan, MaintenanceRecord, FaultRecord
)
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate,
    InspectionPlanCreate, InspectionPlanUpdate,
    InspectionRecordCreate,
    MaintenancePlanCreate, MaintenancePlanUpdate,
    MaintenanceRecordCreate,
    FaultRecordCreate, FaultRecordUpdate
)

# ==================== 设备台账 CRUD ====================

class CRUDEquipment(CRUDBase[Equipment, EquipmentCreate, EquipmentUpdate]):
    """
    设备台账CRUD类
    继承CRUDBase，实现设备台账的特殊查询操作
    """

    def get_by_code(self, db: Session, code: str) -> Optional[Equipment]:
        """
        根据设备编号获取设备
        
        Args:
            db: 数据库会话
            code: 设备编号
            
        Returns:
            Optional[Equipment]: 找到的设备
        """
        return db.query(self.model).filter(self.model.code == code).first()

    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Equipment]:
        """
        根据设备类别获取设备列表
        
        Args:
            db: 数据库会话
            category: 设备类别
            skip: 跳过记录数
            limit: 返回最大记录数
            
        Returns:
            List[Equipment]: 设备列表
        """
        return db.query(self.model).filter(self.model.category == category).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Equipment]:
        """
        根据设备状态获取设备列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def search(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> List[Equipment]:
        """
        搜索设备（按名称或编号模糊查询）
        """
        return db.query(self.model).filter(
            (self.model.name.like(f"%{keyword}%")) |
            (self.model.code.like(f"%{keyword}%"))
        ).offset(skip).limit(limit).all()

    def get_status_statistics(self, db: Session):
        """
        获取设备状态统计
        """
        result = db.query(
            self.model.status,
            func.count(self.model.id).label('count')
        ).group_by(self.model.status).all()
        return [{"status": r.status, "count": r.count} for r in result]

# ==================== 巡检计划 CRUD ====================

class CRUDInspectionPlan(CRUDBase[InspectionPlan, InspectionPlanCreate, InspectionPlanUpdate]):
    """
    巡检计划CRUD类
    """

    def get_by_equipment(self, db: Session, equipment_id: int, skip: int = 0, limit: int = 100) -> List[InspectionPlan]:
        """
        根据设备ID获取巡检计划列表
        """
        return db.query(self.model).filter(self.model.equipment_id == equipment_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[InspectionPlan]:
        """
        根据状态获取巡检计划列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

# ==================== 巡检记录 CRUD ====================

class CRUDInspectionRecord(CRUDBase[InspectionRecord, InspectionRecordCreate, InspectionRecordCreate]):
    """
    巡检记录CRUD类
    """

    def get_by_plan(self, db: Session, plan_id: int, skip: int = 0, limit: int = 100) -> List[InspectionRecord]:
        """
        根据巡检计划ID获取记录列表
        """
        return db.query(InspectionRecord).filter(InspectionRecord.plan_id == plan_id).offset(skip).limit(limit).all()

# ==================== 保养计划 CRUD ====================

class CRUDMaintenancePlan(CRUDBase[MaintenancePlan, MaintenancePlanCreate, MaintenancePlanUpdate]):
    """
    保养计划CRUD类
    """

    def get_by_equipment(self, db: Session, equipment_id: int, skip: int = 0, limit: int = 100) -> List[MaintenancePlan]:
        """
        根据设备ID获取保养计划列表
        """
        return db.query(self.model).filter(self.model.equipment_id == equipment_id).offset(skip).limit(limit).all()

# ==================== 保养记录 CRUD ====================

class CRUDMaintenanceRecord(CRUDBase[MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordCreate]):
    """
    保养记录CRUD类
    """

    def get_by_plan(self, db: Session, plan_id: int, skip: int = 0, limit: int = 100) -> List[MaintenanceRecord]:
        """
        根据保养计划ID获取记录列表
        """
        return db.query(MaintenanceRecord).filter(MaintenanceRecord.plan_id == plan_id).offset(skip).limit(limit).all()

# ==================== 故障维修记录 CRUD ====================

class CRUDFaultRecord(CRUDBase[FaultRecord, FaultRecordCreate, FaultRecordUpdate]):
    """
    故障维修记录CRUD类
    """

    def get_by_equipment(self, db: Session, equipment_id: int, skip: int = 0, limit: int = 100) -> List[FaultRecord]:
        """
        根据设备ID获取故障记录列表
        """
        return db.query(self.model).filter(self.model.equipment_id == equipment_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[FaultRecord]:
        """
        根据状态获取故障记录列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def get_cost_statistics(self, db: Session):
        """
        获取费用统计
        """
        total_fault_cost = db.query(func.sum(FaultRecord.total_cost)).filter(
            FaultRecord.status == "已完成"
        ).scalar() or 0
        
        total_maintenance_cost = db.query(func.sum(MaintenanceRecord.actual_cost)).scalar() or 0
        
        fault_count = db.query(func.count(FaultRecord.id)).filter(
            FaultRecord.status == "已完成"
        ).scalar() or 0
        
        maintenance_count = db.query(func.count(MaintenanceRecord.id)).scalar() or 0
        
        return {
            "total_fault_cost": float(total_fault_cost),
            "total_maintenance_cost": float(total_maintenance_cost),
            "fault_count": fault_count,
            "maintenance_count": maintenance_count,
            "avg_fault_cost": float(total_fault_cost) / fault_count if fault_count > 0 else 0,
            "avg_maintenance_cost": float(total_maintenance_cost) / maintenance_count if maintenance_count > 0 else 0
        }

    def get_fault_type_statistics(self, db: Session):
        """
        获取故障类型统计
        """
        result = db.query(
            FaultRecord.fault_type,
            func.count(FaultRecord.id).label('count'),
            func.sum(FaultRecord.total_cost).label('total_cost')
        ).group_by(FaultRecord.fault_type).all()
        return [
            {
                "fault_type": r.fault_type,
                "count": r.count,
                "total_cost": float(r.total_cost) if r.total_cost else 0
            } for r in result
        ]

# 实例化CRUD对象
equipment = CRUDEquipment(Equipment)
inspection_plan = CRUDInspectionPlan(InspectionPlan)
inspection_record = CRUDInspectionRecord(InspectionRecord)
maintenance_plan = CRUDMaintenancePlan(MaintenancePlan)
maintenance_record = CRUDMaintenanceRecord(MaintenanceRecord)
fault_record = CRUDFaultRecord(FaultRecord)
