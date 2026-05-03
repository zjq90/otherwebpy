"""
抢单路由模块
实现抢单核心接口：活动预加载、抢单执行、状态查询等
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.database import get_async_session
from app.schemas.schemas import (
    ApiResponse,
    SeckillRequest,
    SeckillResponse,
    SeckillStatusResponse,
    SeckillConfigCreate,
    SeckillConfigResponse
)
from app.services.seckill_service import SeckillService, SeckillPreloadService
from app.utils.auth import get_current_user_id
from app.middlewares.security_middleware import RateLimitMiddleware
from app.config import settings


router = APIRouter(prefix="/api/seckill", tags=["抢单管理"])


@router.post("/execute", response_model=ApiResponse)
async def execute_seckill(
    request: Request,
    seckill_request: SeckillRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    执行抢单(核心接口)
    
    完整抢单流程：
    1. 检查活动状态
    2. Redis预扣库存
    3. 用户限购检查
    4. 生成订单信息
    5. 异步写入数据库
    
    需要登录认证
    
    Args:
        request: FastAPI请求对象
        seckill_request: 抢单请求数据
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 抢单结果
    """
    try:
        # 获取客户端IP
        client_ip = RateLimitMiddleware._get_client_ip(request)
        
        # 执行抢单核心流程
        success, message, order_no = await SeckillService.execute_seckill(
            session=session,
            user_id=user_id,
            request=seckill_request,
            client_ip=client_ip
        )
        
        if success and order_no:
            # 抢单成功，准备订单数据并提交到异步队列
            try:
                # 准备订单数据
                order_data = await SeckillService.prepare_order_data(
                    session=session,
                    user_id=user_id,
                    product_id=seckill_request.product_id,
                    quantity=seckill_request.quantity,
                    order_no=order_no
                )
                
                # TODO: 这里可以提交到异步队列
                # 简化处理：直接创建订单(实际高并发场景应使用异步队列)
                from app.models.models import Order
                order = Order(**order_data)
                session.add(order)
                await session.commit()
                
                logger.info(f"抢单成功: user_id={user_id}, product_id={seckill_request.product_id}, order_no={order_no}")
                
            except Exception as e:
                logger.error(f"订单创建失败，执行回滚: {str(e)}")
                # 回滚抢单
                await SeckillService.rollback_seckill(
                    user_id=user_id,
                    product_id=seckill_request.product_id,
                    quantity=seckill_request.quantity,
                    order_no=order_no
                )
                return ApiResponse(
                    code=500,
                    message="系统繁忙，请稍后重试",
                    data=None
                )
        
        # 构建响应
        seckill_response = SeckillResponse(
            success=success,
            order_no=order_no if success else None,
            message=message
        )
        
        return ApiResponse(
            code=200 if success else 400,
            message=message,
            data=seckill_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"抢单执行异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="系统繁忙，请稍后重试",
            data=None
        )


@router.get("/status/{product_id}", response_model=ApiResponse)
async def get_seckill_status(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    查询抢单活动状态
    
    无需登录认证，用于前端展示活动状态和库存
    
    Args:
        product_id: 商品ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 活动状态信息
    """
    try:
        status_data = await SeckillService.check_seckill_status(
            session=session,
            product_id=product_id
        )
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"获取活动状态异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.post("/preload", response_model=ApiResponse)
async def preload_activity(
    product_id: int,
    seckill_stock: int,
    auto_start: bool = False,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    预加载抢单活动(管理接口)
    
    将库存从数据库预加载到Redis，设置活动状态
    需要管理员权限(简化处理：已登录用户即可)
    
    Args:
        product_id: 商品ID
        seckill_stock: 秒杀库存数量
        auto_start: 是否立即开始活动
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 预加载结果
    """
    try:
        # TODO: 检查用户是否为管理员
        # 简化处理：所有已登录用户都可以预加载
        
        # 预加载活动
        success, message = await SeckillPreloadService.preload_activity(
            session=session,
            product_id=product_id,
            seckill_stock=seckill_stock,
            auto_start=auto_start
        )
        
        if success:
            # 获取预加载状态
            status = await SeckillPreloadService.get_preload_status(product_id)
            return ApiResponse(
                code=200,
                message=message,
                data=status
            )
        else:
            return ApiResponse(
                code=400,
                message=message,
                data=None
            )
            
    except Exception as e:
        logger.error(f"预加载活动异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="预加载失败，请稍后重试",
            data=None
        )


@router.post("/start/{product_id}", response_model=ApiResponse)
async def start_activity(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
) -> ApiResponse:
    """
    开始抢单活动(管理接口)
    
    将活动状态设置为"进行中"
    
    Args:
        product_id: 商品ID
        user_id: 当前用户ID
        
    Returns:
        ApiResponse: 操作结果
    """
    try:
        success = await SeckillPreloadService.start_activity(product_id)
        
        if success:
            status = await SeckillPreloadService.get_preload_status(product_id)
            return ApiResponse(
                code=200,
                message="活动已开始",
                data=status
            )
        else:
            return ApiResponse(
                code=400,
                message="活动开始失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"开始活动异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="操作失败，请稍后重试",
            data=None
        )


@router.post("/end/{product_id}", response_model=ApiResponse)
async def end_activity(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
) -> ApiResponse:
    """
    结束抢单活动(管理接口)
    
    将活动状态设置为"已结束"
    
    Args:
        product_id: 商品ID
        user_id: 当前用户ID
        
    Returns:
        ApiResponse: 操作结果
    """
    try:
        success = await SeckillPreloadService.end_activity(product_id)
        
        if success:
            status = await SeckillPreloadService.get_preload_status(product_id)
            return ApiResponse(
                code=200,
                message="活动已结束",
                data=status
            )
        else:
            return ApiResponse(
                code=400,
                message="活动结束失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"结束活动异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="操作失败，请稍后重试",
            data=None
        )


@router.get("/preload-status/{product_id}", response_model=ApiResponse)
async def get_preload_status(
    product_id: int,
    user_id: int = Depends(get_current_user_id)
) -> ApiResponse:
    """
    获取预加载状态(管理接口)
    
    Args:
        product_id: 商品ID
        user_id: 当前用户ID
        
    Returns:
        ApiResponse: 预加载状态
    """
    try:
        status = await SeckillPreloadService.get_preload_status(product_id)
        return ApiResponse(
            code=200,
            message="获取成功",
            data=status
        )
    except Exception as e:
        logger.error(f"获取预加载状态异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )
