from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Staff(Base):
    """
    人员管理模型
    存储员工信息和权限配置
    """
    
    __tablename__ = "staff"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 员工工号
    staff_number = Column(String(50), nullable=False, unique=True, comment="员工工号")
    
    # 员工姓名
    name = Column(String(100), nullable=False, comment="员工姓名")
    
    # 性别
    gender = Column(String(10), nullable=True, comment="性别")
    
    # 年龄
    age = Column(Integer, nullable=True, comment="年龄")
    
    # 联系电话
    phone = Column(String(50), nullable=True, comment="联系电话")
    
    # 邮箱
    email = Column(String(100), nullable=True, comment="邮箱")
    
    # 身份证号
    id_card = Column(String(50), nullable=True, comment="身份证号")
    
    # 所属角色ID（外键）
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True, comment="所属角色ID")
    
    # 岗位职责
    position = Column(String(200), nullable=False, comment="岗位职责")
    
    # 所属部门
    department = Column(String(100), nullable=True, comment="所属部门")
    
    # 操作权限（以逗号分隔的权限列表，如：farm:read,plot:write等）
    # 当员工有自定义权限时使用，否则使用角色权限
    permissions = Column(Text, nullable=True, comment="操作权限")
    
    # 入职日期
    join_date = Column(DateTime, nullable=True, comment="入职日期")
    
    # 员工状态（在职/离职/休假等）
    status = Column(String(50), nullable=False, default="在职", comment="员工状态")
    
    # 备注信息
    remarks = Column(Text, nullable=True, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Staff(id={self.id}, name='{self.name}')>"
