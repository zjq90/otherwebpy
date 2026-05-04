from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, date, timedelta
from calendar import monthrange

from ..database import get_db
from ..models.performance import PerformanceRecord, MonthlySummary
from ..models.lesson import LessonRecord
from ..models.coach import Coach
from ..schemas.performance import (
    PerformanceRecordResponse, PerformanceRecordListResponse,
    CoachStatsResponse, MonthlySummaryResponse, PerformanceQueryParams
)

"""
业绩追踪API路由
实现按月/季度统计教练授课数量、会员反馈与收入贡献的功能
"""

router = APIRouter(
    prefix="/api/performance",
    tags=["业绩追踪"]
)


def get_month_date_range(year: int, month: int) -> tuple:
    """获取指定月份的日期范围"""
    first_day = date(year, month, 1)
    _, last_day_num = monthrange(year, month)
    last_day = date(year, month, last_day_num)
    return first_day, last_day


def get_quarter_date_range(year: int, quarter: int) -> tuple:
    """获取指定季度的日期范围"""
    if quarter == 1:
        return date(year, 1, 1), date(year, 3, 31)
    elif quarter == 2:
        return date(year, 4, 1), date(year, 6, 30)
    elif quarter == 3:
        return date(year, 7, 1), date(year, 9, 30)
    else:
        return date(year, 10, 1), date(year, 12, 31)


@router.get("/stats/{coach_id}", response_model=CoachStatsResponse, summary="获取教练统计数据")
def get_coach_stats(
    coach_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定教练的统计数据
    包括今日、本周、本月、历史累计的统计
    """
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = date(today.year, today.month, 1)
    
    # 基础统计查询
    def get_stats_by_date_range(start_date: date, end_date: date):
        return db.query(
            func.count(LessonRecord.id).label('lessons_count'),
            func.coalesce(func.sum(LessonRecord.hours_used), 0).label('hours_count'),
            func.coalesce(func.sum(LessonRecord.revenue_contribution), 0).label('revenue'),
            func.coalesce(func.sum(LessonRecord.coach_commission), 0).label('commission')
        ).filter(
            LessonRecord.coach_id == coach_id,
            LessonRecord.status == "已完成",
            LessonRecord.lesson_date >= start_date,
            LessonRecord.lesson_date <= end_date
        ).first()
    
    # 今日统计
    today_stats = get_stats_by_date_range(today, today)
    
    # 本周统计
    week_stats = get_stats_by_date_range(week_start, today)
    
    # 本月统计
    month_stats = get_stats_by_date_range(month_start, today)
    
    # 历史累计统计
    total_stats = db.query(
        func.count(LessonRecord.id).label('lessons_count'),
        func.coalesce(func.sum(LessonRecord.hours_used), 0).label('hours_count'),
        func.coalesce(func.sum(LessonRecord.revenue_contribution), 0).label('revenue')
    ).filter(
        LessonRecord.coach_id == coach_id,
        LessonRecord.status == "已完成"
    ).first()
    
    # 评分统计
    rating_stats = db.query(
        func.coalesce(func.avg(LessonRecord.member_rating), 0).label('avg_rating'),
        func.count(LessonRecord.member_rating).label('total_ratings')
    ).filter(
        LessonRecord.coach_id == coach_id,
        LessonRecord.status == "已完成",
        LessonRecord.member_rating.isnot(None)
    ).first()
    
    return CoachStatsResponse(
        coach_id=coach_id,
        coach_name=coach.name,
        
        # 今日统计
        today_lessons=today_stats.lessons_count or 0,
        today_hours=float(today_stats.hours_count or 0),
        today_revenue=float(today_stats.revenue or 0),
        
        # 本周统计
        week_lessons=week_stats.lessons_count or 0,
        week_hours=float(week_stats.hours_count or 0),
        week_revenue=float(week_stats.revenue or 0),
        
        # 本月统计
        month_lessons=month_stats.lessons_count or 0,
        month_hours=float(month_stats.hours_count or 0),
        month_revenue=float(month_stats.revenue or 0),
        month_commission=float(month_stats.commission or 0),
        
        # 历史累计
        total_lessons=total_stats.lessons_count or 0,
        total_hours=float(total_stats.hours_count or 0),
        total_revenue=float(total_stats.revenue or 0),
        
        # 评分统计
        avg_rating=float(rating_stats.avg_rating or 0),
        total_ratings=rating_stats.total_ratings or 0
    )


@router.post("/generate/monthly", summary="生成月度业绩记录")
def generate_monthly_performance(
    year: int = Query(..., ge=2000, le=2100, description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    coach_id: Optional[int] = Query(None, description="教练ID，为空则生成所有教练"),
    db: Session = Depends(get_db)
):
    """
    生成指定月份的业绩记录
    统计该月份内所有已完成的课时
    """
    first_day, last_day = get_month_date_range(year, month)
    
    # 获取教练列表
    coaches_query = db.query(Coach)
    if coach_id:
        coaches_query = coaches_query.filter(Coach.id == coach_id)
    coaches = coaches_query.filter(Coach.status == "在职").all()
    
    if not coaches:
        raise HTTPException(status_code=404, detail="没有找到符合条件的教练")
    
    generated_count = 0
    
    for coach in coaches:
        # 删除已存在的该月份记录
        existing = db.query(PerformanceRecord).filter(
            PerformanceRecord.coach_id == coach.id,
            PerformanceRecord.period_type == "月度",
            PerformanceRecord.year == year,
            PerformanceRecord.month == month
        ).first()
        
        if existing:
            db.delete(existing)
            db.flush()
        
        # 统计该月份的数据
        lessons_query = db.query(LessonRecord).filter(
            LessonRecord.coach_id == coach.id,
            LessonRecord.status == "已完成",
            LessonRecord.lesson_date >= first_day,
            LessonRecord.lesson_date <= last_day
        )
        
        lessons = lessons_query.all()
        total_lessons = len(lessons)
        
        if total_lessons == 0:
            continue
        
        # 计算各项统计
        total_hours = sum(l.hours_used for l in lessons)
        total_revenue = sum(l.revenue_contribution for l in lessons)
        total_commission = sum(l.coach_commission for l in lessons)
        
        # 统计评分
        rated_lessons = [l for l in lessons if l.member_rating is not None]
        rated_count = len(rated_lessons)
        avg_rating = sum(l.member_rating for l in rated_lessons) / rated_count if rated_count > 0 else 0
        
        # 统计星级分布
        five_star = sum(1 for l in rated_lessons if l.member_rating == 5)
        four_star = sum(1 for l in rated_lessons if l.member_rating == 4)
        three_star = sum(1 for l in rated_lessons if l.member_rating == 3)
        
        # 统计常规课和补课
        regular_count = sum(1 for l in lessons if not l.is_makeup)
        makeup_count = sum(1 for l in lessons if l.is_makeup)
        
        # 创建业绩记录
        performance = PerformanceRecord(
            coach_id=coach.id,
            period_type="月度",
            year=year,
            month=month,
            quarter=None,
            total_lessons=total_lessons,
            regular_lessons=regular_count,
            makeup_lessons=makeup_count,
            total_hours=total_hours,
            avg_rating=avg_rating,
            rated_lessons=rated_count,
            five_star_count=five_star,
            four_star_count=four_star,
            three_star_count=three_star,
            total_revenue=total_revenue,
            total_commission=total_commission
        )
        
        db.add(performance)
        generated_count += 1
    
    db.commit()
    
    return {
        "message": f"成功生成 {generated_count} 条月度业绩记录",
        "year": year,
        "month": month,
        "count": generated_count
    }


@router.get("/records/", response_model=PerformanceRecordListResponse, summary="获取业绩记录列表")
def get_performance_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    year: Optional[int] = Query(None, description="年份"),
    month: Optional[int] = Query(None, ge=1, le=12, description="月份"),
    quarter: Optional[int] = Query(None, ge=1, le=4, description="季度"),
    period_type: Optional[str] = Query("月度", description="统计类型：月度/季度"),
    db: Session = Depends(get_db)
):
    """
    分页获取业绩记录列表
    支持按教练、年份、月份、季度、统计类型筛选
    """
    query = db.query(PerformanceRecord)
    
    # 应用筛选条件
    if coach_id:
        query = query.filter(PerformanceRecord.coach_id == coach_id)
    if year:
        query = query.filter(PerformanceRecord.year == year)
    if month and period_type == "月度":
        query = query.filter(PerformanceRecord.month == month)
    if quarter and period_type == "季度":
        query = query.filter(PerformanceRecord.quarter == quarter)
    if period_type:
        query = query.filter(PerformanceRecord.period_type == period_type)
    
    # 获取总记录数
    total = query.count()
    
    # 分页查询
    records = query.order_by(
        PerformanceRecord.year.desc(),
        PerformanceRecord.month.desc() if period_type == "月度" else PerformanceRecord.quarter.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return PerformanceRecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=records
    )


@router.get("/records/{record_id}", response_model=PerformanceRecordResponse, summary="获取单个业绩记录详情")
def get_performance_record(record_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个业绩记录详情
    """
    record = db.query(PerformanceRecord).filter(PerformanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="业绩记录不存在")
    return record


@router.get("/ranking/", summary="获取教练业绩排名")
def get_coach_ranking(
    year: int = Query(..., ge=2000, le=2100, description="年份"),
    month: Optional[int] = Query(None, ge=1, le=12, description="月份，为空则按年度"),
    db: Session = Depends(get_db)
):
    """
    获取教练业绩排名
    按月度或年度排名，按收入贡献降序
    """
    # 获取业绩记录
    query = db.query(PerformanceRecord).filter(
        PerformanceRecord.year == year,
        PerformanceRecord.period_type == "月度" if month else "月度"
    )
    
    if month:
        query = query.filter(PerformanceRecord.month == month)
    
    records = query.order_by(PerformanceRecord.total_revenue.desc()).all()
    
    # 构建排名列表
    ranking = []
    for i, record in enumerate(records, 1):
        coach = db.query(Coach).filter(Coach.id == record.coach_id).first()
        ranking.append({
            "rank": i,
            "coach_id": record.coach_id,
            "coach_name": coach.name if coach else "未知",
            "total_lessons": record.total_lessons,
            "total_hours": record.total_hours,
            "total_revenue": record.total_revenue,
            "avg_rating": record.avg_rating
        })
    
    return {
        "year": year,
        "month": month,
        "total_coaches": len(ranking),
        "ranking": ranking
    }


@router.get("/monthly-summary/", response_model=List[MonthlySummaryResponse], summary="获取月度汇总列表")
def get_monthly_summaries(
    coach_id: int = Query(..., description="教练ID"),
    year: Optional[int] = Query(None, description="年份"),
    db: Session = Depends(get_db)
):
    """
    获取指定教练的月度汇总列表
    用于图表展示
    """
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    query = db.query(MonthlySummary).filter(MonthlySummary.coach_id == coach_id)
    
    if year:
        query = query.filter(MonthlySummary.year == year)
    
    summaries = query.order_by(MonthlySummary.year.desc(), MonthlySummary.month.desc()).all()
    
    # 如果没有月度汇总数据，从业绩记录生成
    if not summaries:
        # 从业绩记录生成简化的汇总数据
        perf_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.coach_id == coach_id,
            PerformanceRecord.period_type == "月度"
        )
        if year:
            perf_records = perf_records.filter(PerformanceRecord.year == year)
        
        perf_records = perf_records.order_by(
            PerformanceRecord.year.desc(),
            PerformanceRecord.month.desc()
        ).all()
        
        summaries = []
        for record in perf_records:
            summary = MonthlySummary(
                coach_id=record.coach_id,
                year=record.year,
                month=record.month or 1,
                lessons_count=record.total_lessons,
                hours_count=record.total_hours,
                revenue=record.total_revenue,
                commission=record.total_commission,
                avg_score=record.avg_rating
            )
            summaries.append(summary)
    
    return summaries
