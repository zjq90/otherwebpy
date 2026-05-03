"""
Redis客户端模块
实现高并发抢单的核心功能：
1. Redis连接池管理
2. 库存预扣减(原子操作)
3. 限流功能(滑动窗口算法)
4. 活动状态管理
5. 用户限购检查
6. 黑名单缓存
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from loguru import logger

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis

from app.config import settings


# ==================== Redis连接池管理 ====================

class RedisClient:
    """
    Redis客户端封装类
    
    管理Redis连接池，提供常用的Redis操作封装
    支持异步操作和连接池复用
    """

    # 单例实例
    _instance: Optional["RedisClient"] = None
    _pool: Optional[ConnectionPool] = None

    def __new__(cls) -> "RedisClient":
        """单例模式确保只有一个连接池"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化Redis连接池(仅执行一次)"""
        if self._pool is None:
            self._init_pool()

    def _init_pool(self) -> None:
        """初始化Redis连接池"""
        logger.info("初始化Redis连接池...")

        pool_kwargs: Dict[str, Any] = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
            "socket_connect_timeout": settings.REDIS_SOCKET_TIMEOUT,
            "max_connections": settings.REDIS_CONNECTION_POOL_SIZE,
            "decode_responses": True,  # 自动解码bytes为str
        }

        if settings.REDIS_PASSWORD:
            pool_kwargs["password"] = settings.REDIS_PASSWORD

        self._pool = ConnectionPool(**pool_kwargs)
        logger.info("Redis连接池初始化完成")

    @asynccontextmanager
    async def get_connection(self) -> redis.Redis:
        """
        从连接池获取Redis连接
        
        使用上下文管理器确保连接正确归还
        
        Yields:
            redis.Redis: Redis异步连接对象
        """
        if self._pool is None:
            self._init_pool()

        conn = redis.Redis(connection_pool=self._pool)
        try:
            yield conn
        finally:
            # 异步Redis客户端不需要显式关闭连接
            await conn.aclose()


# 创建全局Redis客户端实例
redis_client = RedisClient()


# ==================== 库存管理 ====================

class InventoryRedisManager:
    """
    Redis库存管理器
    
    实现高并发场景下的库存预扣减
    使用Redis原子操作确保库存一致性
    """

    # Redis键前缀
    STOCK_KEY_PREFIX = "seckill:stock:"
    STOCK_LOCK_PREFIX = "seckill:lock:"
    SOLD_COUNT_PREFIX = "seckill:sold:"

    @classmethod
    async def preload_inventory(cls, product_id: int, stock_count: int) -> bool:
        """
        预加载商品库存到Redis
        
        在抢单活动开始前调用，将库存从数据库同步到Redis
        同时重置相关计数器
        
        Args:
            product_id: 商品ID
            stock_count: 库存数量
            
        Returns:
            bool: 是否成功
        """
        async with redis_client.get_connection() as conn:
            # 使用Redis事务确保原子性
            async with conn.pipeline(transaction=True) as pipe:
                # 设置库存
                stock_key = f"{cls.STOCK_KEY_PREFIX}{product_id}"
                pipe.set(stock_key, stock_count)

                # 重置已售数量
                sold_key = f"{cls.SOLD_COUNT_PREFIX}{product_id}"
                pipe.set(sold_key, 0)

                # 删除可能存在的锁
                lock_key = f"{cls.STOCK_LOCK_PREFIX}{product_id}"
                pipe.delete(lock_key)

                # 设置过期时间(24小时)
                pipe.expire(stock_key, 86400)
                pipe.expire(sold_key, 86400)

                try:
                    await pipe.execute()
                    logger.info(f"商品{product_id}库存预加载成功: {stock_count}件")
                    return True
                except Exception as e:
                    logger.error(f"商品{product_id}库存预加载失败: {str(e)}")
                    return False

    @classmethod
    async def deduct_stock(cls, product_id: int, quantity: int = 1) -> bool:
        """
        扣减库存(原子操作)
        
        使用Redis的DECR命令实现原子扣减
        确保高并发下的库存一致性
        
        Args:
            product_id: 商品ID
            quantity: 扣减数量(默认1)
            
        Returns:
            bool: 是否扣减成功
        """
        stock_key = f"{cls.STOCK_KEY_PREFIX}{product_id}"

        async with redis_client.get_connection() as conn:
            # 检查库存是否存在
            exists = await conn.exists(stock_key)
            if not exists:
                logger.warning(f"商品{product_id}库存未预加载到Redis")
                return False

            # 使用Lua脚本确保原子性: 检查库存 >= 扣减数量后才扣减
            lua_script = """
            local current = tonumber(redis.call('GET', KEYS[1]))
            local quantity = tonumber(ARGV[1])
            
            if current and current >= quantity then
                redis.call('DECRBY', KEYS[1], quantity)
                return 1
            else
                return 0
            end
            """

            result = await conn.eval(lua_script, 1, stock_key, quantity)

            if result == 1:
                # 扣减成功，增加已售计数
                sold_key = f"{cls.SOLD_COUNT_PREFIX}{product_id}"
                await conn.incrby(sold_key, quantity)
                return True
            else:
                logger.debug(f"商品{product_id}库存不足，扣减失败")
                return False

    @classmethod
    async def restore_stock(cls, product_id: int, quantity: int = 1) -> bool:
        """
        归还库存(用于订单取消等场景)
        
        Args:
            product_id: 商品ID
            quantity: 归还数量
            
        Returns:
            bool: 是否成功
        """
        stock_key = f"{cls.STOCK_KEY_PREFIX}{product_id}"
        sold_key = f"{cls.SOLD_COUNT_PREFIX}{product_id}"

        async with redis_client.get_connection() as conn:
            async with conn.pipeline(transaction=True) as pipe:
                # 增加库存
                pipe.incrby(stock_key, quantity)
                # 减少已售计数
                pipe.decrby(sold_key, quantity)

                try:
                    await pipe.execute()
                    logger.debug(f"归还商品{product_id}库存: {quantity}件")
                    return True
                except Exception as e:
                    logger.error(f"归还库存失败: {str(e)}")
                    return False

    @classmethod
    async def get_stock(cls, product_id: int) -> int:
        """
        获取当前库存数量
        
        Args:
            product_id: 商品ID
            
        Returns:
            int: 库存数量(-1表示未找到)
        """
        stock_key = f"{cls.STOCK_KEY_PREFIX}{product_id}"

        async with redis_client.get_connection() as conn:
            stock = await conn.get(stock_key)
            return int(stock) if stock else -1

    @classmethod
    async def get_sold_count(cls, product_id: int) -> int:
        """
        获取已售数量
        
        Args:
            product_id: 商品ID
            
        Returns:
            int: 已售数量
        """
        sold_key = f"{cls.SOLD_COUNT_PREFIX}{product_id}"

        async with redis_client.get_connection() as conn:
            sold = await conn.get(sold_key)
            return int(sold) if sold else 0


# ==================== 限流管理 ====================

class RateLimiter:
    """
    限流器
    
    使用Redis实现滑动窗口限流算法
    支持: IP限流、用户限流、全局限流
    """

    # Redis键前缀
    IP_LIMIT_PREFIX = "rate:ip:"
    USER_LIMIT_PREFIX = "rate:user:"
    GLOBAL_LIMIT_KEY = "rate:global"

    @classmethod
    async def check_ip_limit(cls, ip: str, limit: Optional[int] = None) -> bool:
        """
        检查IP限流
        
        Args:
            ip: IP地址
            limit: 每秒最大请求数(默认使用配置)
            
        Returns:
            bool: 是否允许通过(True=允许, False=限流)
        """
        if limit is None:
            limit = settings.IP_RATE_LIMIT_PER_SECOND

        key = f"{cls.IP_LIMIT_PREFIX}{ip}"
        return await cls._check_sliding_window(key, limit, 1)  # 1秒窗口

    @classmethod
    async def check_user_limit(cls, user_id: int, limit: Optional[int] = None) -> bool:
        """
        检查用户限流
        
        Args:
            user_id: 用户ID
            limit: 每秒最大请求数
            
        Returns:
            bool: 是否允许通过
        """
        if limit is None:
            limit = settings.USER_RATE_LIMIT_PER_SECOND

        key = f"{cls.USER_LIMIT_PREFIX}{user_id}"
        return await cls._check_sliding_window(key, limit, 1)

    @classmethod
    async def check_global_limit(cls, limit: Optional[int] = None) -> bool:
        """
        检查全局限流
        
        Args:
            limit: 每秒最大请求数
            
        Returns:
            bool: 是否允许通过
        """
        if limit is None:
            limit = settings.GLOBAL_RATE_LIMIT_PER_SECOND

        return await cls._check_sliding_window(cls.GLOBAL_LIMIT_KEY, limit, 1)

    @classmethod
    async def _check_sliding_window(cls, key: str, limit: int, window_seconds: int) -> bool:
        """
        滑动窗口限流算法实现
        
        使用Redis的ZSET实现滑动窗口
        1. 移除窗口外的旧请求
        2. 统计窗口内的请求数
        3. 如果未超限则添加当前请求
        
        Args:
            key: Redis键
            limit: 窗口内最大请求数
            window_seconds: 窗口大小(秒)
            
        Returns:
            bool: 是否允许通过
        """
        async with redis_client.get_connection() as conn:
            current_time = datetime.now()
            current_ts = current_time.timestamp() * 1000  # 毫秒
            window_start = current_ts - (window_seconds * 1000)

            # 使用Lua脚本确保原子性
            lua_script = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window_start = tonumber(ARGV[2])
            local current_ts = tonumber(ARGV[3])
            local window_seconds = tonumber(ARGV[4])

            -- 移除窗口外的旧数据
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

            -- 获取当前窗口内的请求数
            local count = redis.call('ZCARD', key)

            if count < limit then
                -- 未超限，添加当前请求
                redis.call('ZADD', key, current_ts, current_ts)
                -- 设置过期时间
                redis.call('EXPIRE', key, window_seconds + 1)
                return 1
            else
                -- 已超限
                return 0
            end
            """

            result = await conn.eval(
                lua_script,
                1,
                key,
                limit,
                window_start,
                current_ts,
                window_seconds
            )

            return result == 1


# ==================== 活动状态管理 ====================

class ActivityManager:
    """
    抢单活动状态管理器
    
    管理活动开始/结束状态
    确保活动未开始时拒绝请求
    """

    # Redis键前缀
    ACTIVITY_STATUS_KEY = "seckill:activity:status"
    ACTIVITY_START_KEY = "seckill:activity:start"
    ACTIVITY_END_KEY = "seckill:activity:end"

    # 活动状态枚举
    STATUS_NOT_STARTED = 0
    STATUS_RUNNING = 1
    STATUS_ENDED = 2

    @classmethod
    async def set_activity_status(cls, product_id: int, status: int) -> bool:
        """
        设置活动状态
        
        Args:
            product_id: 商品ID
            status: 状态(0=未开始, 1=进行中, 2=已结束)
            
        Returns:
            bool: 是否成功
        """
        key = f"{cls.ACTIVITY_STATUS_KEY}:{product_id}"

        async with redis_client.get_connection() as conn:
            result = await conn.set(key, status)
            logger.info(f"商品{product_id}活动状态设置为: {status}")
            return bool(result)

    @classmethod
    async def get_activity_status(cls, product_id: int) -> int:
        """
        获取活动状态
        
        Args:
            product_id: 商品ID
            
        Returns:
            int: 活动状态(-1表示未设置)
        """
        key = f"{cls.ACTIVITY_STATUS_KEY}:{product_id}"

        async with redis_client.get_connection() as conn:
            status = await conn.get(key)
            return int(status) if status else -1

    @classmethod
    async def check_activity_started(cls, product_id: int) -> bool:
        """
        检查活动是否已开始
        
        Args:
            product_id: 商品ID
            
        Returns:
            bool: 是否已开始
        """
        status = await cls.get_activity_status(product_id)
        return status == cls.STATUS_RUNNING

    @classmethod
    async def set_activity_times(
            cls,
            product_id: int,
            start_time: datetime,
            end_time: datetime
    ) -> bool:
        """
        设置活动时间
        
        Args:
            product_id: 商品ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            bool: 是否成功
        """
        start_key = f"{cls.ACTIVITY_START_KEY}:{product_id}"
        end_key = f"{cls.ACTIVITY_END_KEY}:{product_id}"

        async with redis_client.get_connection() as conn:
            async with conn.pipeline(transaction=True) as pipe:
                pipe.set(start_key, start_time.timestamp())
                pipe.set(end_key, end_time.timestamp())
                await pipe.execute()

            logger.info(f"商品{product_id}活动时间已设置: {start_time} ~ {end_time}")
            return True

    @classmethod
    async def is_within_activity_time(cls, product_id: int) -> bool:
        """
        检查当前时间是否在活动时间范围内
        
        Args:
            product_id: 商品ID
            
        Returns:
            bool: 是否在活动时间内
        """
        start_key = f"{cls.ACTIVITY_START_KEY}:{product_id}"
        end_key = f"{cls.ACTIVITY_END_KEY}:{product_id}"

        async with redis_client.get_connection() as conn:
            start_ts = await conn.get(start_key)
            end_ts = await conn.get(end_key)

            if not start_ts or not end_ts:
                # 未设置时间，默认检查状态标记
                return await cls.check_activity_started(product_id)

            current_ts = datetime.now().timestamp()
            start = float(start_ts)
            end = float(end_ts)

            return start <= current_ts <= end


# ==================== 用户限购检查 ====================

class PurchaseLimitManager:
    """
    用户限购管理器
    
    防止单一用户重复购买
    支持按商品和活动设置限购数量
    """

    # Redis键前缀
    USER_PURCHASE_PREFIX = "seckill:purchase:"
    USER_HAS_BUY_PREFIX = "seckill:hasbuy:"

    @classmethod
    async def check_user_purchased(cls, user_id: int, product_id: int) -> bool:
        """
        检查用户是否已购买过该商品
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            bool: 是否已购买
        """
        key = f"{cls.USER_HAS_BUY_PREFIX}{product_id}:{user_id}"

        async with redis_client.get_connection() as conn:
            exists = await conn.exists(key)
            return exists > 0

    @classmethod
    async def get_user_purchase_count(cls, user_id: int, product_id: int) -> int:
        """
        获取用户购买次数
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            int: 购买次数
        """
        key = f"{cls.USER_PURCHASE_PREFIX}{product_id}:{user_id}"

        async with redis_client.get_connection() as conn:
            count = await conn.get(key)
            return int(count) if count else 0

    @classmethod
    async def record_purchase(
            cls,
            user_id: int,
            product_id: int,
            quantity: int = 1,
            expire_hours: int = 24
    ) -> bool:
        """
        记录用户购买
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            quantity: 购买数量
            expire_hours: 记录过期时间(小时)
            
        Returns:
            bool: 是否成功
        """
        purchase_key = f"{cls.USER_PURCHASE_PREFIX}{product_id}:{user_id}"
        hasbuy_key = f"{cls.USER_HAS_BUY_PREFIX}{product_id}:{user_id}"

        async with redis_client.get_connection() as conn:
            async with conn.pipeline(transaction=True) as pipe:
                # 增加购买计数
                pipe.incrby(purchase_key, quantity)
                # 设置购买标记
                pipe.set(hasbuy_key, 1)
                # 设置过期时间
                pipe.expire(purchase_key, expire_hours * 3600)
                pipe.expire(hasbuy_key, expire_hours * 3600)

                try:
                    await pipe.execute()
                    logger.debug(f"记录用户{user_id}购买商品{product_id}: {quantity}件")
                    return True
                except Exception as e:
                    logger.error(f"记录购买失败: {str(e)}")
                    return False

    @classmethod
    async def check_and_record(
            cls,
            user_id: int,
            product_id: int,
            max_limit: int = 1,
            quantity: int = 1
    ) -> tuple[bool, str]:
        """
        检查限购并记录(原子操作)
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            max_limit: 最大限购数量
            quantity: 当前购买数量
            
        Returns:
            tuple: (是否允许, 原因描述)
        """
        # 先检查是否已购买过(限购1件场景)
        if max_limit == 1:
            has_purchased = await cls.check_user_purchased(user_id, product_id)
            if has_purchased:
                return False, "您已购买过该商品，每人限购1件"

        # 获取当前购买数量
        current_count = await cls.get_user_purchase_count(user_id, product_id)

        if current_count + quantity > max_limit:
            return False, f"每人限购{max_limit}件，您已购买{current_count}件"

        # 记录购买
        success = await cls.record_purchase(user_id, product_id, quantity)
        if not success:
            return False, "购买记录失败"

        return True, "限购检查通过"


# ==================== 黑名单缓存 ====================

class BlacklistCache:
    """
    黑名单缓存管理器
    
    使用Redis缓存黑名单，提高查询性能
    支持IP黑名单和用户ID黑名单
    """

    # Redis键前缀
    IP_BLACKLIST_KEY = "blacklist:ip:"
    USER_BLACKLIST_KEY = "blacklist:user:"
    BLACKLIST_SET_KEY = "blacklist:all"

    @classmethod
    async def add_to_blacklist(
            cls,
            target_type: str,
            target_value: str,
            expire_seconds: Optional[int] = None
    ) -> bool:
        """
        添加到黑名单
        
        Args:
            target_type: 类型(ip或user_id)
            target_value: 值(IP地址或用户ID)
            expire_seconds: 过期时间(秒，None表示永久)
            
        Returns:
            bool: 是否成功
        """
        if target_type == "ip":
            key = f"{cls.IP_BLACKLIST_KEY}{target_value}"
        else:
            key = f"{cls.USER_BLACKLIST_KEY}{target_value}"

        async with redis_client.get_connection() as conn:
            await conn.set(key, 1)

            if expire_seconds:
                await conn.expire(key, expire_seconds)

            logger.info(f"添加{target_type}黑名单: {target_value}")
            return True

    @classmethod
    async def check_blacklist(cls, target_type: str, target_value: str) -> bool:
        """
        检查是否在黑名单中
        
        Args:
            target_type: 类型(ip或user_id)
            target_value: 值
            
        Returns:
            bool: 是否在黑名单中(True=在黑名单)
        """
        if target_type == "ip":
            key = f"{cls.IP_BLACKLIST_KEY}{target_value}"
        else:
            key = f"{cls.USER_BLACKLIST_KEY}{target_value}"

        async with redis_client.get_connection() as conn:
            exists = await conn.exists(key)
            return exists > 0

    @classmethod
    async def check_ip_blacklist(cls, ip: str) -> bool:
        """检查IP是否在黑名单"""
        return await cls.check_blacklist("ip", ip)

    @classmethod
    async def check_user_blacklist(cls, user_id: int) -> bool:
        """检查用户是否在黑名单"""
        return await cls.check_blacklist("user_id", str(user_id))

    @classmethod
    async def remove_from_blacklist(cls, target_type: str, target_value: str) -> bool:
        """
        从黑名单移除
        
        Args:
            target_type: 类型
            target_value: 值
            
        Returns:
            bool: 是否成功
        """
        if target_type == "ip":
            key = f"{cls.IP_BLACKLIST_KEY}{target_value}"
        else:
            key = f"{cls.USER_BLACKLIST_KEY}{target_value}"

        async with redis_client.get_connection() as conn:
            await conn.delete(key)
            logger.info(f"移除{target_type}黑名单: {target_value}")
            return True

    @classmethod
    async def batch_load_blacklist(cls, blacklist_items: List[Dict]) -> int:
        """
        批量加载黑名单
        
        用于系统启动时从数据库同步黑名单到Redis
        
        Args:
            blacklist_items: 黑名单列表，每项包含target_type, target_value
            
        Returns:
            int: 加载数量
        """
        count = 0
        async with redis_client.get_connection() as conn:
            async with conn.pipeline(transaction=False) as pipe:
                for item in blacklist_items:
                    target_type = item.get("target_type")
                    target_value = item.get("target_value")

                    if target_type == "ip":
                        key = f"{cls.IP_BLACKLIST_KEY}{target_value}"
                    else:
                        key = f"{cls.USER_BLACKLIST_KEY}{target_value}"

                    pipe.set(key, 1)
                    count += 1

                if count > 0:
                    await pipe.execute()

        logger.info(f"批量加载黑名单完成，共{count}条")
        return count
