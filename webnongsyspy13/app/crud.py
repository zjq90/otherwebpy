"""
CRUD操作模块
封装所有数据库的增删改查操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Type, Any, Dict
from datetime import datetime, timedelta
from app import models, schemas
from app.config import settings


class CRUDBase:
    """
    基础CRUD类
    提供通用的增删改查操作
    """
    
    def __init__(self, model: Type[Any]):
        """
        初始化CRUD类
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[Any]:
        """
        根据ID获取单个记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            记录对象或None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Any]:
        """
        获取多个记录（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            记录列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def get_count(self, db: Session) -> int:
        """
        获取记录总数
        
        Args:
            db: 数据库会话
            
        Returns:
            记录总数
        """
        return db.query(func.count(self.model.id)).scalar()
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> Any:
        """
        创建新记录
        
        Args:
            db: 数据库会话
            obj_in: 创建数据字典
            
        Returns:
            创建的记录对象
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        db_obj: Any, 
        obj_in: Dict[str, Any]
    ) -> Any:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 数据库中已存在的记录对象
            obj_in: 更新数据字典
            
        Returns:
            更新后的记录对象
        """
        for key, value in obj_in.items():
            if value is not None:
                setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, id: int) -> Any:
        """
        删除记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            被删除的记录对象
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        db.delete(obj)
        db.commit()
        return obj


class CRUDProduct(CRUDBase):
    """产品CRUD类"""
    
    def get_by_name(self, db: Session, name: str) -> Optional[models.Product]:
        """根据名称获取产品"""
        return db.query(self.model).filter(self.model.name == name).first()
    
    def search(
        self, 
        db: Session, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Product]:
        """搜索产品"""
        return db.query(self.model).filter(
            self.model.name.contains(keyword) |
            self.model.category.contains(keyword) |
            self.model.origin.contains(keyword)
        ).offset(skip).limit(limit).all()


class CRUDBatch(CRUDBase):
    """批次CRUD类"""
    
    def get_by_batch_number(self, db: Session, batch_number: str) -> Optional[models.Batch]:
        """根据批次编号获取批次（包含关联的产品信息）"""
        from sqlalchemy.orm import joinedload
        
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(self.model.batch_number == batch_number).first()
    
    def get_by_product_id(
        self, 
        db: Session, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Batch]:
        """根据产品ID获取批次列表（包含关联的产品信息）"""
        from sqlalchemy.orm import joinedload
        
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(
            self.model.product_id == product_id
        ).offset(skip).limit(limit).all()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Batch]:
        """
        获取多个批次（分页，包含关联的产品信息）
        重写父类方法，确保加载product关联数据
        """
        from sqlalchemy.orm import joinedload
        
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).offset(skip).limit(limit).all()
    
    def get(self, db: Session, id: int) -> Optional[models.Batch]:
        """
        根据ID获取单个批次（包含关联的产品信息）
        重写父类方法，确保加载product关联数据
        """
        from sqlalchemy.orm import joinedload
        
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(self.model.id == id).first()
    
    def get_with_details(self, db: Session, id: int) -> Optional[models.Batch]:
        """获取批次详情（包含所有关联数据）"""
        from sqlalchemy.orm import joinedload
        
        return db.query(self.model).options(
            joinedload(self.model.product),
            joinedload(self.model.planting_records),
            joinedload(self.model.agrochemical_usages),
            joinedload(self.model.test_results)
        ).filter(self.model.id == id).first()


class CRUDPlantingRecord(CRUDBase):
    """种植记录CRUD类"""
    
    def get_by_batch_id(
        self, 
        db: Session, 
        batch_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.PlantingRecord]:
        """根据批次ID获取种植记录"""
        return db.query(self.model).filter(
            self.model.batch_id == batch_id
        ).order_by(self.model.record_date.desc()).offset(skip).limit(limit).all()


class CRUDAgrochemicalUsage(CRUDBase):
    """农资使用记录CRUD类"""
    
    def get_by_batch_id(
        self, 
        db: Session, 
        batch_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.AgrochemicalUsage]:
        """根据批次ID获取农资使用记录"""
        return db.query(self.model).filter(
            self.model.batch_id == batch_id
        ).order_by(self.model.usage_date.desc()).offset(skip).limit(limit).all()


class CRUDTestResult(CRUDBase):
    """检测结果CRUD类"""
    
    def get_by_batch_id(
        self, 
        db: Session, 
        batch_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.TestResult]:
        """根据批次ID获取检测结果"""
        return db.query(self.model).filter(
            self.model.batch_id == batch_id
        ).order_by(self.model.test_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_type(
        self, 
        db: Session, 
        test_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.TestResult]:
        """根据检测类型获取检测结果"""
        return db.query(self.model).filter(
            self.model.test_type == test_type
        ).order_by(self.model.test_date.desc()).offset(skip).limit(limit).all()


class CRUDCertificate(CRUDBase):
    """认证证书CRUD类"""
    
    def get_by_certificate_number(
        self, 
        db: Session, 
        certificate_number: str
    ) -> Optional[models.Certificate]:
        """根据证书编号获取证书"""
        return db.query(self.model).filter(
            self.model.certificate_number == certificate_number
        ).first()
    
    def get_by_type(
        self, 
        db: Session, 
        certificate_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Certificate]:
        """根据认证类型获取证书列表"""
        return db.query(self.model).filter(
            self.model.certificate_type == certificate_type
        ).offset(skip).limit(limit).all()
    
    def get_expiring_soon(
        self, 
        db: Session, 
        days: int = None
    ) -> List[models.Certificate]:
        """
        获取即将过期的证书
        
        Args:
            db: 数据库会话
            days: 提前提醒天数，默认使用配置中的CERTIFICATE_REMINDER_DAYS
            
        Returns:
            即将过期的证书列表
        """
        if days is None:
            days = settings.CERTIFICATE_REMINDER_DAYS
        
        today = datetime.now().date()
        reminder_date = today + timedelta(days=days)
        
        return db.query(self.model).filter(
            and_(
                self.model.valid_until <= reminder_date,
                self.model.valid_until >= today,
                self.model.status != "过期"
            )
        ).all()
    
    def get_expired(self, db: Session) -> List[models.Certificate]:
        """获取已过期的证书"""
        today = datetime.now().date()
        
        return db.query(self.model).filter(
            self.model.valid_until < today
        ).all()
    
    def update_certificate_status(self, db: Session) -> int:
        """
        更新所有证书的状态
        
        Args:
            db: 数据库会话
            
        Returns:
            更新的证书数量
        """
        today = datetime.now().date()
        reminder_days = settings.CERTIFICATE_REMINDER_DAYS
        reminder_date = today + timedelta(days=reminder_days)
        
        count = 0
        
        # 更新已过期的证书
        expired_certs = db.query(self.model).filter(
            and_(
                self.model.valid_until < today,
                self.model.status != "过期"
            )
        ).all()
        
        for cert in expired_certs:
            cert.status = "过期"
            count += 1
        
        # 更新即将过期的证书
        expiring_certs = db.query(self.model).filter(
            and_(
                self.model.valid_until <= reminder_date,
                self.model.valid_until >= today,
                self.model.status == "有效"
            )
        ).all()
        
        for cert in expiring_certs:
            cert.status = "即将过期"
            count += 1
        
        db.commit()
        return count


# 实例化各CRUD类
product = CRUDProduct(models.Product)
batch = CRUDBatch(models.Batch)
planting_record = CRUDPlantingRecord(models.PlantingRecord)
agrochemical_usage = CRUDAgrochemicalUsage(models.AgrochemicalUsage)
test_result = CRUDTestResult(models.TestResult)
certificate = CRUDCertificate(models.Certificate)
