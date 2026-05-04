"""
仪表盘统计API路由
提供首页统计数据接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/api/dashboard",
    tags=["仪表盘统计"]
)


@router.get("/stats", response_model=schemas.DashboardStats, summary="获取首页统计数据")
def get_stats(db: Session = Depends(get_db)):
    """
    获取系统首页统计数据，包括：
    - 项目总数
    - 房产总数
    - 业主总数
    - 各状态房产数量（空置、出租、自住）
    """
    return crud.get_dashboard_stats(db)
