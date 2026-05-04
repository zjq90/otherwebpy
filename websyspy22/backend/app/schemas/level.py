"""
等级与权益相关Pydantic模型
定义会员等级和权益的数据格式
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


class MemberLevelBase(BaseModel):
    """
    会员等级基础模型
    """
    level_code: str = Field(..., min_length=1, max_length=20, description="等级代码")
    level_name: str = Field(..., min_length=1, max_length=50, description="等级名称")
    description: Optional[str] = Field(default=None, description="等级描述")
    min_consumption: int = Field(default=0, description="最低消费门槛（分）")
    min_visits: int = Field(default=0, description="最低到店次数")
    sort_order: int = Field(default=0, description="排序顺序")
    icon_url: Optional[str] = Field(default=None, max_length=500, description="等级图标URL")
    color_hex: Optional[str] = Field(default=None, max_length=20, description="等级颜色（十六进制）")
    is_active: bool = Field(default=True, description="是否启用")
    
    class Config:
        from_attributes = True


class MemberLevelResponse(MemberLevelBase):
    """
    会员等级响应模型
    """
    id: int = Field(description="等级ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


class LevelBenefitBase(BaseModel):
    """
    等级权益基础模型
    """
    level_code: str = Field(..., min_length=1, max_length=20, description="关联等级代码")
    benefit_code: str = Field(..., min_length=1, max_length=50, description="权益代码")
    benefit_name: str = Field(..., min_length=1, max_length=100, description="权益名称")
    description: Optional[str] = Field(default=None, description="权益详细描述")
    benefit_type: str = Field(..., min_length=1, max_length=50, description="权益类型")
    value: Optional[Decimal] = Field(default=None, description="权益数值")
    unit: Optional[str] = Field(default=None, max_length=20, description="数值单位")
    sort_order: int = Field(default=0, description="显示排序")
    is_active: bool = Field(default=True, description="是否启用")
    
    class Config:
        from_attributes = True


class LevelBenefitResponse(LevelBenefitBase):
    """
    等级权益响应模型
    """
    id: int = Field(description="权益ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


class MemberLevelInfo(BaseModel):
    """
    会员等级信息
    用于展示会员当前等级和可享受的权益
    """
    # 当前等级信息
    current_level_code: str = Field(description="当前等级代码")
    current_level_name: str = Field(description="当前等级名称")
    current_level_description: Optional[str] = Field(description="当前等级描述")
    total_consumption: int = Field(description="累计消费金额（分）")
    total_visits: int = Field(description="累计到店次数")
    
    # 下一等级信息
    next_level_code: Optional[str] = Field(default=None, description="下一等级代码")
    next_level_name: Optional[str] = Field(default=None, description="下一等级名称")
    consumption_to_next_level: Optional[int] = Field(default=None, description="达到下一等级还需消费（分）")
    visits_to_next_level: Optional[int] = Field(default=None, description="达到下一等级还需到店次数")
    
    # 当前权益
    benefits: List[LevelBenefitResponse] = Field(default_factory=list, description="当前等级享有的权益列表")
    
    class Config:
        from_attributes = True


class LevelUpgradeRule(BaseModel):
    """
    等级升级规则说明
    """
    level_code: str = Field(description="等级代码")
    level_name: str = Field(description="等级名称")
    min_consumption: int = Field(description="最低消费门槛（分）")
    min_visits: int = Field(description="最低到店次数")
    sort_order: int = Field(description="排序顺序")
    
    class Config:
        from_attributes = True
