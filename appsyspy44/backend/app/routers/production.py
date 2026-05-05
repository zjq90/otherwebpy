from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.production import (
    ProductionDataCreate, ProductionDataUpdate, ProductionDataResponse,
    ProductionTaskCreate, ProductionTaskUpdate, ProductionTaskResponse,
    ProductionReportResponse, ChartResponse
)
from app.crud.production_crud import ProductionDataCRUD, ProductionTaskCRUD

router = APIRouter()

@router.get("/production-data", response_model=List[ProductionDataResponse])
def get_production_data_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ProductionDataCRUD.get_all(db, skip=skip, limit=limit)

@router.get("/production-data/{data_id}", response_model=ProductionDataResponse)
def get_production_data(data_id: int, db: Session = Depends(get_db)):
    data = ProductionDataCRUD.get_by_id(db, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="生产数据不存在")
    return data

@router.post("/production-data", response_model=ProductionDataResponse)
def create_production_data(data: ProductionDataCreate, db: Session = Depends(get_db)):
    return ProductionDataCRUD.create(db, data)

@router.put("/production-data/{data_id}", response_model=ProductionDataResponse)
def update_production_data(data_id: int, data: ProductionDataUpdate, db: Session = Depends(get_db)):
    db_data = ProductionDataCRUD.update(db, data_id, data)
    if not db_data:
        raise HTTPException(status_code=404, detail="生产数据不存在")
    return db_data

@router.delete("/production-data/{data_id}")
def delete_production_data(data_id: int, db: Session = Depends(get_db)):
    success = ProductionDataCRUD.delete(db, data_id)
    if not success:
        raise HTTPException(status_code=404, detail="生产数据不存在")
    return {"message": "删除成功"}

@router.get("/report/daily", response_model=ProductionReportResponse)
def get_daily_report(
    report_date: date = Query(..., description="报告日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    return ProductionDataCRUD.get_daily_report(db, report_date)

@router.get("/report/weekly", response_model=ProductionReportResponse)
def get_weekly_report(
    week_start: date = Query(..., description="周开始日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    return ProductionDataCRUD.get_weekly_report(db, week_start)

@router.get("/report/monthly", response_model=ProductionReportResponse)
def get_monthly_report(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    db: Session = Depends(get_db)
):
    return ProductionDataCRUD.get_monthly_report(db, year, month)

@router.get("/chart/production", response_model=ChartResponse)
def get_production_chart(
    chart_type: str = Query("bar", description="图表类型：bar或line"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    data = ProductionDataCRUD.get_by_date_range(db, start_date, end_date)
    
    daily_stats = {}
    for d in data:
        day_key = d.production_date.isoformat()
        if day_key not in daily_stats:
            daily_stats[day_key] = {
                "actual": 0,
                "qualified": 0,
                "planned": 0
            }
        daily_stats[day_key]["actual"] += d.actual_quantity
        daily_stats[day_key]["qualified"] += d.qualified_quantity
        daily_stats[day_key]["planned"] += d.planned_quantity
    
    sorted_dates = sorted(daily_stats.keys())
    
    x_axis_data = [d for d in sorted_dates]
    actual_data = [daily_stats[d]["actual"] for d in sorted_dates]
    qualified_data = [daily_stats[d]["qualified"] for d in sorted_dates]
    planned_data = [daily_stats[d]["planned"] for d in sorted_dates]
    
    return {
        "chart_type": chart_type,
        "title": "产量统计图表",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "计划产量", "data": planned_data, "type": chart_type},
            {"name": "实际产量", "data": actual_data, "type": chart_type},
            {"name": "合格产量", "data": qualified_data, "type": chart_type}
        ]
    }

@router.get("/chart/completion-rate", response_model=ChartResponse)
def get_completion_rate_chart(
    chart_type: str = Query("line", description="图表类型：line或bar"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    data = ProductionDataCRUD.get_by_date_range(db, start_date, end_date)
    
    daily_stats = {}
    for d in data:
        day_key = d.production_date.isoformat()
        if day_key not in daily_stats:
            daily_stats[day_key] = {
                "actual": 0,
                "planned": 0
            }
        daily_stats[day_key]["actual"] += d.actual_quantity
        daily_stats[day_key]["planned"] += d.planned_quantity
    
    sorted_dates = sorted(daily_stats.keys())
    
    x_axis_data = [d for d in sorted_dates]
    completion_rates = []
    for d in sorted_dates:
        stats = daily_stats[d]
        rate = 0.0
        if stats["planned"] > 0:
            rate = round((stats["actual"] / stats["planned"]) * 100, 2)
        completion_rates.append(rate)
    
    return {
        "chart_type": chart_type,
        "title": "任务完成率趋势",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "完成率(%)", "data": completion_rates, "type": chart_type}
        ]
    }

@router.get("/tasks", response_model=List[ProductionTaskResponse])
def get_tasks_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ProductionTaskCRUD.get_all(db, skip=skip, limit=limit)

@router.get("/tasks/{task_id}", response_model=ProductionTaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = ProductionTaskCRUD.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@router.post("/tasks", response_model=ProductionTaskResponse)
def create_task(task: ProductionTaskCreate, db: Session = Depends(get_db)):
    existing = ProductionTaskCRUD.get_by_task_no(db, task.task_no)
    if existing:
        raise HTTPException(status_code=400, detail="任务编号已存在")
    return ProductionTaskCRUD.create(db, task)

@router.put("/tasks/{task_id}", response_model=ProductionTaskResponse)
def update_task(task_id: int, task: ProductionTaskUpdate, db: Session = Depends(get_db)):
    db_task = ProductionTaskCRUD.update(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = ProductionTaskCRUD.delete(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "删除成功"}
