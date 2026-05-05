"""
环保资讯路由模块
包含环保资讯、旧衣知识、公益活动等内容
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime
from typing import Optional, List
import logging

from app.database import get_db
from app.models import EcoArticle, RecycleProcess
from app.schemas.common import success, success_page, error
from app.utils.dependencies import get_current_user, get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/article", tags=["环保资讯"])


@router.get("/categories")
async def get_article_categories():
    """
    获取资讯分类列表
    """
    categories = [
        {"id": 0, "name": "全部", "code": "all"},
        {"id": 1, "name": "环保资讯", "code": "eco_news"},
        {"id": 2, "name": "旧衣知识", "code": "clothing_knowledge"},
        {"id": 3, "name": "公益活动", "code": "public_welfare"},
        {"id": 4, "name": "环保政策", "code": "policy"},
    ]
    
    return success(data=categories)


@router.get("/list")
async def get_article_list(
    category: Optional[str] = Query(None, description="分类名称"),
    is_top: Optional[bool] = Query(None, description="是否置顶"),
    is_hot: Optional[bool] = Query(None, description="是否热门"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Optional[object] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    获取资讯列表
    """
    # 构建查询条件
    conditions = [EcoArticle.status == 1]
    
    if category and category != "全部":
        conditions.append(EcoArticle.category == category)
    
    if is_top is not None:
        conditions.append(EcoArticle.is_top == 1 if is_top else 0)
    
    if is_hot is not None:
        conditions.append(EcoArticle.is_hot == 1 if is_hot else 0)
    
    if keyword:
        conditions.append(
            (EcoArticle.title.contains(keyword)) |
            (EcoArticle.summary.contains(keyword))
        )
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(EcoArticle.id)).where(*conditions)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(EcoArticle)
        .where(*conditions)
        .order_by(
            EcoArticle.is_top.desc(),
            EcoArticle.publish_time.desc(),
            EcoArticle.id.desc()
        )
        .offset(offset)
        .limit(page_size)
    )
    articles = result.scalars().all()
    
    # 转换为字典
    article_list = []
    for article in articles:
        article_dict = article.to_dict()
        # 移除完整内容，列表只显示摘要
        article_dict.pop("content", None)
        article_list.append(article_dict)
    
    return success_page(
        items=article_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{article_id}")
async def get_article_detail(
    article_id: int,
    current_user: Optional[object] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    获取资讯详情
    同时增加浏览量
    """
    result = await db.execute(
        select(EcoArticle).where(
            EcoArticle.id == article_id,
            EcoArticle.status == 1
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        return error(code=404, message="资讯不存在")
    
    # 增加浏览量
    article.view_count += 1
    await db.commit()
    await db.refresh(article)
    
    return success(data=article.to_dict())


@router.post("/{article_id}/like")
async def like_article(
    article_id: int,
    current_user: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    点赞资讯
    """
    result = await db.execute(
        select(EcoArticle).where(
            EcoArticle.id == article_id,
            EcoArticle.status == 1
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        return error(code=404, message="资讯不存在")
    
    # 增加点赞数（简单实现，实际可能需要去重）
    article.like_count += 1
    await db.commit()
    
    return success(data={"like_count": article.like_count}, message="点赞成功")


@router.get("/recycle/process")
async def get_recycle_process(
    db: AsyncSession = Depends(get_db)
):
    """
    获取旧衣回收流程说明
    """
    result = await db.execute(
        select(RecycleProcess).where(
            RecycleProcess.status == 1
        ).order_by(RecycleProcess.step, RecycleProcess.sort_order)
    )
    processes = result.scalars().all()
    
    return success(data=[p.to_dict() for p in processes])


@router.get("/hot")
async def get_hot_articles(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热门资讯
    """
    result = await db.execute(
        select(EcoArticle).where(
            EcoArticle.status == 1,
            EcoArticle.is_hot == 1
        ).order_by(
            EcoArticle.view_count.desc(),
            EcoArticle.publish_time.desc()
        ).limit(limit)
    )
    articles = result.scalars().all()
    
    article_list = []
    for article in articles:
        article_dict = article.to_dict()
        article_dict.pop("content", None)
        article_list.append(article_dict)
    
    return success(data=article_list)


@router.get("/recommendations")
async def get_recommended_articles(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    获取推荐资讯
    """
    result = await db.execute(
        select(EcoArticle).where(
            EcoArticle.status == 1
        ).order_by(
            EcoArticle.is_top.desc(),
            EcoArticle.view_count.desc(),
            EcoArticle.publish_time.desc()
        ).limit(limit)
    )
    articles = result.scalars().all()
    
    article_list = []
    for article in articles:
        article_dict = article.to_dict()
        article_dict.pop("content", None)
        article_list.append(article_dict)
    
    return success(data=article_list)
