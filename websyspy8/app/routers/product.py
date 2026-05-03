"""
商品路由模块
实现商品CRUD、库存查询等接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.database import get_async_session
from app.models.models import Product, Inventory
from app.schemas.schemas import (
    ApiResponse,
    PageResponse,
    ProductCreate,
    ProductResponse,
    InventoryResponse
)
from app.services.product_service import ProductService, InventoryService
from app.utils.auth import get_current_user_id


router = APIRouter(prefix="/api/products", tags=["商品管理"])


@router.get("", response_model=ApiResponse)
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否上架"),
    category: Optional[str] = Query(None, description="分类筛选"),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取商品列表(分页)
    
    无需登录认证，用于商品展示
    
    Args:
        page: 页码
        page_size: 每页数量
        is_active: 是否上架筛选
        category: 分类筛选
        session: 数据库会话
        
    Returns:
        ApiResponse: 商品列表(分页)
    """
    try:
        products, total = await ProductService.get_list(
            session=session,
            page=page,
            page_size=page_size,
            is_active=is_active,
            category=category
        )
        
        # 转换为响应模型
        product_responses = [
            ProductService.to_response(p) for p in products
        ]
        
        return PageResponse(
            code=200,
            message="获取成功",
            data=[p.model_dump() for p in product_responses],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取商品列表异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.get("/{product_id}", response_model=ApiResponse)
async def get_product_detail(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取商品详情
    
    无需登录认证
    
    Args:
        product_id: 商品ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 商品详情
    """
    try:
        product = await ProductService.get_by_id(session, product_id)
        
        if product is None:
            return ApiResponse(
                code=404,
                message="商品不存在",
                data=None
            )
        
        product_response = ProductService.to_response(product)
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=product_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"获取商品详情异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.post("", response_model=ApiResponse)
async def create_product(
    product_data: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    创建商品(管理接口)
    
    需要登录认证
    
    Args:
        product_data: 商品创建数据
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 创建结果
    """
    try:
        # TODO: 检查用户是否为管理员
        # 简化处理：所有已登录用户都可以创建商品
        
        product = await ProductService.create(session, product_data)
        product_response = ProductService.to_response(product)
        
        logger.info(f"商品创建成功: product_code={product.product_code}")
        
        return ApiResponse(
            code=200,
            message="创建成功",
            data=product_response.model_dump()
        )
        
    except ValueError as e:
        logger.warning(f"商品创建失败: {str(e)}")
        return ApiResponse(
            code=400,
            message=str(e),
            data=None
        )
    except Exception as e:
        logger.error(f"商品创建异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="创建失败，请稍后重试",
            data=None
        )


@router.put("/{product_id}", response_model=ApiResponse)
async def update_product(
    product_id: int,
    update_data: dict,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    更新商品(管理接口)
    
    Args:
        product_id: 商品ID
        update_data: 更新数据
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 更新结果
    """
    try:
        product = await ProductService.update(session, product_id, update_data)
        
        if product is None:
            return ApiResponse(
                code=404,
                message="商品不存在",
                data=None
            )
        
        product_response = ProductService.to_response(product)
        
        return ApiResponse(
            code=200,
            message="更新成功",
            data=product_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"商品更新异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="更新失败，请稍后重试",
            data=None
        )


@router.delete("/{product_id}", response_model=ApiResponse)
async def delete_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    删除商品(软删除，设置为下架)(管理接口)
    
    Args:
        product_id: 商品ID
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 删除结果
    """
    try:
        success = await ProductService.delete(session, product_id)
        
        if not success:
            return ApiResponse(
                code=404,
                message="商品不存在",
                data=None
            )
        
        return ApiResponse(
            code=200,
            message="商品已下架",
            data=None
        )
        
    except Exception as e:
        logger.error(f"商品删除异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="删除失败，请稍后重试",
            data=None
        )


@router.get("/{product_id}/inventory", response_model=ApiResponse)
async def get_inventory(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取商品库存信息(管理接口)
    
    Args:
        product_id: 商品ID
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 库存信息
    """
    try:
        inventory = await InventoryService.get_by_product_id(session, product_id)
        
        if inventory is None:
            return ApiResponse(
                code=404,
                message="库存记录不存在",
                data=None
            )
        
        inventory_response = InventoryService.to_response(inventory)
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=inventory_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"获取库存信息异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )
