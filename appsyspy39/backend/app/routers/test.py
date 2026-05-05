"""
测试工具路由 - 提供测试数据生成和测试辅助接口
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.models import User, Task, Formula, FormulaAdjustment, FeedingRecord, MixingRecord
from app.schemas import SuccessResponse
from app.core.auth import require_role
from app.utils.test_data import populate_test_data

router = APIRouter(prefix="/test", tags=["测试工具"])


@router.post("/generate-data", response_model=SuccessResponse, summary="生成测试数据（管理员功能）")
async def generate_test_data(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    生成测试数据
    
    - 创建测试用户（管理员和操作员）
    - 创建标准配合比配方
    - 创建生产任务（各种状态）
    - 创建投料记录和搅拌记录（包含偏差预警和异常情况）
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    result = await populate_test_data(db)
    
    return SuccessResponse(
        message="测试数据生成成功",
        data=result
    )


@router.post("/clear-data", response_model=SuccessResponse, summary="清空测试数据（管理员功能）")
async def clear_test_data(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    清空测试数据
    
    按依赖顺序删除所有数据：
    1. 搅拌记录
    2. 投料记录
    3. 配方调整记录
    4. 任务
    5. 配方
    6. 用户（保留admin用户）
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    # 按依赖顺序删除
    await db.execute(delete(MixingRecord))
    await db.execute(delete(FeedingRecord))
    await db.execute(delete(FormulaAdjustment))
    await db.execute(delete(Task))
    await db.execute(delete(Formula))
    # 保留admin用户
    await db.execute(delete(User).where(User.username != "admin"))
    
    await db.commit()
    
    return SuccessResponse(message="测试数据已清空")


@router.get("/summary", summary="获取数据概览")
async def get_data_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    获取数据库数据概览
    
    统计各表数据数量
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        dict: 数据统计
    """
    # 统计各表数据量
    users_count = await db.execute(select(func_count(User.id)))
    users_count = users_count.scalar() or 0
    
    tasks_count = await db.execute(select(func_count(Task.id)))
    tasks_count = tasks_count.scalar() or 0
    
    formulas_count = await db.execute(select(func_count(Formula.id)))
    formulas_count = formulas_count.scalar() or 0
    
    feeding_count = await db.execute(select(func_count(FeedingRecord.id)))
    feeding_count = feeding_count.scalar() or 0
    
    mixing_count = await db.execute(select(func_count(MixingRecord.id)))
    mixing_count = mixing_count.scalar() or 0
    
    # 按状态统计任务
    from sqlalchemy import func
    task_status_result = await db.execute(
        select(Task.status, func.count(Task.id)).group_by(Task.status)
    )
    task_status_stats = {row[0]: row[1] for row in task_status_result.all()}
    
    # 预警统计
    warning_result = await db.execute(
        select(
            FeedingRecord.has_warning,
            FeedingRecord.warning_level,
            func.count(FeedingRecord.id)
        ).group_by(FeedingRecord.has_warning, FeedingRecord.warning_level)
    )
    warning_stats = {}
    for row in warning_result.all():
        key = f"{row[0]}_{row[1]}" if row[1] else str(row[0])
        warning_stats[key] = row[2]
    
    return {
        "summary": {
            "users": users_count,
            "tasks": tasks_count,
            "formulas": formulas_count,
            "feeding_records": feeding_count,
            "mixing_records": mixing_count
        },
        "task_status": task_status_stats,
        "warning_stats": warning_stats
    }


@router.get("/test-users", summary="获取测试账号信息")
async def get_test_users(
    db: AsyncSession = Depends(get_db)
):
    """
    获取测试账号信息（用于功能测试）
    
    不需要登录即可访问，方便测试时查看账号
    
    Returns:
        dict: 测试账号信息
    """
    return {
        "test_accounts": [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "description": "系统管理员，可以管理用户、配方、任务等"
            },
            {
                "username": "operator1",
                "password": "123456",
                "role": "operator",
                "description": "张操作员，可以接单、投料、搅拌操作"
            },
            {
                "username": "operator2",
                "password": "123456",
                "role": "operator",
                "description": "李操作员，可以接单、投料、搅拌操作"
            }
        ],
        "api_docs": [
            "Swagger UI: http://localhost:8000/docs",
            "ReDoc: http://localhost:8000/redoc",
            "OpenAPI JSON: http://localhost:8000/openapi.json"
        ]
    }


# 辅助函数
from sqlalchemy import func
from sqlalchemy.sql import func as func_count
