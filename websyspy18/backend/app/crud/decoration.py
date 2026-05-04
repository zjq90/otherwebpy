"""
装修管理模块 - CRUD操作
包含装修申请、押金管理、巡检记录等CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.decoration import (
    DecorationApplication, DecorationDeposit, DecorationInspection
)
from app.schemas.decoration import (
    DecorationApplicationCreate, DecorationApplicationUpdate,
    DecorationDepositCreate, DecorationDepositUpdate,
    DecorationInspectionCreate, DecorationInspectionUpdate
)

# ==================== 装修申请 CRUD ====================

class CRUDDecorationApplication(CRUDBase[DecorationApplication, DecorationApplicationCreate, DecorationApplicationUpdate]):
    """
    装修申请CRUD类
    """

    def get_by_application_no(self, db: Session, application_no: str) -> Optional[DecorationApplication]:
        """
        根据申请编号获取装修申请
        """
        return db.query(self.model).filter(self.model.application_no == application_no).first()

    def get_by_room(self, db: Session, room_number: str, skip: int = 0, limit: int = 100) -> List[DecorationApplication]:
        """
        根据房间号获取装修申请列表
        """
        return db.query(self.model).filter(self.model.room_number == room_number).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[DecorationApplication]:
        """
        根据状态获取装修申请列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def search(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> List[DecorationApplication]:
        """
        搜索装修申请（按房间号、业主姓名、申请编号）
        """
        return db.query(self.model).filter(
            (self.model.room_number.like(f"%{keyword}%")) |
            (self.model.owner_name.like(f"%{keyword}%")) |
            (self.model.application_no.like(f"%{keyword}%"))
        ).offset(skip).limit(limit).all()

# ==================== 装修押金 CRUD ====================

class CRUDDecorationDeposit(CRUDBase[DecorationDeposit, DecorationDepositCreate, DecorationDepositUpdate]):
    """
    装修押金CRUD类
    """

    def get_by_application(self, db: Session, application_id: int, skip: int = 0, limit: int = 100) -> List[DecorationDeposit]:
        """
        根据装修申请ID获取押金记录列表
        """
        return db.query(self.model).filter(self.model.application_id == application_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[DecorationDeposit]:
        """
        根据状态获取押金记录列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

# ==================== 装修巡检 CRUD ====================

class CRUDDecorationInspection(CRUDBase[DecorationInspection, DecorationInspectionCreate, DecorationInspectionUpdate]):
    """
    装修巡检CRUD类
    """

    def get_by_application(self, db: Session, application_id: int, skip: int = 0, limit: int = 100) -> List[DecorationInspection]:
        """
        根据装修申请ID获取巡检记录列表
        """
        return db.query(self.model).filter(self.model.application_id == application_id).offset(skip).limit(limit).all()

    def get_unrectified(self, db: Session, skip: int = 0, limit: int = 100) -> List[DecorationInspection]:
        """
        获取未整改的巡检记录
        """
        return db.query(self.model).filter(
            self.model.is_rectified == False,
            self.model.result == "异常"
        ).offset(skip).limit(limit).all()

# 实例化CRUD对象
decoration_application = CRUDDecorationApplication(DecorationApplication)
decoration_deposit = CRUDDecorationDeposit(DecorationDeposit)
decoration_inspection = CRUDDecorationInspection(DecorationInspection)
