"""
财务记录管理路由
处理财务记录的增删改查和财务报表
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from database import get_db
from models import FinancialRecord, User
from schemas import (
    FinancialRecordCreate, FinancialRecordUpdate, FinancialRecordResponse,
    FinancialReportRequest, APIResponse, PaginatedResponse
)
from routers.auth import get_current_active_user
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由
router = APIRouter(prefix="/financial", tags=["财务管理"])


@router.get("", response_model=PaginatedResponse)
async def get_financial_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量"),
    record_type: Optional[str] = Query(None, description="类型：income/expense"),
    category: Optional[str] = Query(None, description="分类筛选"),
    year: Optional[int] = Query(None, description="年份筛选"),
    quarter: Optional[int] = Query(None, description="季度筛选"),
    month: Optional[int] = Query(None, description="月份筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取财务记录列表
    支持分页和筛选
    """
    # 构建查询
    query = select(FinancialRecord)
    
    # 筛选条件
    if record_type:
        query = query.where(FinancialRecord.record_type == record_type)
    if category:
        query = query.where(FinancialRecord.category == category)
    if year:
        query = query.where(FinancialRecord.year == year)
    if quarter:
        query = query.where(FinancialRecord.quarter == quarter)
    if month:
        query = query.where(FinancialRecord.month == month)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(FinancialRecord.record_date.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 转换为响应模型
    record_responses = [FinancialRecordResponse.model_validate(record) for record in records]
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data=record_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{record_id}", response_model=FinancialRecordResponse)
async def get_financial_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个财务记录详情
    """
    query = select(FinancialRecord).where(FinancialRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="财务记录不存在"
        )
    
    return record


@router.post("", response_model=APIResponse)
async def create_financial_record(
    record_data: FinancialRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新财务记录
    """
    data = record_data.model_dump()
    
    # 自动计算年份、月份、季度
    record_date = data["record_date"]
    data["year"] = record_date.year
    data["month"] = record_date.month
    data["quarter"] = (record_date.month - 1) // 3 + 1
    
    # 创建新记录
    new_record = FinancialRecord(**data)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return APIResponse(
        success=True,
        message="创建成功",
        data={"record_id": new_record.id}
    )


@router.put("/{record_id}", response_model=APIResponse)
async def update_financial_record(
    record_id: int,
    record_data: FinancialRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新财务记录
    """
    query = select(FinancialRecord).where(FinancialRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="财务记录不存在"
        )
    
    # 更新字段
    update_data = record_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    
    # 如果更新了日期，重新计算年份、月份、季度
    if "record_date" in update_data:
        record.year = record.record_date.year
        record.month = record.record_date.month
        record.quarter = (record.record_date.month - 1) // 3 + 1
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message="更新成功"
    )


@router.delete("/{record_id}", response_model=APIResponse)
async def delete_financial_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除财务记录
    """
    query = select(FinancialRecord).where(FinancialRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="财务记录不存在"
        )
    
    await db.delete(record)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="删除成功"
    )


@router.post("/report", response_model=APIResponse)
async def generate_financial_report(
    report_request: FinancialReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成财务报表
    收入、支出、利润汇总，支持多维度对比
    """
    # 构建查询条件
    query = select(FinancialRecord)
    
    conditions = []
    if report_request.record_type:
        conditions.append(FinancialRecord.record_type == report_request.record_type)
    if report_request.category:
        conditions.append(FinancialRecord.category == report_request.category)
    if report_request.year:
        conditions.append(FinancialRecord.year == report_request.year)
    if report_request.quarter:
        conditions.append(FinancialRecord.quarter == report_request.quarter)
    if report_request.month:
        conditions.append(FinancialRecord.month == report_request.month)
    if report_request.start_date:
        conditions.append(FinancialRecord.record_date >= report_request.start_date)
    if report_request.end_date:
        conditions.append(FinancialRecord.record_date <= report_request.end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(FinancialRecord.record_date)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 统计数据
    total_records = len(records)
    
    # 收入统计
    income_records = [r for r in records if r.record_type == "income"]
    total_income = sum(r.amount for r in income_records)
    
    # 支出统计
    expense_records = [r for r in records if r.record_type == "expense"]
    total_expense = sum(r.amount for r in expense_records)
    
    # 利润
    total_profit = total_income - total_expense
    
    # 按类型统计
    by_type = {
        "income": {"count": len(income_records), "total": round(total_income, 2)},
        "expense": {"count": len(expense_records), "total": round(total_expense, 2)}
    }
    
    # 按分类统计
    by_category = {}
    for r in records:
        category = r.category
        if category not in by_category:
            by_category[category] = {
                "count": 0,
                "income": 0.0,
                "expense": 0.0,
                "total": 0.0
            }
        by_category[category]["count"] += 1
        if r.record_type == "income":
            by_category[category]["income"] += r.amount
            by_category[category]["total"] += r.amount
        else:
            by_category[category]["expense"] += r.amount
            by_category[category]["total"] -= r.amount
    
    # 按年份统计
    by_year = {}
    for r in records:
        year = str(r.year)
        if year not in by_year:
            by_year[year] = {
                "count": 0,
                "income": 0.0,
                "expense": 0.0,
                "profit": 0.0
            }
        by_year[year]["count"] += 1
        if r.record_type == "income":
            by_year[year]["income"] += r.amount
            by_year[year]["profit"] += r.amount
        else:
            by_year[year]["expense"] += r.amount
            by_year[year]["profit"] -= r.amount
    
    # 按季度统计
    by_quarter = {}
    for r in records:
        key = f"{r.year}Q{r.quarter}"
        if key not in by_quarter:
            by_quarter[key] = {
                "count": 0,
                "income": 0.0,
                "expense": 0.0,
                "profit": 0.0
            }
        by_quarter[key]["count"] += 1
        if r.record_type == "income":
            by_quarter[key]["income"] += r.amount
            by_quarter[key]["profit"] += r.amount
        else:
            by_quarter[key]["expense"] += r.amount
            by_quarter[key]["profit"] -= r.amount
    
    # 利润率
    profit_rate = round((total_profit / total_income) * 100, 2) if total_income > 0 else 0
    
    return APIResponse(
        success=True,
        message="报表生成成功",
        data={
            "summary": {
                "total_records": total_records,
                "total_income": round(total_income, 2),
                "total_expense": round(total_expense, 2),
                "total_profit": round(total_profit, 2),
                "profit_rate": profit_rate
            },
            "by_type": by_type,
            "by_category": by_category,
            "by_year": by_year,
            "by_quarter": by_quarter,
            "records": [
                {
                    "id": r.id,
                    "record_date": str(r.record_date),
                    "record_type": r.record_type,
                    "category": r.category,
                    "amount": r.amount,
                    "description": r.description,
                    "year": r.year,
                    "month": r.month,
                    "quarter": r.quarter
                }
                for r in records
            ]
        }
    )


@router.get("/statistics/summary", response_model=APIResponse)
async def get_financial_statistics(
    year: Optional[int] = Query(None, description="年份，不指定则统计所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取财务统计摘要
    """
    query = select(FinancialRecord)
    if year:
        query = query.where(FinancialRecord.year == year)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 收入统计
    income_records = [r for r in records if r.record_type == "income"]
    total_income = sum(r.amount for r in income_records)
    
    # 支出统计
    expense_records = [r for r in records if r.record_type == "expense"]
    total_expense = sum(r.amount for r in expense_records)
    
    # 利润
    total_profit = total_income - total_expense
    
    # 按月份统计
    monthly_stats = {}
    for r in records:
        month_key = f"{r.year}-{r.month:02d}"
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {"income": 0.0, "expense": 0.0, "profit": 0.0}
        if r.record_type == "income":
            monthly_stats[month_key]["income"] += r.amount
            monthly_stats[month_key]["profit"] += r.amount
        else:
            monthly_stats[month_key]["expense"] += r.amount
            monthly_stats[month_key]["profit"] -= r.amount
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={
            "total_records": len(records),
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "total_profit": round(total_profit, 2),
            "profit_rate": round((total_profit / total_income) * 100, 2) if total_income > 0 else 0,
            "monthly_stats": dict(sorted(monthly_stats.items()))
        }
    )


@router.get("/categories/income", response_model=APIResponse)
async def get_income_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有收入分类
    """
    query = select(FinancialRecord.category).where(
        FinancialRecord.record_type == "income"
    ).distinct().order_by(FinancialRecord.category)
    
    result = await db.execute(query)
    categories = [row[0] for row in result.all()]
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={"categories": categories}
    )


@router.get("/categories/expense", response_model=APIResponse)
async def get_expense_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有支出分类
    """
    query = select(FinancialRecord.category).where(
        FinancialRecord.record_type == "expense"
    ).distinct().order_by(FinancialRecord.category)
    
    result = await db.execute(query)
    categories = [row[0] for row in result.all()]
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={"categories": categories}
    )
