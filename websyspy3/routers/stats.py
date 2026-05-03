"""
统计图表路由模块
提供CD趋势、热门CD、分类统计等图表数据
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from utils.database import execute_query
from routers.auth import get_current_user_required, get_current_admin
from config import TEMPLATES_DIR, STATUS_BORROWED, STATUS_RETURNED


# 创建路由
router = APIRouter(tags=["统计图表"])

# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/stats", response_class=HTMLResponse)
async def stats_page(
    request: Request,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示统计图表页面
    """
    return templates.TemplateResponse(
        "stats/index.html",
        {
            "request": request,
            "current_user": current_user
        }
    )


@router.get("/api/stats/overview")
async def get_overview_stats(
    current_user: dict = Depends(get_current_user_required)
) -> JSONResponse:
    """
    获取系统概览统计数据
    """
    # 统计总CD数量
    cd_count = execute_query(
        "SELECT COUNT(*) as count FROM cds",
        fetchone=True
    )
    
    # 统计总分类数量
    category_count = execute_query(
        "SELECT COUNT(*) as count FROM categories",
        fetchone=True
    )
    
    # 统计总用户数量
    user_count = execute_query(
        "SELECT COUNT(*) as count FROM users",
        fetchone=True
    )
    
    # 统计借出中的CD数量
    borrowed_count = execute_query(
        "SELECT COUNT(*) as count FROM borrow_records WHERE status = ?",
        (STATUS_BORROWED,),
        fetchone=True
    )
    
    # 统计已归还的CD数量
    returned_count = execute_query(
        "SELECT COUNT(*) as count FROM borrow_records WHERE status = ?",
        (STATUS_RETURNED,),
        fetchone=True
    )
    
    # 统计可用库存总数
    available_stock = execute_query(
        "SELECT SUM(available_quantity) as total FROM cds",
        fetchone=True
    )
    
    # 统计总库存
    total_stock = execute_query(
        "SELECT SUM(total_quantity) as total FROM cds",
        fetchone=True
    )
    
    return JSONResponse({
        "total_cds": cd_count[0]["count"] if cd_count else 0,
        "total_categories": category_count[0]["count"] if category_count else 0,
        "total_users": user_count[0]["count"] if user_count else 0,
        "borrowed_cds": borrowed_count[0]["count"] if borrowed_count else 0,
        "returned_cds": returned_count[0]["count"] if returned_count else 0,
        "available_stock": available_stock[0]["total"] if available_stock and available_stock[0]["total"] else 0,
        "total_stock": total_stock[0]["total"] if total_stock and total_stock[0]["total"] else 0
    })


@router.get("/api/stats/category-distribution")
async def get_category_distribution(
    current_user: dict = Depends(get_current_user_required)
) -> JSONResponse:
    """
    获取分类分布统计（用于饼图）
    """
    # 查询每个分类的CD数量
    category_stats = execute_query(
        """
        SELECT 
            cat.id,
            cat.name,
            COUNT(c.id) as cd_count,
            SUM(c.total_quantity) as total_quantity,
            SUM(c.available_quantity) as available_quantity
        FROM categories cat
        LEFT JOIN cds c ON cat.id = c.category_id
        GROUP BY cat.id, cat.name
        ORDER BY cd_count DESC
        """
    )
    
    labels = []
    data = []
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ]
    
    if category_stats:
        for i, stat in enumerate(category_stats):
            labels.append(stat["name"])
            data.append(stat["cd_count"])
    
    return JSONResponse({
        "labels": labels,
        "datasets": [{
            "data": data,
            "backgroundColor": colors[:len(labels)],
            "borderWidth": 1
        }]
    })


@router.get("/api/stats/popular-cds")
async def get_popular_cds(
    limit: int = 10,
    current_user: dict = Depends(get_current_user_required)
) -> JSONResponse:
    """
    获取热门CD统计（借阅次数最多的CD，用于柱状图）
    """
    # 查询借阅次数最多的CD
    popular_cds = execute_query(
        """
        SELECT 
            c.id,
            c.title,
            c.artist,
            COUNT(br.id) as borrow_count
        FROM cds c
        LEFT JOIN borrow_records br ON c.id = br.cd_id
        GROUP BY c.id, c.title, c.artist
        ORDER BY borrow_count DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    labels = []
    data = []
    
    if popular_cds:
        for cd in popular_cds:
            # 截断长标题
            title = cd["title"]
            if len(title) > 15:
                title = title[:15] + "..."
            labels.append(f"{title} - {cd['artist']}")
            data.append(cd["borrow_count"])
    
    return JSONResponse({
        "labels": labels,
        "datasets": [{
            "label": "借阅次数",
            "data": data,
            "backgroundColor": [
                'rgba(75, 192, 192, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)'
            ] * 3,
            "borderColor": [
                'rgb(75, 192, 192)',
                'rgb(255, 159, 64)',
                'rgb(153, 102, 255)',
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)'
            ] * 3,
            "borderWidth": 1
        }]
    })


@router.get("/api/stats/borrow-trend")
async def get_borrow_trend(
    days: int = 30,
    current_user: dict = Depends(get_current_user_required)
) -> JSONResponse:
    """
    获取借还趋势统计（用于折线图）
    """
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按日期统计借阅和归还数量
    # 这里使用简化的方式，实际可以使用更复杂的SQL分组
    # 为了简单，我们生成过去N天的日期并统计
    
    labels = []
    borrow_data = []
    return_data = []
    
    # 生成日期标签
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        labels.append(date_str)
        
        # 统计当天的借阅数量
        borrow_count = execute_query(
            """
            SELECT COUNT(*) as count FROM borrow_records 
            WHERE DATE(borrow_date) = ?
            """,
            (date_str,),
            fetchone=True
        )
        borrow_data.append(borrow_count[0]["count"] if borrow_count else 0)
        
        # 统计当天的归还数量
        return_count = execute_query(
            """
            SELECT COUNT(*) as count FROM borrow_records 
            WHERE DATE(return_date) = ?
            """,
            (date_str,),
            fetchone=True
        )
        return_data.append(return_count[0]["count"] if return_count else 0)
    
    return JSONResponse({
        "labels": labels,
        "datasets": [
            {
                "label": "借阅数量",
                "data": borrow_data,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.1)",
                "fill": True,
                "tension": 0.4
            },
            {
                "label": "归还数量",
                "data": return_data,
                "borderColor": "rgb(255, 159, 64)",
                "backgroundColor": "rgba(255, 159, 64, 0.1)",
                "fill": True,
                "tension": 0.4
            }
        ]
    })


@router.get("/api/stats/monthly-stats")
async def get_monthly_stats(
    months: int = 6,
    current_user: dict = Depends(get_current_admin)
) -> JSONResponse:
    """
    获取月度统计数据（仅管理员可访问）
    """
    # 获取最近N个月的统计数据
    end_date = datetime.now()
    
    labels = []
    borrow_data = []
    return_data = []
    
    for i in range(months - 1, -1, -1):
        # 计算月份
        month_date = end_date - timedelta(days=i * 30)
        month_str = month_date.strftime("%Y-%m")
        labels.append(month_str)
        
        # 统计该月的借阅数量
        borrow_count = execute_query(
            """
            SELECT COUNT(*) as count FROM borrow_records 
            WHERE strftime('%Y-%m', borrow_date) = ?
            """,
            (month_str,),
            fetchone=True
        )
        borrow_data.append(borrow_count[0]["count"] if borrow_count else 0)
        
        # 统计该月的归还数量
        return_count = execute_query(
            """
            SELECT COUNT(*) as count FROM borrow_records 
            WHERE return_date IS NOT NULL AND strftime('%Y-%m', return_date) = ?
            """,
            (month_str,),
            fetchone=True
        )
        return_data.append(return_count[0]["count"] if return_count else 0)
    
    return JSONResponse({
        "labels": labels,
        "borrow_data": borrow_data,
        "return_data": return_data
    })


@router.get("/api/stats/user-activity")
async def get_user_activity(
    limit: int = 10,
    current_user: dict = Depends(get_current_admin)
) -> JSONResponse:
    """
    获取用户活跃度统计（仅管理员可访问）
    """
    # 查询借阅次数最多的用户
    active_users = execute_query(
        """
        SELECT 
            u.id,
            u.username,
            u.email,
            COUNT(br.id) as borrow_count,
            COUNT(CASE WHEN br.status = ? THEN 1 END) as returned_count,
            COUNT(CASE WHEN br.status = ? THEN 1 END) as borrowing_count
        FROM users u
        LEFT JOIN borrow_records br ON u.id = br.user_id
        WHERE u.role != 'admin'
        GROUP BY u.id, u.username, u.email
        ORDER BY borrow_count DESC
        LIMIT ?
        """,
        (STATUS_RETURNED, STATUS_BORROWED, limit)
    )
    
    return JSONResponse({
        "users": active_users or []
    })
