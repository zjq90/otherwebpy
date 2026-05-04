"""
课程管理Pydantic Schema
定义课程类型、课程和课程排期的请求/响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time


class CourseTypeBase(BaseModel):
    """
    课程类型基础Schema
    包含课程类型的基本字段
    """
    name: str = Field(..., min_length=1, max_length=50, description="课程类型名称")
    code: str = Field(..., min_length=1, max_length=50, description="课程类型代码")
    description: Optional[str] = Field(None, description="课程类型描述")
    is_active: Optional[bool] = Field(True, description="是否启用")


class CourseTypeCreate(CourseTypeBase):
    """
    课程类型创建Schema
    继承自CourseTypeBase，用于创建新的课程类型
    """
    pass


class CourseTypeUpdate(BaseModel):
    """
    课程类型更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="课程类型名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="课程类型代码")
    description: Optional[str] = Field(None, description="课程类型描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CourseTypeResponse(CourseTypeBase):
    """
    课程类型响应Schema
    包含课程类型的所有字段，用于返回给前端
    """
    id: int = Field(..., description="课程类型ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """
    课程基础Schema
    包含课程的基本字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="课程名称")
    course_type_id: int = Field(..., description="课程类型ID")
    duration: int = Field(60, gt=0, description="课程时长(分钟)")
    max_capacity: int = Field(20, gt=0, description="最大容量")
    description: Optional[str] = Field(None, description="课程描述")
    difficulty_level: Optional[int] = Field(3, ge=1, le=5, description="难度等级(1-5)")
    suitable_for: Optional[str] = Field(None, max_length=200, description="适合人群")
    precautions: Optional[str] = Field(None, description="注意事项")
    image_url: Optional[str] = Field(None, max_length=500, description="课程图片URL")
    instructor: Optional[str] = Field(None, max_length=100, description="教练/老师名称")
    is_active: Optional[bool] = Field(True, description="是否启用")


class CourseCreate(CourseBase):
    """
    课程创建Schema
    继承自CourseBase，用于创建新的课程
    """
    pass


class CourseUpdate(BaseModel):
    """
    课程更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="课程名称")
    course_type_id: Optional[int] = Field(None, description="课程类型ID")
    duration: Optional[int] = Field(None, gt=0, description="课程时长(分钟)")
    max_capacity: Optional[int] = Field(None, gt=0, description="最大容量")
    description: Optional[str] = Field(None, description="课程描述")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="难度等级(1-5)")
    suitable_for: Optional[str] = Field(None, max_length=200, description="适合人群")
    precautions: Optional[str] = Field(None, description="注意事项")
    image_url: Optional[str] = Field(None, max_length=500, description="课程图片URL")
    instructor: Optional[str] = Field(None, max_length=100, description="教练/老师名称")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CourseResponse(CourseBase):
    """
    课程响应Schema
    包含课程的所有字段，用于返回给前端
    """
    id: int = Field(..., description="课程ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    course_type: Optional[CourseTypeResponse] = Field(None, description="关联的课程类型")
    
    class Config:
        from_attributes = True


class CourseScheduleBase(BaseModel):
    """
    课程排期基础Schema
    包含课程排期的基本字段
    """
    course_id: int = Field(..., description="课程ID")
    venue_id: int = Field(..., description="场地ID")
    schedule_date: date = Field(..., description="课程日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    instructor: Optional[str] = Field(None, max_length=100, description="教练名称")
    max_capacity: Optional[int] = Field(None, gt=0, description="最大容量")
    status: Optional[str] = Field("scheduled", max_length=20, description="排期状态")
    remarks: Optional[str] = Field(None, description="备注")


class CourseScheduleCreate(CourseScheduleBase):
    """
    课程排期创建Schema
    继承自CourseScheduleBase，用于创建新的课程排期
    """
    pass


class CourseScheduleUpdate(BaseModel):
    """
    课程排期更新Schema
    所有字段都是可选的，用于部分更新
    """
    course_id: Optional[int] = Field(None, description="课程ID")
    venue_id: Optional[int] = Field(None, description="场地ID")
    schedule_date: Optional[date] = Field(None, description="课程日期")
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    instructor: Optional[str] = Field(None, max_length=100, description="教练名称")
    max_capacity: Optional[int] = Field(None, gt=0, description="最大容量")
    booked_count: Optional[int] = Field(None, ge=0, description="已预约人数")
    status: Optional[str] = Field(None, max_length=20, description="排期状态")
    remarks: Optional[str] = Field(None, description="备注")


class CourseScheduleResponse(CourseScheduleBase):
    """
    课程排期响应Schema
    包含课程排期的所有字段，用于返回给前端
    """
    id: int = Field(..., description="排期ID")
    booked_count: int = Field(0, description="已预约人数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    course: Optional[CourseResponse] = Field(None, description="关联的课程")
    
    class Config:
        from_attributes = True
