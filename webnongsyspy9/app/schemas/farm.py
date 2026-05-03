from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FarmBase(BaseModel):
    """
    农场信息基础模型
    包含农场信息的公共字段
    """
    
    # 农场名称
    name: str = Field(..., min_length=1, max_length=200, description="农场名称")
    
    # 农场地址
    address: str = Field(..., min_length=1, max_length=500, description="农场地址")
    
    # 负责人姓名
    manager: str = Field(..., min_length=1, max_length=100, description="负责人")
    
    # 联系方式（电话/手机）
    contact: str = Field(..., min_length=1, max_length=50, description="联系方式")
    
    # 土地面积（单位：亩）
    land_area: float = Field(..., gt=0, description="土地面积(亩)")
    
    # 认证类型：绿色/有机/无公害
    certification_type: str = Field(default="绿色", pattern="^(绿色|有机|无公害)$", description="认证类型")
    
    # 农场描述/备注
    description: Optional[str] = Field(None, description="农场描述")


class FarmCreate(FarmBase):
    """
    创建农场时使用的模型
    继承自FarmBase，无需额外字段
    """
    pass


class FarmUpdate(BaseModel):
    """
    更新农场时使用的模型
    所有字段都是可选的
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="农场名称")
    address: Optional[str] = Field(None, min_length=1, max_length=500, description="农场地址")
    manager: Optional[str] = Field(None, min_length=1, max_length=100, description="负责人")
    contact: Optional[str] = Field(None, min_length=1, max_length=50, description="联系方式")
    land_area: Optional[float] = Field(None, gt=0, description="土地面积(亩)")
    certification_type: Optional[str] = Field(None, pattern="^(绿色|有机|无公害)$", description="认证类型")
    description: Optional[str] = Field(None, description="农场描述")


class FarmResponse(FarmBase):
    """
    农场响应模型
    包含从数据库读取时返回的所有字段
    """
    
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
