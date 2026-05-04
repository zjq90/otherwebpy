from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

"""
业绩追踪相关的Pydantic模型
"""

class PerformanceRecordBase(BaseModel):
    """
    业绩记录基础模型
    """
    coach_id: int = Field(..., description="教练ID")
    period_type: str = Field(default="月度", description="统计类型: 月度/季度")
    year: int = Field(..., ge=2000, le=2100, description="年份")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="月份 1-12")
    quarter: Optional[int] = Field(default=None, ge=1, le=4, description="季度 1-4")


class PerformanceRecordResponse(PerformanceRecordBase):
    """
    业绩记录响应模型
    """
    id: int
    total_lessons: int
    regular_lessons: int
    makeup_lessons: int
    total_hours: float
    avg_rating: float
    rated_lessons: int
    five_star_count: int
    four_star_count: int
    three_star_count: int
    total_revenue: float
    new_members_count: int
    renewal_members_count: int
    total_commission: float
    rank: Optional[int]
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PerformanceRecordListResponse(BaseModel):
    """
    业绩记录列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[PerformanceRecordResponse]


class CoachStatsResponse(BaseModel):
    """
    教练统计数据响应模型
    用于首页或统计页面的快速展示
    """
    coach_id: int
    coach_name: str
    
    # 今日统计
    today_lessons: int = 0
    today_hours: float = 0.0
    today_revenue: float = 0.0
    
    # 本周统计
    week_lessons: int = 0
    week_hours: float = 0.0
    week_revenue: float = 0.0
    
    # 本月统计
    month_lessons: int = 0
    month_hours: float = 0.0
    month_revenue: float = 0.0
    month_commission: float = 0.0
    
    # 历史累计
    total_lessons: int = 0
    total_hours: float = 0.0
    total_revenue: float = 0.0
    
    # 评分统计
    avg_rating: float = 0.0
    total_ratings: int = 0
    
    # 当前排名
    current_rank: Optional[int] = None


class MonthlySummaryResponse(BaseModel):
    """
    月度汇总响应模型
    """
    id: int
    coach_id: int
    year: int
    month: int
    lessons_count: int
    hours_count: float
    revenue: float
    commission: float
    avg_score: float
    status: str
    settlement_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PerformanceQueryParams(BaseModel):
    """
    业绩查询参数模型
    """
    coach_id: Optional[int] = Field(default=None, description="教练ID，为空则查询所有")
    year: Optional[int] = Field(default=None, description="年份")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="月份")
    quarter: Optional[int] = Field(default=None, ge=1, le=4, description="季度")
    period_type: Optional[str] = Field(default="月度", description="统计类型")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数")
