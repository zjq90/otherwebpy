from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

"""
会员和课程包相关的Pydantic模型
"""

class MemberBase(BaseModel):
    """
    会员基础模型
    """
    name: str = Field(..., min_length=1, max_length=50, description="会员姓名")
    gender: Optional[str] = Field(default="男", description="性别: 男/女")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号码")
    id_card: Optional[str] = Field(default=None, max_length=18, description="身份证号")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    age: Optional[int] = Field(default=None, ge=1, le=150, description="年龄")
    level: Optional[str] = Field(default="普通", description="会员等级: 普通/银卡/金卡/钻石")
    fitness_goal: Optional[str] = Field(default=None, max_length=100, description="健身目标")
    health_condition: Optional[str] = Field(default=None, description="健康状况")
    status: Optional[str] = Field(default="正常", description="状态: 正常/冻结/过期")
    register_date: Optional[date] = Field(default_factory=date.today, description="注册日期")
    note: Optional[str] = None


class MemberCreate(MemberBase):
    """
    创建会员时使用的模型
    """
    pass


class MemberUpdate(BaseModel):
    """
    更新会员时使用的模型
    """
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    level: Optional[str] = None
    fitness_goal: Optional[str] = None
    health_condition: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None


class MemberResponse(MemberBase):
    """
    会员响应模型
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """
    会员列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[MemberResponse]


# 课程包相关模型

class CoursePackageBase(BaseModel):
    """
    课程包基础模型
    """
    member_id: int = Field(..., description="会员ID")
    coach_id: Optional[int] = Field(default=None, description="教练ID，可为空")
    name: str = Field(..., min_length=1, max_length=100, description="课程包名称")
    course_type: Optional[str] = Field(default="常规课", description="课程类型")
    total_lessons: int = Field(..., ge=1, description="购买总课时")
    bonus_lessons: Optional[int] = Field(default=0, ge=0, description="赠送课时")
    unit_price: float = Field(..., ge=0, description="课程单价")
    discount_amount: Optional[float] = Field(default=0.0, ge=0, description="优惠金额")
    paid_amount: float = Field(..., ge=0, description="实付金额")
    purchase_date: Optional[date] = Field(default_factory=date.today, description="购买日期")
    start_date: Optional[date] = Field(default_factory=date.today, description="开始生效日期")
    expire_date: Optional[date] = Field(default=None, description="有效期截止日期")
    payment_method: Optional[str] = Field(default="微信", description="支付方式")
    note: Optional[str] = None


class CoursePackageCreate(CoursePackageBase):
    """
    创建课程包时使用的模型
    """
    pass


class CoursePackageUpdate(BaseModel):
    """
    更新课程包时使用的模型
    """
    coach_id: Optional[int] = None
    name: Optional[str] = None
    course_type: Optional[str] = None
    expire_date: Optional[date] = None
    status: Optional[str] = None
    note: Optional[str] = None


class CoursePackageResponse(CoursePackageBase):
    """
    课程包响应模型
    """
    id: int
    package_no: str
    used_lessons: int
    remaining_lessons: int
    frozen_lessons: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CoursePackageListResponse(BaseModel):
    """
    课程包列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[CoursePackageResponse]
