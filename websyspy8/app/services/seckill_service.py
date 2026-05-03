"""
抢单核心服务模块
实现高并发抢单的核心业务逻辑：
1. 活动状态检查
2. Redis预扣库存
3. 用户限购检查
4. 异步订单写入
"""
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.models.models import Order, Product, SeckillConfig
from app.schemas.schemas import SeckillRequest, SeckillResponse
from app.utils.redis_client import (
    InventoryRedisManager,
    ActivityManager,
    PurchaseLimitManager,
    RateLimiter,
    BlacklistCache
)
from app.services.product_service import ProductService, SeckillConfigService


class SeckillService:
    """
    抢单核心服务类
    
    实现高并发抢单的完整流程：
    1. 前置检查(活动状态、用户限流、黑名单等)
    2. Redis预扣库存
    3. 用户限购检查
    4. 生成订单并异步写入数据库
    """

    @staticmethod
    async def execute_seckill(
            session: AsyncSession,
            user_id: int,
            request: SeckillRequest,
            client_ip: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        执行抢单核心流程
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            request: 抢单请求
            client_ip: 客户端IP
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 消息, 订单号)
        """
        product_id = request.product_id
        quantity = request.quantity

        # ========== 第1步: 前置检查 ==========

        # 1.1 检查用户是否在黑名单
        user_blacklisted = await BlacklistCache.check_user_blacklist(user_id)
        if user_blacklisted:
            logger.warning(f"抢单被拒绝: 用户黑名单 - user_id={user_id}")
            return False, "您的账号被限制参与活动", None

        # 1.2 检查活动是否已开始
        activity_started = await ActivityManager.check_activity_started(product_id)
        if not activity_started:
            # 检查活动时间设置
            within_time = await ActivityManager.is_within_activity_time(product_id)
            if not within_time:
                logger.info(f"抢单被拒绝: 活动未开始 - product_id={product_id}")
                return False, "活动未开始或已结束", None

        # 1.3 获取活动配置
        seckill_config = await SeckillConfigService.get_active_by_product_id(session, product_id)

        # 1.4 检查用户限流(已登录用户)
        if seckill_config:
            user_limit = seckill_config.user_rate_limit
        else:
            user_limit = settings.USER_RATE_LIMIT_PER_SECOND

        user_allowed = await RateLimiter.check_user_limit(user_id, user_limit)
        if not user_allowed:
            logger.warning(f"抢单被拒绝: 用户限流 - user_id={user_id}")
            return False, "请求过于频繁，请稍后重试", None

        # ========== 第2步: Redis预扣库存 ==========

        # 2.1 检查库存是否存在
        stock = await InventoryRedisManager.get_stock(product_id)
        if stock < 0:
            logger.error(f"抢单失败: 库存未预加载 - product_id={product_id}")
            return False, "系统异常，请稍后重试", None

        # 2.2 检查库存是否足够
        if stock < quantity:
            logger.info(f"抢单失败: 库存不足 - product_id={product_id}, available={stock}")
            return False, "商品已售罄", None

        # 2.3 执行Redis库存扣减(原子操作)
        deduct_success = await InventoryRedisManager.deduct_stock(product_id, quantity)
        if not deduct_success:
            logger.warning(f"抢单失败: 库存扣减失败 - product_id={product_id}")
            return False, "商品已售罄", None

        # ========== 第3步: 用户限购检查 ==========

        max_purchase = settings.MAX_PURCHASE_PER_USER
        if seckill_config:
            max_purchase = seckill_config.max_purchase_per_user

        # 3.1 检查并记录购买(原子操作)
        limit_allowed, limit_message = await PurchaseLimitManager.check_and_record(
            user_id=user_id,
            product_id=product_id,
            max_limit=max_purchase,
            quantity=quantity
        )

        if not limit_allowed:
            # 限购检查失败，归还库存
            await InventoryRedisManager.restore_stock(product_id, quantity)
            logger.warning(f"抢单被拒绝: 限购限制 - user_id={user_id}, product_id={product_id}")
            return False, limit_message, None

        # ========== 第4步: 生成订单信息 ==========

        # 4.1 获取商品信息
        product = await ProductService.get_by_id(session, product_id)
        if product is None:
            # 商品不存在，归还库存
            await InventoryRedisManager.restore_stock(product_id, quantity)
            logger.error(f"抢单失败: 商品不存在 - product_id={product_id}")
            return False, "商品不存在", None

        # 4.2 生成订单号
        order_no = SeckillService._generate_order_no(user_id, product_id)

        # 4.3 计算订单金额
        unit_price = product.seckill_price
        total_amount = unit_price * quantity

        logger.info(
            f"抢单成功: user_id={user_id}, product_id={product_id}, "
            f"quantity={quantity}, order_no={order_no}"
        )

        return True, "抢单成功", order_no

    @staticmethod
    def _generate_order_no(user_id: int, product_id: int) -> str:
        """
        生成唯一订单号
        
        订单号规则: 时间戳 + 用户ID后4位 + 商品ID后4位 + 随机UUID前8位
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            str: 订单号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user_suffix = str(user_id).zfill(4)[-4:]
        product_suffix = str(product_id).zfill(4)[-4:]
        random_suffix = uuid.uuid4().hex[:8].upper()

        return f"{timestamp}{user_suffix}{product_suffix}{random_suffix}"

    @staticmethod
    async def prepare_order_data(
            session: AsyncSession,
            user_id: int,
            product_id: int,
            quantity: int,
            order_no: str,
            extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        准备订单数据(用于异步写入)
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            product_id: 商品ID
            quantity: 数量
            order_no: 订单号
            extra_data: 额外数据(收货信息等)
            
        Returns:
            Dict: 订单数据字典
        """
        # 获取商品信息
        product = await ProductService.get_by_id(session, product_id)
        if product is None:
            raise ValueError(f"商品不存在: product_id={product_id}")

        unit_price = product.seckill_price
        total_amount = unit_price * quantity

        order_data = {
            "order_no": order_no,
            "user_id": user_id,
            "product_id": product_id,
            "product_name": product.product_name,
            "product_code": product.product_code,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "status": 0,  # 待处理
            "status_message": "抢单成功，待确认",
        }

        # 添加额外数据
        if extra_data:
            for key in ["receiver_name", "receiver_phone", "receiver_address", "remark"]:
                if key in extra_data:
                    order_data[key] = extra_data[key]

        return order_data

    @staticmethod
    async def check_seckill_status(
            session: AsyncSession,
            product_id: int
    ) -> Dict[str, Any]:
        """
        检查抢单活动状态
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            
        Returns:
            Dict: 活动状态信息
        """
        # 获取Redis中的库存和状态
        stock = await InventoryRedisManager.get_stock(product_id)
        sold_count = await InventoryRedisManager.get_sold_count(product_id)
        activity_status = await ActivityManager.get_activity_status(product_id)

        # 获取活动配置
        seckill_config = await SeckillConfigService.get_active_by_product_id(session, product_id)

        result = {
            "product_id": product_id,
            "activity_status": activity_status if activity_status >= 0 else 0,
            "available_stock": max(0, stock),
            "sold_count": sold_count,
        }

        if seckill_config:
            result["start_time"] = seckill_config.start_time
            result["end_time"] = seckill_config.end_time
            result["max_purchase_per_user"] = seckill_config.max_purchase_per_user
            result["seckill_stock"] = seckill_config.seckill_stock

        return result

    @staticmethod
    async def rollback_seckill(
            user_id: int,
            product_id: int,
            quantity: int,
            order_no: Optional[str] = None
    ) -> bool:
        """
        抢单回滚(用于订单创建失败等场景)
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            quantity: 数量
            order_no: 订单号(可选)
            
        Returns:
            bool: 是否成功
        """
        logger.warning(
            f"执行抢单回滚: user_id={user_id}, product_id={product_id}, "
            f"quantity={quantity}, order_no={order_no}"
        )

        # 1. 归还库存
        await InventoryRedisManager.restore_stock(product_id, quantity)

        # 2. 清除购买记录(简化处理，实际可根据需求调整)
        # 注意: 这里不清除购买记录以防止用户恶意刷单后回滚重新抢单
        # 如果需要完整回滚，可以调用PurchaseLimitManager的相关方法

        return True


class SeckillPreloadService:
    """
    抢单预加载服务
    
    用于活动开始前预加载数据到Redis：
    1. 预加载库存
    2. 设置活动状态
    3. 缓存活动配置
    """

    @staticmethod
    async def preload_activity(
            session: AsyncSession,
            product_id: int,
            seckill_stock: int,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            auto_start: bool = False
    ) -> Tuple[bool, str]:
        """
        预加载抢单活动
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            seckill_stock: 秒杀库存数量
            start_time: 开始时间
            end_time: 结束时间
            auto_start: 是否立即开始活动
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 1. 检查商品是否存在
        product = await ProductService.get_by_id(session, product_id)
        if product is None:
            return False, "商品不存在"

        # 2. 检查库存是否足够
        if product.stock_quantity < seckill_stock:
            return False, f"商品库存不足，当前库存: {product.stock_quantity}"

        # 3. 预加载库存到Redis
        preload_success = await InventoryRedisManager.preload_inventory(product_id, seckill_stock)
        if not preload_success:
            return False, "库存预加载失败"

        # 4. 设置活动时间
        if start_time and end_time:
            await ActivityManager.set_activity_times(product_id, start_time, end_time)

        # 5. 设置活动状态
        if auto_start:
            await ActivityManager.set_activity_status(product_id, ActivityManager.STATUS_RUNNING)
        else:
            await ActivityManager.set_activity_status(product_id, ActivityManager.STATUS_NOT_STARTED)

        logger.info(
            f"活动预加载完成: product_id={product_id}, "
            f"stock={seckill_stock}, auto_start={auto_start}"
        )

        return True, "活动预加载成功"

    @staticmethod
    async def start_activity(product_id: int) -> bool:
        """
        开始活动
        
        Args:
            product_id: 商品ID
            
        Returns:
            bool: 是否成功
        """
        success = await ActivityManager.set_activity_status(
            product_id,
            ActivityManager.STATUS_RUNNING
        )
        logger.info(f"活动已开始: product_id={product_id}")
        return success

    @staticmethod
    async def end_activity(product_id: int) -> bool:
        """
        结束活动
        
        Args:
            product_id: 商品ID
            
        Returns:
            bool: 是否成功
        """
        success = await ActivityManager.set_activity_status(
            product_id,
            ActivityManager.STATUS_ENDED
        )
        logger.info(f"活动已结束: product_id={product_id}")
        return success

    @staticmethod
    async def get_preload_status(product_id: int) -> Dict[str, Any]:
        """
        获取预加载状态
        
        Args:
            product_id: 商品ID
            
        Returns:
            Dict: 状态信息
        """
        stock = await InventoryRedisManager.get_stock(product_id)
        sold = await InventoryRedisManager.get_sold_count(product_id)
        status = await ActivityManager.get_activity_status(product_id)

        status_text = "未设置"
        if status == ActivityManager.STATUS_NOT_STARTED:
            status_text = "未开始"
        elif status == ActivityManager.STATUS_RUNNING:
            status_text = "进行中"
        elif status == ActivityManager.STATUS_ENDED:
            status_text = "已结束"

        return {
            "product_id": product_id,
            "is_preloaded": stock >= 0,
            "available_stock": max(0, stock),
            "sold_count": sold,
            "activity_status": status,
            "activity_status_text": status_text
        }
