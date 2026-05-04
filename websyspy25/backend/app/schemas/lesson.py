from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

"""
课时记录、补课、冻结相关的Pydantic模型
"""

class LessonRecordBase(BaseModel):
    """
    课时记录基础模型
    """
    package_id: int = Field(..., description="课程包ID")
    member_id: int = Field(..., description="会员ID")
    coach_id: int = Field(..., description="教练ID")
    lesson_type: Optional[str] = Field(default="常规课", description="课程类型: 常规课/补课/赠送课")
    hours_used: Optional[float] = Field(default=1.0, gt=0, description="消耗课时数")
    lesson_date: Optional[date] = Field(default_factory=date.today, description="上课日期")
    start_time: Optional[str] = Field(default=None, description="开始时间 HH:MM")
    end_time: Optional[str] = Field(default=None, description="结束时间 HH:MM")
    lesson_content: Optional[str] = Field(default=None, description="课程内容")
    member_rating: Optional[int] = Field(default=None, ge=1, le=5, description="会员评分 1-5")
    member_feedback: Optional[str] = Field(default=None, description="会员反馈")
    coach_note: Optional[str] = Field(default=None, description="教练备注")
    status: Optional[str] = Field(default="已预约", description="状态: 已预约/已完成/已取消/已缺席")
    note: Optional[str] = None


class LessonRecordCreate(LessonRecordBase):
    """
    创建课时记录时使用的模型
    """
    pass


class LessonRecordComplete(BaseModel):
    """
    完成课时时使用的模型
    """
    end_time: Optional[str] = None
    lesson_content: Optional[str] = None
    member_rating: Optional[int] = None
    member_feedback: Optional[str] = None
    coach_note: Optional[str] = None
    note: Optional[str] = None


class LessonRecordUpdate(BaseModel):
    """
    更新课时记录时使用的模型
    """
    lesson_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    lesson_content: Optional[str] = None
    member_rating: Optional[int] = None
    member_feedback: Optional[str] = None
    coach_note: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None


class LessonRecordResponse(LessonRecordBase):
    """
    课时记录响应模型
    """
    id: int
    record_no: str
    is_makeup: bool
    makeup_id: Optional[int]
    coach_commission: float
    revenue_contribution: float
    operator_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LessonRecordListResponse(BaseModel):
    """
    课时记录列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[LessonRecordResponse]


# 补课相关模型

class MakeupLessonBase(BaseModel):
    """
    补课基础模型
    """
    member_id: int = Field(..., description="会员ID")
    package_id: int = Field(..., description="课程包ID")
    original_lesson_id: Optional[int] = Field(default=None, description="原课程记录ID")
    reason: str = Field(..., min_length=1, max_length=100, description="补课原因")
    reason_detail: Optional[str] = Field(default=None, description="原因详情")
    requested_count: Optional[int] = Field(default=1, ge=1, description="申请补课数量")
    apply_date: Optional[date] = Field(default_factory=date.today, description="申请日期")
    expire_date: Optional[date] = Field(default=None, description="有效期截止日期")
    note: Optional[str] = None


class MakeupLessonCreate(MakeupLessonBase):
    """
    创建补课时使用的模型
    """
    pass


class MakeupLessonApprove(BaseModel):
    """
    审批补课时使用的模型
    """
    status: str = Field(..., description="状态: 已批准/已拒绝")
    approval_note: Optional[str] = None


class MakeupLessonUpdate(BaseModel):
    """
    更新补课时使用的模型
    """
    expire_date: Optional[date] = None
    note: Optional[str] = None


class MakeupLessonResponse(MakeupLessonBase):
    """
    补课响应模型
    """
    id: int
    makeup_no: str
    used_count: int
    remaining_count: int
    status: str
    approval_note: Optional[str]
    approver_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MakeupLessonListResponse(BaseModel):
    """
    补课列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[MakeupLessonResponse]


# 冻结相关模型

class FreezeRecordBase(BaseModel):
    """
    冻结记录基础模型
    """
    member_id: int = Field(..., description="会员ID")
    package_id: int = Field(..., description="课程包ID")
    operation_type: str = Field(..., description="操作类型: 冻结/解冻")
    reason: Optional[str] = Field(default=None, description="冻结原因")
    freeze_start_date: Optional[date] = Field(default_factory=date.today, description="冻结开始日期")
    planned_end_date: Optional[date] = Field(default=None, description="计划冻结结束日期")
    frozen_lessons: Optional[int] = Field(default=0, ge=0, description="冻结课时数量")
    note: Optional[str] = None


class FreezeRecordCreate(FreezeRecordBase):
    """
    创建冻结记录时使用的模型
    """
    pass


class FreezeRecordResponse(FreezeRecordBase):
    """
    冻结记录响应模型
    """
    id: int
    freeze_no: str
    actual_end_date: Optional[date]
    status: str
    operator_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FreezeRecordListResponse(BaseModel):
    """
    冻结记录列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[FreezeRecordResponse]
