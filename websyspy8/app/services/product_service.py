"""
商品服务模块
处理商品CRUD、库存管理等业务逻辑
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.models import Product, Inventory, SeckillConfig
from app.schemas.schemas import ProductCreate, ProductResponse, InventoryResponse


class ProductService:
    """
    商品服务类
    
    提供商品相关的业务逻辑处理
    """

    @staticmethod
    async def get_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
        """
        根据ID获取商品
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            
        Returns:
            Optional[Product]: 商品对象或None
        """
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(session: AsyncSession, product_code: str) -> Optional[Product]:
        """
        根据商品编码获取商品
        
        Args:
            session: 数据库会话
            product_code: 商品编码
            
        Returns:
            Optional[Product]: 商品对象或None
        """
        stmt = select(Product).where(Product.product_code == product_code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, product_data: ProductCreate) -> Product:
        """
        创建新商品
        
        同时创建对应的库存记录
        
        Args:
            session: 数据库会话
            product_data: 商品创建数据
            
        Returns:
            Product: 新创建的商品对象
        """
        # 检查商品编码是否已存在
        existing = await ProductService.get_by_code(session, product_data.product_code)
        if existing:
            raise ValueError("商品编码已存在")

        # 创建商品
        product = Product(
            product_name=product_data.product_name,
            product_code=product_data.product_code,
            description=product_data.description,
            original_price=product_data.original_price,
            seckill_price=product_data.seckill_price,
            stock_quantity=product_data.stock_quantity,
            category=product_data.category,
            image_url=product_data.image_url,
            is_active=True,
            sold_quantity=0
        )

        session.add(product)
        await session.flush()  # 获取product.id

        # 创建库存记录
        inventory = Inventory(
            product_id=product.id,
            total_stock=product_data.stock_quantity,
            available_stock=product_data.stock_quantity,
            frozen_stock=0,
            sold_stock=0,
            version=0
        )

        session.add(inventory)
        await session.commit()
        await session.refresh(product)

        logger.info(f"商品创建成功: product_code={product.product_code}")
        return product

    @staticmethod
    async def update(
            session: AsyncSession,
            product_id: int,
            update_data: dict
    ) -> Optional[Product]:
        """
        更新商品信息
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            update_data: 更新数据字典
            
        Returns:
            Optional[Product]: 更新后的商品对象
        """
        product = await ProductService.get_by_id(session, product_id)
        if product is None:
            return None

        # 允许更新的字段
        allowed_fields = [
            'product_name', 'description', 'original_price',
            'seckill_price', 'category', 'image_url', 'is_active'
        ]

        for key, value in update_data.items():
            if key in allowed_fields and hasattr(product, key):
                setattr(product, key, value)

        await session.commit()
        await session.refresh(product)

        logger.info(f"商品更新成功: product_id={product_id}")
        return product

    @staticmethod
    async def delete(session: AsyncSession, product_id: int) -> bool:
        """
        软删除商品(设置为下架状态)
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            
        Returns:
            bool: 是否成功
        """
        product = await ProductService.get_by_id(session, product_id)
        if product is None:
            return False

        product.is_active = False
        await session.commit()

        logger.info(f"商品下架成功: product_id={product_id}")
        return True

    @staticmethod
    async def get_list(
            session: AsyncSession,
            page: int = 1,
            page_size: int = 10,
            is_active: Optional[bool] = None,
            category: Optional[str] = None
    ) -> tuple[List[Product], int]:
        """
        获取商品列表(分页)
        
        Args:
            session: 数据库会话
            page: 页码
            page_size: 每页数量
            is_active: 上架状态筛选
            category: 分类筛选
            
        Returns:
            tuple: (商品列表, 总记录数)
        """
        stmt = select(Product)
        count_stmt = select(func.count(Product.id))

        # 筛选条件
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
            count_stmt = count_stmt.where(Product.is_active == is_active)

        if category:
            stmt = stmt.where(Product.category == category)
            count_stmt = count_stmt.where(Product.category == category)

        # 获取总数
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 分页查询
        stmt = stmt.order_by(Product.id.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await session.execute(stmt)
        products = result.scalars().all()

        return list(products), total

    @staticmethod
    def to_response(product: Product) -> ProductResponse:
        """
        将Product模型转换为ProductResponse
        
        Args:
            product: Product模型对象
            
        Returns:
            ProductResponse: 商品响应对象
        """
        return ProductResponse(
            id=product.id,
            product_name=product.product_name,
            product_code=product.product_code,
            description=product.description,
            original_price=product.original_price,
            seckill_price=product.seckill_price,
            stock_quantity=product.stock_quantity,
            sold_quantity=product.sold_quantity,
            category=product.category,
            image_url=product.image_url,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )


class InventoryService:
    """
    库存服务类
    
    提供库存相关的业务逻辑处理
    """

    @staticmethod
    async def get_by_product_id(session: AsyncSession, product_id: int) -> Optional[Inventory]:
        """
        根据商品ID获取库存记录
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            
        Returns:
            Optional[Inventory]: 库存对象或None
        """
        stmt = select(Inventory).where(Inventory.product_id == product_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_stock(
            session: AsyncSession,
            product_id: int,
            quantity: int,
            is_add: bool = False
    ) -> bool:
        """
        更新库存(增加或减少)
        
        使用乐观锁防止并发问题
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            quantity: 数量
            is_add: 是否为增加库存(默认False表示扣减)
            
        Returns:
            bool: 是否成功
        """
        inventory = await InventoryService.get_by_product_id(session, product_id)
        if inventory is None:
            logger.error(f"库存记录不存在: product_id={product_id}")
            return False

        # 计算新库存
        if is_add:
            new_available = inventory.available_stock + quantity
            new_total = inventory.total_stock + quantity
        else:
            if inventory.available_stock < quantity:
                logger.warning(f"库存不足: product_id={product_id}, available={inventory.available_stock}, need={quantity}")
                return False
            new_available = inventory.available_stock - quantity
            new_total = inventory.total_stock  # 总库存不变

        # 更新库存
        inventory.available_stock = new_available
        inventory.total_stock = new_total
        if not is_add:
            inventory.sold_stock += quantity

        # 版本号递增(乐观锁)
        inventory.version += 1

        await session.commit()
        logger.info(f"库存更新成功: product_id={product_id}, change={quantity if is_add else -quantity}")
        return True

    @staticmethod
    async def freeze_stock(session: AsyncSession, product_id: int, quantity: int) -> bool:
        """
        冻结库存(下单时)
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            quantity: 冻结数量
            
        Returns:
            bool: 是否成功
        """
        inventory = await InventoryService.get_by_product_id(session, product_id)
        if inventory is None:
            return False

        if inventory.available_stock < quantity:
            return False

        inventory.available_stock -= quantity
        inventory.frozen_stock += quantity
        inventory.version += 1

        await session.commit()
        logger.info(f"库存冻结: product_id={product_id}, quantity={quantity}")
        return True

    @staticmethod
    async def unfreeze_stock(session: AsyncSession, product_id: int, quantity: int) -> bool:
        """
        解冻库存(订单取消时)
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            quantity: 解冻数量
            
        Returns:
            bool: 是否成功
        """
        inventory = await InventoryService.get_by_product_id(session, product_id)
        if inventory is None:
            return False

        if inventory.frozen_stock < quantity:
            return False

        inventory.available_stock += quantity
        inventory.frozen_stock -= quantity
        inventory.version += 1

        await session.commit()
        logger.info(f"库存解冻: product_id={product_id}, quantity={quantity}")
        return True

    @staticmethod
    async def confirm_sale(session: AsyncSession, product_id: int, quantity: int) -> bool:
        """
        确认销售(支付后)
        
        将冻结库存转为已售
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            quantity: 数量
            
        Returns:
            bool: 是否成功
        """
        inventory = await InventoryService.get_by_product_id(session, product_id)
        if inventory is None:
            return False

        if inventory.frozen_stock < quantity:
            return False

        inventory.frozen_stock -= quantity
        inventory.sold_stock += quantity
        inventory.version += 1

        await session.commit()
        logger.info(f"确认销售: product_id={product_id}, quantity={quantity}")
        return True

    @staticmethod
    def to_response(inventory: Inventory) -> InventoryResponse:
        """
        将Inventory模型转换为InventoryResponse
        
        Args:
            inventory: Inventory模型对象
            
        Returns:
            InventoryResponse: 库存响应对象
        """
        return InventoryResponse(
            product_id=inventory.product_id,
            total_stock=inventory.total_stock,
            available_stock=inventory.available_stock,
            frozen_stock=inventory.frozen_stock,
            sold_stock=inventory.sold_stock,
            version=inventory.version
        )


class SeckillConfigService:
    """
    抢单活动配置服务类
    
    提供抢单活动配置的业务逻辑处理
    """

    @staticmethod
    async def get_by_id(session: AsyncSession, config_id: int) -> Optional[SeckillConfig]:
        """
        根据ID获取活动配置
        
        Args:
            session: 数据库会话
            config_id: 配置ID
            
        Returns:
            Optional[SeckillConfig]: 配置对象或None
        """
        stmt = select(SeckillConfig).where(SeckillConfig.id == config_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_by_product_id(session: AsyncSession, product_id: int) -> Optional[SeckillConfig]:
        """
        获取指定商品的有效活动配置
        
        Args:
            session: 数据库会话
            product_id: 商品ID
            
        Returns:
            Optional[SeckillConfig]: 配置对象或None
        """
        now = datetime.utcnow()
        stmt = (
            select(SeckillConfig)
            .where(
                SeckillConfig.product_id == product_id,
                SeckillConfig.is_active == True,
                SeckillConfig.start_time <= now,
                SeckillConfig.end_time >= now
            )
            .order_by(SeckillConfig.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_active(session: AsyncSession) -> List[SeckillConfig]:
        """
        获取所有进行中的活动
        
        Args:
            session: 数据库会话
            
        Returns:
            List[SeckillConfig]: 活动配置列表
        """
        now = datetime.utcnow()
        stmt = (
            select(SeckillConfig)
            .where(
                SeckillConfig.is_active == True,
                SeckillConfig.start_time <= now,
                SeckillConfig.end_time >= now
            )
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
