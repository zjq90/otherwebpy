from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Plot
from ..schemas import PlotCreate, PlotUpdate


class PlotCRUD:
    """
    地块管理CRUD操作类
    提供地块信息的增删改查功能
    """
    
    def get_by_id(self, db: Session, plot_id: int) -> Optional[Plot]:
        """
        根据ID获取地块信息
        :param db: 数据库会话
        :param plot_id: 地块ID
        :return: 地块对象或None
        """
        return db.query(Plot).filter(Plot.id == plot_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Plot]:
        """
        获取所有地块信息（分页）
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :return: 地块列表
        """
        return db.query(Plot).offset(skip).limit(limit).all()
    
    def get_by_plot_number(self, db: Session, plot_number: str) -> Optional[Plot]:
        """
        根据地块编号获取地块信息
        :param db: 数据库会话
        :param plot_number: 地块编号
        :return: 地块对象或None
        """
        return db.query(Plot).filter(Plot.plot_number == plot_number).first()
    
    def get_by_farm_id(self, db: Session, farm_id: int) -> List[Plot]:
        """
        根据农场ID获取该农场下的所有地块
        :param db: 数据库会话
        :param farm_id: 农场ID
        :return: 地块列表
        """
        return db.query(Plot).filter(Plot.farm_id == farm_id).all()
    
    def create(self, db: Session, plot: PlotCreate) -> Plot:
        """
        创建新地块
        :param db: 数据库会话
        :param plot: 地块创建数据
        :return: 创建的地块对象
        """
        db_plot = Plot(**plot.model_dump())
        db.add(db_plot)
        db.commit()
        db.refresh(db_plot)
        return db_plot
    
    def update(self, db: Session, plot_id: int, plot: PlotUpdate) -> Optional[Plot]:
        """
        更新地块信息
        :param db: 数据库会话
        :param plot_id: 地块ID
        :param plot: 地块更新数据
        :return: 更新后的地块对象或None
        """
        db_plot = self.get_by_id(db, plot_id)
        if db_plot:
            # 只更新提供的字段
            for key, value in plot.model_dump(exclude_unset=True).items():
                setattr(db_plot, key, value)
            db.commit()
            db.refresh(db_plot)
        return db_plot
    
    def delete(self, db: Session, plot_id: int) -> bool:
        """
        删除地块
        :param db: 数据库会话
        :param plot_id: 地块ID
        :return: 是否成功删除
        """
        db_plot = self.get_by_id(db, plot_id)
        if db_plot:
            db.delete(db_plot)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """
        统计地块数量
        :param db: 数据库会话
        :return: 地块总数
        """
        return db.query(Plot).count()


# 全局实例
plot_crud = PlotCRUD()
