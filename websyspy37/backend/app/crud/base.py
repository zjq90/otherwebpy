"""
通用CRUD基类
提供基础的增删改查操作
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import Base

# 定义泛型类型
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用CRUD基类
    提供基础的增删改查操作
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化CRUD对象
        :param model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单条记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 记录对象或None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        获取多条记录（分页）
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 每页记录数
        :return: 记录列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        :param db: 数据库会话
        :param obj_in: 创建数据
        :return: 创建的记录对象
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        :param db: 数据库会话
        :param db_obj: 数据库中的记录对象
        :param obj_in: 更新数据
        :return: 更新后的记录对象
        """
        obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        删除记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 删除的记录对象
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
