from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Crop
from ..schemas import CropCreate, CropUpdate


class CropCRUD:
    """
    作物档案CRUD操作类
    提供作物信息的增删改查功能
    """
    
    def get_by_id(self, db: Session, crop_id: int) -> Optional[Crop]:
        """
        根据ID获取作物信息
        :param db: 数据库会话
        :param crop_id: 作物ID
        :return: 作物对象或None
        """
        return db.query(Crop).filter(Crop.id == crop_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Crop]:
        """
        获取所有作物信息（分页）
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :return: 作物列表
        """
        return db.query(Crop).offset(skip).limit(limit).all()
    
    def get_by_name(self, db: Session, name: str) -> List[Crop]:
        """
        根据名称获取作物信息
        :param db: 数据库会话
        :param name: 作物名称
        :return: 作物列表
        """
        return db.query(Crop).filter(Crop.name == name).all()
    
    def get_by_name_and_variety(self, db: Session, name: str, variety: str) -> Optional[Crop]:
        """
        根据名称和品种获取作物信息
        :param db: 数据库会话
        :param name: 作物名称
        :param variety: 品种
        :return: 作物对象或None
        """
        return db.query(Crop).filter(Crop.name == name, Crop.variety == variety).first()
    
    def create(self, db: Session, crop: CropCreate) -> Crop:
        """
        创建新作物
        :param db: 数据库会话
        :param crop: 作物创建数据
        :return: 创建的作物对象
        """
        db_crop = Crop(**crop.model_dump())
        db.add(db_crop)
        db.commit()
        db.refresh(db_crop)
        return db_crop
    
    def update(self, db: Session, crop_id: int, crop: CropUpdate) -> Optional[Crop]:
        """
        更新作物信息
        :param db: 数据库会话
        :param crop_id: 作物ID
        :param crop: 作物更新数据
        :return: 更新后的作物对象或None
        """
        db_crop = self.get_by_id(db, crop_id)
        if db_crop:
            # 只更新提供的字段
            for key, value in crop.model_dump(exclude_unset=True).items():
                setattr(db_crop, key, value)
            db.commit()
            db.refresh(db_crop)
        return db_crop
    
    def delete(self, db: Session, crop_id: int) -> bool:
        """
        删除作物
        :param db: 数据库会话
        :param crop_id: 作物ID
        :return: 是否成功删除
        """
        db_crop = self.get_by_id(db, crop_id)
        if db_crop:
            db.delete(db_crop)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """
        统计作物数量
        :param db: 数据库会话
        :return: 作物总数
        """
        return db.query(Crop).count()


# 全局实例
crop_crud = CropCRUD()
