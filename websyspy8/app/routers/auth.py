"""
认证路由模块
实现用户注册、登录、登出等认证相关接口
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.database import get_async_session
from app.schemas.schemas import (
    ApiResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse
)
from app.services.user_service import UserService
from app.utils.auth import AuthService, get_current_user_id
from app.config import settings


router = APIRouter(prefix="/api/auth", tags=["认证管理"])


@router.post("/register", response_model=ApiResponse)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    用户注册接口
    
    创建新用户账号
    
    Args:
        user_data: 用户注册数据
        session: 数据库会话
        
    Returns:
        ApiResponse: 注册结果
    """
    try:
        user = await UserService.create(session, user_data)
        user_response = UserService.to_response(user)
        
        logger.info(f"用户注册成功: username={user.username}")
        
        return ApiResponse(
            code=200,
            message="注册成功",
            data=user_response.model_dump()
        )
        
    except ValueError as e:
        logger.warning(f"用户注册失败: {str(e)}")
        return ApiResponse(
            code=400,
            message=str(e),
            data=None
        )
    except Exception as e:
        logger.error(f"用户注册异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="注册失败，请稍后重试",
            data=None
        )


@router.post("/login", response_model=ApiResponse)
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    用户登录接口
    
    验证用户名和密码，返回JWT Token
    
    Args:
        login_data: 登录数据
        session: 数据库会话
        
    Returns:
        ApiResponse: 登录结果(含Token)
    """
    try:
        # 验证用户凭证
        user = await UserService.authenticate(
            session,
            login_data.username,
            login_data.password
        )
        
        if user is None:
            return ApiResponse(
                code=401,
                message="用户名或密码错误",
                data=None
            )
        
        # 生成JWT Token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)},
        )
        
        # 构建响应
        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            user=UserService.to_response(user)
        )
        
        logger.info(f"用户登录成功: username={user.username}")
        
        return ApiResponse(
            code=200,
            message="登录成功",
            data=login_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"用户登录异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="登录失败，请稍后重试",
            data=None
        )


@router.get("/me", response_model=ApiResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    获取当前用户信息
    
    需要登录认证
    
    Args:
        user_id: 当前用户ID(从Token解析)
        session: 数据库会话
        
    Returns:
        ApiResponse: 用户信息
    """
    try:
        user = await UserService.get_by_id(session, user_id)
        
        if user is None:
            return ApiResponse(
                code=404,
                message="用户不存在",
                data=None
            )
        
        user_response = UserService.to_response(user)
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=user_response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"获取用户信息异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取失败，请稍后重试",
            data=None
        )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    user_id: int = Depends(get_current_user_id)
) -> ApiResponse:
    """
    用户登出接口
    
    注意: JWT是无状态的，服务端不需要维护Token状态
    这里主要是记录日志，实际的Token失效需要客户端处理
    
    Args:
        user_id: 当前用户ID
        
    Returns:
        ApiResponse: 登出结果
    """
    logger.info(f"用户登出: user_id={user_id}")
    
    return ApiResponse(
        code=200,
        message="登出成功",
        data=None
    )


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    old_password: str,
    new_password: str,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> ApiResponse:
    """
    修改密码接口
    
    Args:
        old_password: 原密码
        new_password: 新密码
        user_id: 当前用户ID
        session: 数据库会话
        
    Returns:
        ApiResponse: 修改结果
    """
    try:
        # 验证新密码长度
        if len(new_password) < 6:
            return ApiResponse(
                code=400,
                message="新密码长度至少6位",
                data=None
            )
        
        # 执行密码修改
        success = await UserService.change_password(
            session,
            user_id,
            old_password,
            new_password
        )
        
        if not success:
            return ApiResponse(
                code=400,
                message="原密码错误",
                data=None
            )
        
        logger.info(f"密码修改成功: user_id={user_id}")
        
        return ApiResponse(
            code=200,
            message="密码修改成功",
            data=None
        )
        
    except Exception as e:
        logger.error(f"修改密码异常: {str(e)}")
        return ApiResponse(
            code=500,
            message="修改失败，请稍后重试",
            data=None
        )
