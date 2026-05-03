"""
用户服务模块
处理用户注册、登录、查询等业务逻辑
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse
from app.utils.auth import AuthService


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑处理
    """

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象或None
        """
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            session: 数据库会话
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象或None
        """
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            session: 数据库会话
            user_data: 用户创建数据
            
        Returns:
            User: 新创建的用户对象
            
        Raises:
            ValueError: 用户名已存在时抛出
        """
        # 检查用户名是否已存在
        existing = await UserService.get_by_username(session, user_data.username)
        if existing:
            raise ValueError("用户名已存在")

        # 创建密码哈希
        password_hash = AuthService.get_password_hash(user_data.password)

        # 创建用户对象
        user = User(
            username=user_data.username,
            password_hash=password_hash,
            email=user_data.email,
            phone=user_data.phone,
            is_active=True,
            is_admin=False
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        logger.info(f"用户创建成功: username={user.username}")
        return user

    @staticmethod
    async def authenticate(session: AsyncSession, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        验证用户名和密码是否匹配
        
        Args:
            session: 数据库会话
            username: 用户名
            password: 明文密码
            
        Returns:
            Optional[User]: 认证成功返回用户对象，失败返回None
        """
        # 获取用户
        user = await UserService.get_by_username(session, username)

        if user is None:
            logger.warning(f"登录失败: 用户不存在 - username={username}")
            return None

        # 验证密码
        if not AuthService.verify_password(password, user.password_hash):
            logger.warning(f"登录失败: 密码错误 - username={username}")
            return None

        # 检查用户是否激活
        if not user.is_active:
            logger.warning(f"登录失败: 用户已禁用 - username={username}")
            return None

        # 更新登录信息
        user.last_login_at = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        await session.commit()

        logger.info(f"用户登录成功: username={username}")
        return user

    @staticmethod
    async def update(session: AsyncSession, user_id: int, update_data: dict) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            update_data: 更新数据字典
            
        Returns:
            Optional[User]: 更新后的用户对象
        """
        user = await UserService.get_by_id(session, user_id)
        if user is None:
            return None

        # 过滤不允许更新的字段
        allowed_fields = ['email', 'phone']
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        logger.info(f"用户信息更新成功: user_id={user_id}")
        return user

    @staticmethod
    async def change_password(
            session: AsyncSession,
            user_id: int,
            old_password: str,
            new_password: str
    ) -> bool:
        """
        修改密码
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            old_password: 原密码
            new_password: 新密码
            
        Returns:
            bool: 是否成功
        """
        user = await UserService.get_by_id(session, user_id)
        if user is None:
            return False

        # 验证原密码
        if not AuthService.verify_password(old_password, user.password_hash):
            logger.warning(f"密码修改失败: 原密码错误 - user_id={user_id}")
            return False

        # 更新密码
        user.password_hash = AuthService.get_password_hash(new_password)
        await session.commit()

        logger.info(f"密码修改成功: user_id={user_id}")
        return True

    @staticmethod
    async def get_list(
            session: AsyncSession,
            page: int = 1,
            page_size: int = 10,
            is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """
        获取用户列表(分页)
        
        Args:
            session: 数据库会话
            page: 页码
            page_size: 每页数量
            is_active: 激活状态筛选
            
        Returns:
            tuple: (用户列表, 总记录数)
        """
        # 构建查询条件
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        # 获取总数
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 分页查询
        stmt = stmt.order_by(User.id.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await session.execute(stmt)
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    def to_response(user: User) -> UserResponse:
        """
        将User模型转换为UserResponse
        
        Args:
            user: User模型对象
            
        Returns:
            UserResponse: 用户响应对象
        """
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
