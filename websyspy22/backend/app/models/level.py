"""
会员等级与权益数据模型
定义会员等级体系和对应的权益
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric
from app.database import Base


class MemberLevel(Base):
    """
    会员等级配置表
    定义不同会员等级的配置信息
    """
    __tablename__ = "member_levels"

    id = Column(Integer, primary_key=True, index=True, comment="等级ID")
    
    # 等级基本信息
    level_code = Column(String(20), unique=True, nullable=False, comment="等级代码: bronze/silver/gold")
    level_name = Column(String(50), nullable=False, comment="等级名称: 铜卡/银卡/金卡")
    description = Column(Text, nullable=True, comment="等级描述")
    
    # 等级门槛
    min_consumption = Column(Integer, default=0, comment="最低消费门槛（分）")
    min_visits = Column(Integer, default=0, comment="最低到店次数")
    
    # 等级排序
    sort_order = Column(Integer, default=0, comment="排序顺序，数值越大等级越高")
    
    # 等级标识
    icon_url = Column(String(500), nullable=True, comment="等级图标URL")
    color_hex = Column(String(20), nullable=True, comment="等级颜色（十六进制）")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class LevelBenefit(Base):
    """
    等级权益配置表
    定义每个会员等级享有的权益
    """
    __tablename__ = "level_benefits"

    id = Column(Integer, primary_key=True, index=True, comment="权益ID")
    
    # 关联等级
    level_code = Column(String(20), nullable=False, index=True, comment="关联等级代码")
    
    # 权益基本信息
    benefit_code = Column(String(50), nullable=False, comment="权益代码")
    benefit_name = Column(String(100), nullable=False, comment="权益名称")
    description = Column(Text, nullable=True, comment="权益详细描述")
    
    # 权益类型和值
    benefit_type = Column(String(50), nullable=False, comment="权益类型: discount/free/priority/other")
    value = Column(Numeric(10, 2), nullable=True, comment="权益数值（如折扣率、免费次数等）")
    unit = Column(String(20), nullable=True, comment="数值单位")
    
    # 示例：
    # 课程折扣: benefit_type=discount, value=0.9 (9折), unit=%
    # 免费体测: benefit_type=free, value=1 (每月1次), unit=次/月
    # 优先预约: benefit_type=priority, value=24 (提前24小时), unit=小时
    
    # 排序
    sort_order = Column(Integer, default=0, comment="显示排序")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
