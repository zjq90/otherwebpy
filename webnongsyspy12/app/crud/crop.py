from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Crop
from app.schemas import CropCreate, CropUpdate


class CropCRUD:
    """
    作物CRUD操作类
    封装作物相关的数据库操作
    """

    @staticmethod
    def get_by_id(db: Session, crop_id: int) -> Optional[Crop]:
        """
        根据ID获取作物信息
        
        Args:
            db: 数据库会话
            crop_id: 作物ID
            
        Returns:
            作物对象或None
        """
        return db.query(Crop).filter(Crop.id == crop_id).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        crop_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple:
        """
        获取作物列表（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过条数
            limit: 获取条数
            crop_type: 作物类型筛选
            status: 作物状态筛选
            
        Returns:
            tuple: (总数, 作物列表)
        """
        query = db.query(Crop)
        
        # 添加筛选条件
        if crop_type:
            query = query.filter(Crop.crop_type == crop_type)
        if status:
            query = query.filter(Crop.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        crops = query.order_by(desc(Crop.created_at)).offset(skip).limit(limit).all()
        
        return total, crops

    @staticmethod
    def create(db: Session, crop_in: CropCreate) -> Crop:
        """
        创建作物
        
        Args:
            db: 数据库会话
            crop_in: 作物创建数据
            
        Returns:
            创建的作物对象
        """
        db_crop = Crop(
            crop_name=crop_in.crop_name,
            crop_type=crop_in.crop_type,
            variety=crop_in.variety,
            planting_date=crop_in.planting_date,
            expected_harvest_date=crop_in.expected_harvest_date,
            location=crop_in.location,
            status=crop_in.status or "growing",
            notes=crop_in.notes
        )
        db.add(db_crop)
        db.commit()
        db.refresh(db_crop)
        return db_crop

    @staticmethod
    def update(db: Session, crop: Crop, crop_in: CropUpdate) -> Crop:
        """
        更新作物信息
        
        Args:
            db: 数据库会话
            crop: 原作物对象
            crop_in: 更新数据
            
        Returns:
            更新后的作物对象
        """
        update_data = crop_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(crop, key, value)
        
        db.commit()
        db.refresh(crop)
        return crop

    @staticmethod
    def delete(db: Session, crop: Crop) -> Crop:
        """
        删除作物
        
        Args:
            db: 数据库会话
            crop: 作物对象
            
        Returns:
            被删除的作物对象
        """
        db.delete(crop)
        db.commit()
        return crop

    @staticmethod
    def get_statistics(db: Session) -> dict:
        """
        获取作物统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计结果字典
        """
        from sqlalchemy import func
        
        # 统计各状态的作物数量
        status_stats = db.query(
            Crop.status,
            func.count(Crop.id).label('count')
        ).group_by(Crop.status).all()
        
        # 统计各类型的作物数量
        type_stats = db.query(
            Crop.crop_type,
            func.count(Crop.id).label('count')
        ).filter(Crop.crop_type.isnot(None)).group_by(Crop.crop_type).all()
        
        return {
            'total': db.query(Crop).count(),
            'by_status': {s.status: s.count for s in status_stats},
            'by_type': {s.crop_type: s.count for s in type_stats}
        }
