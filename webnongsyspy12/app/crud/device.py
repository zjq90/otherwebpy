from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Device
from app.schemas import DeviceCreate, DeviceUpdate


class DeviceCRUD:
    """
    设备CRUD操作类
    封装设备相关的数据库操作
    """

    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Optional[Device]:
        """
        根据ID获取设备信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            设备对象或None
        """
        return db.query(Device).filter(Device.id == device_id).first()

    @staticmethod
    def get_by_code(db: Session, device_code: str) -> Optional[Device]:
        """
        根据设备编号获取设备信息
        
        Args:
            db: 数据库会话
            device_code: 设备编号
            
        Returns:
            设备对象或None
        """
        return db.query(Device).filter(Device.device_code == device_code).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        device_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple:
        """
        获取设备列表（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过条数
            limit: 获取条数
            device_type: 设备类型筛选
            status: 设备状态筛选
            
        Returns:
            tuple: (总数, 设备列表)
        """
        query = db.query(Device)
        
        # 添加筛选条件
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if status:
            query = query.filter(Device.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        devices = query.order_by(desc(Device.created_at)).offset(skip).limit(limit).all()
        
        return total, devices

    @staticmethod
    def create(db: Session, device_in: DeviceCreate) -> Device:
        """
        创建设备
        
        Args:
            db: 数据库会话
            device_in: 设备创建数据
            
        Returns:
            创建的设备对象
        """
        db_device = Device(
            device_code=device_in.device_code,
            device_name=device_in.device_name,
            device_type=device_in.device_type,
            location=device_in.location,
            status=device_in.status or "online",
            description=device_in.description
        )
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    @staticmethod
    def update(db: Session, device: Device, device_in: DeviceUpdate) -> Device:
        """
        更新设备信息
        
        Args:
            db: 数据库会话
            device: 原设备对象
            device_in: 更新数据
            
        Returns:
            更新后的设备对象
        """
        update_data = device_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(device, key, value)
        
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def delete(db: Session, device: Device) -> Device:
        """
        删除设备
        
        Args:
            db: 数据库会话
            device: 设备对象
            
        Returns:
            被删除的设备对象
        """
        db.delete(device)
        db.commit()
        return device
