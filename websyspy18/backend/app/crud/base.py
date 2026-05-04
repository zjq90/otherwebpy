"""
基础CRUD类
提供通用的增删改查操作，供其他CRUD类继承
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础CRUD类
    实现了通用的增删改查操作
    
    Type Parameters:
        ModelType: SQLAlchemy模型类
        CreateSchemaType: 创建数据的Pydantic Schema
        UpdateSchemaType: 更新数据的Pydantic Schema
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD构造函数
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单条记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[ModelType]: 找到的记录，如果不存在则返回None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        获取多条记录（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            List[ModelType]: 记录列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        
        Args:
            db: 数据库会话
            obj_in: 创建数据的Schema对象
            
        Returns:
            ModelType: 创建的记录
        """
        obj_in_data = jsonable_encoder(obj_in)
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
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的现有记录对象
            obj_in: 更新的数据，可以是Schema对象或字典
            
        Returns:
            ModelType: 更新后的记录
        """
        obj_data = jsonable_encoder(db_obj)
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

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        根据ID删除记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[ModelType]: 被删除的记录，如果不存在则返回None
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
