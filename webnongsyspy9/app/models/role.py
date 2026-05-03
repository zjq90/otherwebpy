from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from ..database import Base


class Role(Base):
    """
    角色管理模型
    存储系统角色信息和权限配置
    """
    
    __tablename__ = "roles"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 角色名称
    name = Column(String(100), nullable=False, comment="角色名称")
    
    # 角色代码（唯一标识）
    code = Column(String(100), nullable=False, unique=True, index=True, comment="角色代码")
    
    # 角色描述
    description = Column(String(500), nullable=True, comment="角色描述")
    
    # 权限列表（逗号分隔的权限代码）
    permissions = Column(Text, nullable=True, comment="权限列表")
    
    # 是否为系统预设角色（不可删除）
    is_system = Column(Boolean, nullable=False, default=False, comment="是否系统预设")
    
    # 是否为默认角色（新员工默认分配）
    is_default = Column(Boolean, nullable=False, default=False, comment="是否默认角色")
    
    # 排序顺序
    sort_order = Column(Integer, nullable=False, default=0, comment="排序顺序")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', code='{self.code}')>"
