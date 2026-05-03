"""
订单路由模块
实现订单查询、订单管理等接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from loguru import logger

from app.models.database import get_async_session
from app.models.models import Order, Product
from app.schemas.schemas import (
    ApiResponse,
    PageResponse,
    OrderResponse,
    OrderCreate,
    OrderListQuery
)
from app.utils.auth import get_current_user_id


router = APIRouter(prefix="/api/orders", tags=["订单管理"])


@router.get("/my", response_model=ApiResponse)
async def get_my_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="订单状态筛选"),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取当前用户的订单列表
    
    需要登录认证
    
    Args:
        page: 页码
        page_size: 每页数量
        status: 订单状态筛选
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 订单列表(分页)
    """
    try:
        # 构建查询
        stmt = select(Order).where(Order.user_id == user_id)
        count_stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        
        # 状态筛选
        if status is not None:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)
        
        # 获取总数
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # 分页查询
        stmt = stmt.order_by(Order.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await session.execute(stmt)
        orders = result.scalars().all()
        
        # 转换为响应模型
        order_responses = []
        for order in orders:
            order_responses.append(
                OrderResponse(
                    id=order.id,
                    order_no=order.order_no,
                    user_id=order.user_id,
                    product_id=order.product_id,
                    product_name=order.product_name,
                    product_code=order.product_code,
                    quantity=order.quantity,
                    unit_price=order.unit_price,
                    total_amount=order.total_amount,
                    status=order.status,
                    status_message=order.status_message,
                    receiver_name=order.receiver_name,
                    receiver_phone=order.receiver_phone,
                    receiver_address=order.receiver_address,
                    pay_time=order.pay_time,
                    pay_method=order.pay_method,
                    created_at=order.created_at,
                    updated_at=order.updated_at
                )
            )
        
        return PageResponse(
            code=200,
            message="获取成功",
            data=[o.model_dump() for o in order_responses],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取订单列表异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.get("/{order_id}", response_model=ApiResponse)
async def get_order_detail(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取订单详情
    
    需要登录认证，只能查看自己的订单
    
    Args:
        order_id: 订单ID
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 订单详情
    """
    try:
        # 查询订单
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if order is None:
            return ApiResponse(
                code=404,
                message="订单不存在",
                data=None
            )
        
        # 验证订单归属
        if order.user_id != user_id:
            # TODO: 管理员可以查看所有订单
            return ApiResponse(
                code=403,
                message="无权查看该订单",
                data=None
            )
        
        # 构建响应
        order_response = OrderResponse(
            id=order.id,
            order_no=order.order_no,
            user_id=order.user_id,
            product_id=order.product_id,
            product_name=order.product_name,
            product_code=order.product_code,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_amount=order.total_amount,
            status=order.status,
            status_message=order.status_message,
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            receiver_address=order.receiver_address,
            pay_time=order.pay_time,
            pay_method=order.pay_method,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=order_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"获取订单详情异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.post("/{order_id}/cancel", response_model=ApiResponse)
async def cancel_order(
    order_id: int,
    reason: str = "用户主动取消",
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    取消订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 取消结果
    """
    try:
        # 查询订单
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if order is None:
            return ApiResponse(
                code=404,
                message="订单不存在",
                data=None
            )
        
        # 验证订单归属
        if order.user_id != user_id:
            return ApiResponse(
                code=403,
                message="无权操作该订单",
                data=None
            )
        
        # 检查订单状态是否可以取消
        if order.status >= 2:
            return ApiResponse(
                code=400,
                message="该订单状态不可取消",
                data=None
            )
        
        # 更新订单状态
        order.status = 3  # 已取消
        order.status_message = f"订单已取消: {reason}"
        order.cancel_reason = reason
        
        await session.commit()
        
        logger.info(f"订单已取消: order_id={order_id}, reason={reason}")
        
        # TODO: 归还库存
        # 这里应该调用库存归还逻辑
        
        return ApiResponse(
            code=200,
            message="订单已取消",
            data=None
        )
        
    except Exception as e:
        logger.error(f"取消订单异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="取消失败，请稍后重试",
            data=None
        )


@router.get("/by-no/{order_no}", response_model=ApiResponse)
async def get_order_by_no(
    order_no: str,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    根据订单号查询订单
    
    Args:
        order_no: 订单编号
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 订单详情
    """
    try:
        stmt = select(Order).where(Order.order_no == order_no)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if order is None:
            return ApiResponse(
                code=404,
                message="订单不存在",
                data=None
            )
        
        # 验证订单归属
        if order.user_id != user_id:
            return ApiResponse(
                code=403,
                message="无权查看该订单",
                data=None
            )
        
        order_response = OrderResponse(
            id=order.id,
            order_no=order.order_no,
            user_id=order.user_id,
            product_id=order.product_id,
            product_name=order.product_name,
            product_code=order.product_code,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_amount=order.total_amount,
            status=order.status,
            status_message=order.status_message,
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            receiver_address=order.receiver_address,
            pay_time=order.pay_time,
            pay_method=order.pay_method,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=order_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"查询订单异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )
