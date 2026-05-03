from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Farm
from ..schemas import FarmCreate, FarmUpdate


class FarmCRUD:
    """
    农场信息CRUD操作类
    提供农场信息的增删改查功能
    """
    
    def get_by_id(self, db: Session, farm_id: int) -> Optional[Farm]:
        """
        根据ID获取农场信息
        :param db: 数据库会话
        :param farm_id: 农场ID
        :return: 农场对象或None
        """
        return db.query(Farm).filter(Farm.id == farm_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Farm]:
        """
        获取所有农场信息（分页）
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :return: 农场列表
        """
        return db.query(Farm).offset(skip).limit(limit).all()
    
    def get_by_name(self, db: Session, name: str) -> Optional[Farm]:
        """
        根据名称获取农场信息
        :param db: 数据库会话
        :param name: 农场名称
        :return: 农场对象或None
        """
        return db.query(Farm).filter(Farm.name == name).first()
    
    def create(self, db: Session, farm: FarmCreate) -> Farm:
        """
        创建新农场
        :param db: 数据库会话
        :param farm: 农场创建数据
        :return: 创建的农场对象
        """
        db_farm = Farm(**farm.model_dump())
        db.add(db_farm)
        db.commit()
        db.refresh(db_farm)
        return db_farm
    
    def update(self, db: Session, farm_id: int, farm: FarmUpdate) -> Optional[Farm]:
        """
        更新农场信息
        :param db: 数据库会话
        :param farm_id: 农场ID
        :param farm: 农场更新数据
        :return: 更新后的农场对象或None
        """
        db_farm = self.get_by_id(db, farm_id)
        if db_farm:
            # 只更新提供的字段
            for key, value in farm.model_dump(exclude_unset=True).items():
                setattr(db_farm, key, value)
            db.commit()
            db.refresh(db_farm)
        return db_farm
    
    def delete(self, db: Session, farm_id: int) -> bool:
        """
        删除农场
        :param db: 数据库会话
        :param farm_id: 农场ID
        :return: 是否成功删除
        """
        db_farm = self.get_by_id(db, farm_id)
        if db_farm:
            db.delete(db_farm)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """
        统计农场数量
        :param db: 数据库会话
        :return: 农场总数
        """
        return db.query(Farm).count()


# 全局实例
farm_crud = FarmCRUD()
