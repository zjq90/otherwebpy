from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

"""
教练相关的Pydantic模型
用于API请求参数验证和响应数据序列化
"""

class CoachBase(BaseModel):
    """
    教练基础模型
    包含教练的通用字段
    """
    name: str = Field(..., min_length=1, max_length=50, description="教练姓名")
    gender: Optional[str] = Field(default="男", description="性别: 男/女")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号码")
    id_card: Optional[str] = Field(default=None, max_length=18, description="身份证号")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    address: Optional[str] = Field(default=None, max_length=200, description="住址")
    hire_date: Optional[date] = Field(default_factory=date.today, description="入职日期")
    level: Optional[str] = Field(default="初级", description="教练级别: 初级/中级/高级/金牌")
    expertise: Optional[str] = Field(default=None, max_length=200, description="擅长领域，多个用逗号分隔")
    bio: Optional[str] = Field(default=None, description="个人简介")
    hourly_rate: Optional[float] = Field(default=100.0, ge=0, description="课时费率（每小时）")
    commission_rate: Optional[float] = Field(default=30.0, ge=0, le=100, description="提成比例（百分比）")
    status: Optional[str] = Field(default="在职", description="状态: 在职/离职/休假")


class CoachCreate(CoachBase):
    """
    创建教练时使用的模型
    继承基础模型，无需额外字段
    """
    pass


class CoachUpdate(BaseModel):
    """
    更新教练时使用的模型
    所有字段都是可选的
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    gender: Optional[str] = None
    phone: Optional[str] = Field(default=None, min_length=11, max_length=20)
    id_card: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    hire_date: Optional[date] = None
    level: Optional[str] = None
    expertise: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = Field(default=None, ge=0)
    commission_rate: Optional[float] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None


class CoachResponse(CoachBase):
    """
    教练响应模型
    包含数据库中的所有字段
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CoachListResponse(BaseModel):
    """
    教练列表响应模型
    用于分页查询
    """
    total: int
    page: int
    page_size: int
    data: List[CoachResponse]


# 排班相关模型

class CoachScheduleBase(BaseModel):
    """
    排班基础模型
    """
    coach_id: int = Field(..., description="教练ID")
    day_of_week: int = Field(..., ge=1, le=7, description="星期几: 1-7")
    start_time: str = Field(..., min_length=5, max_length=5, description="开始时间，格式 HH:MM")
    end_time: str = Field(..., min_length=5, max_length=5, description="结束时间，格式 HH:MM")
    status: Optional[str] = Field(default="可用", description="状态: 可用/已预约/休息")
    note: Optional[str] = None


class CoachScheduleCreate(CoachScheduleBase):
    """
    创建排班时使用的模型
    """
    pass


class CoachScheduleUpdate(BaseModel):
    """
    更新排班时使用的模型
    """
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None


class CoachScheduleResponse(CoachScheduleBase):
    """
    排班响应模型
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CoachWithScheduleResponse(CoachResponse):
    """
    带排班信息的教练响应模型
    """
    schedules: List[CoachScheduleResponse] = []
    
    class Config:
        from_attributes = True
