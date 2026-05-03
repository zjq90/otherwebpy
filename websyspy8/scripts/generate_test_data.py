"""
测试数据生成脚本
生成大量测试数据用于压力测试：
1. 生成用户数据(支持万级)
2. 生成商品数据
3. 生成活动配置
4. 生成订单数据(可选)

使用Faker库生成真实的模拟数据
"""
import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from contextlib import asynccontextmanager

# 添加项目根目录到路径
sys.path.insert(0, 'd:\\Aijava\\javaproject\\260422\\SolcodePython\\otherSysweb\\v8\\websyspy8')

from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import engine, async_session_maker, init_db
from app.models.models import User, Product, Inventory, SeckillConfig, Order, Blacklist
from app.utils.auth import AuthService


fake = Faker('zh_CN')  # 使用中文数据


class TestDataGenerator:
    """测试数据生成器"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_users(self, count: int = 10000, batch_size: int = 500) -> List[int]:
        """
        生成用户数据
        
        Args:
            count: 生成数量(默认10000)
            batch_size: 批量插入大小
            
        Returns:
            List[int]: 生成的用户ID列表
        """
        logger.info(f"开始生成用户数据，数量: {count}")

        user_ids = []
        password_hash = AuthService.get_password_hash("123456")  # 默认密码

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_count = batch_end - batch_start

            batch_users = []
            for i in range(batch_count):
                user_num = batch_start + i + 1
                username = f"user_{user_num:08d}"
                email = f"{username}@example.com"
                phone = fake.phone_number()

                user = User(
                    username=username,
                    password_hash=password_hash,
                    email=email,
                    phone=phone,
                    is_active=True,
                    is_admin=False
                )
                batch_users.append(user)

            # 批量添加
            self.session.add_all(batch_users)
            await self.session.commit()

            # 刷新获取ID
            for user in batch_users:
                await self.session.refresh(user)
                user_ids.append(user.id)

            logger.info(f"已生成 {batch_end}/{count} 个用户")

        logger.info(f"用户数据生成完成，共生成 {len(user_ids)} 个用户")
        return user_ids

    async def generate_products(self, count: int = 10) -> List[int]:
        """
        生成商品数据
        
        Args:
            count: 生成数量
            
        Returns:
            List[int]: 生成的商品ID列表
        """
        logger.info(f"开始生成商品数据，数量: {count}")

        product_ids = []
        categories = ["电子产品", "服装", "家居", "食品", "美妆", "运动", "图书"]

        for i in range(count):
            product_code = f"PROD{datetime.now().strftime('%Y%m%d')}{i+1:04d}"
            original_price = fake.random_int(min=100, max=10000)
            seckill_price = int(original_price * fake.random_int(min=3, max=8) / 10)
            stock_quantity = fake.random_int(min=100, max=10000)

            product = Product(
                product_name=fake.catch_phrase(),
                product_code=product_code,
                description=fake.text(max_nb_chars=200),
                original_price=original_price,
                seckill_price=seckill_price,
                stock_quantity=stock_quantity,
                sold_quantity=0,
                is_active=True,
                category=fake.random_element(elements=categories),
                image_url=f"https://picsum.photos/400/300?random={fake.random_int()}"
            )

            self.session.add(product)
            await self.session.flush()

            # 创建库存记录
            inventory = Inventory(
                product_id=product.id,
                total_stock=stock_quantity,
                available_stock=stock_quantity,
                frozen_stock=0,
                sold_stock=0,
                version=0
            )

            self.session.add(inventory)
            await self.session.commit()

            product_ids.append(product.id)
            logger.info(f"已生成商品: {product.product_name}, ID={product.id}")

        logger.info(f"商品数据生成完成，共生成 {len(product_ids)} 个商品")
        return product_ids

    async def generate_seckill_configs(
            self,
            product_ids: List[int],
            start_hours: int = 0,
            duration_hours: int = 24
    ) -> List[int]:
        """
        生成抢单活动配置
        
        Args:
            product_ids: 商品ID列表
            start_hours: 开始时间(小时后，0表示立即开始)
            duration_hours: 持续时间(小时)
            
        Returns:
            List[int]: 生成的配置ID列表
        """
        logger.info(f"开始生成抢单活动配置，商品数量: {len(product_ids)}")

        config_ids = []
        now = datetime.utcnow()
        start_time = now + timedelta(hours=start_hours)
        end_time = start_time + timedelta(hours=duration_hours)

        for product_id in product_ids:
            # 获取商品信息
            from sqlalchemy import select
            stmt = select(Product).where(Product.id == product_id)
            result = await self.session.execute(stmt)
            product = result.scalar_one_or_none()

            if product is None:
                continue

            # 秒杀库存取商品库存的一部分
            seckill_stock = min(
                product.stock_quantity,
                fake.random_int(min=100, max=1000)
            )

            config = SeckillConfig(
                config_name=f"秒杀活动-{product.product_name[:20]}",
                product_id=product_id,
                seckill_stock=seckill_stock,
                start_time=start_time,
                end_time=end_time,
                is_active=True,
                max_purchase_per_user=1,
                ip_rate_limit=10,
                user_rate_limit=5,
                global_rate_limit=10000,
                activity_status=1 if start_hours == 0 else 0
            )

            self.session.add(config)
            await self.session.commit()

            config_ids.append(config.id)
            logger.info(f"已生成活动配置: {config.config_name}, ID={config.id}")

        logger.info(f"活动配置生成完成，共生成 {len(config_ids)} 个配置")
        return config_ids

    async def generate_orders(
            self,
            user_ids: List[int],
            product_ids: List[int],
            count: int = 1000,
            batch_size: int = 100
    ) -> List[int]:
        """
        生成订单数据
        
        Args:
            user_ids: 用户ID列表
            product_ids: 商品ID列表
            count: 订单数量
            batch_size: 批量插入大小
            
        Returns:
            List[int]: 生成的订单ID列表
        """
        logger.info(f"开始生成订单数据，数量: {count}")

        order_ids = []

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_count = batch_end - batch_start

            batch_orders = []
            for i in range(batch_count):
                user_id = fake.random_element(elements=user_ids)
                product_id = fake.random_element(elements=product_ids)

                # 获取商品信息
                from sqlalchemy import select
                stmt = select(Product).where(Product.id == product_id)
                result = await self.session.execute(stmt)
                product = result.scalar_one_or_none()

                if product is None:
                    continue

                quantity = 1
                unit_price = product.seckill_price
                total_amount = unit_price * quantity

                # 生成订单号
                order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{fake.random_int(min=1000, max=9999)}"

                order = Order(
                    order_no=order_no,
                    user_id=user_id,
                    product_id=product_id,
                    product_name=product.product_name,
                    product_code=product.product_code,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    status=fake.random_int(min=0, max=3),
                    status_message="测试订单",
                    receiver_name=fake.name(),
                    receiver_phone=fake.phone_number(),
                    receiver_address=fake.address()
                )

                batch_orders.append(order)

            # 批量添加
            self.session.add_all(batch_orders)
            await self.session.commit()

            # 刷新获取ID
            for order in batch_orders:
                await self.session.refresh(order)
                order_ids.append(order.id)

            logger.info(f"已生成 {batch_end}/{count} 个订单")

        logger.info(f"订单数据生成完成，共生成 {len(order_ids)} 个订单")
        return order_ids

    async def generate_blacklist(
            self,
            user_ids: List[int] = None,
            ip_count: int = 10,
            user_count: int = 5
    ) -> List[int]:
        """
        生成黑名单数据
        
        Args:
            user_ids: 用户ID列表
            ip_count: IP黑名单数量
            user_count: 用户黑名单数量
            
        Returns:
            List[int]: 生成的黑名单ID列表
        """
        logger.info(f"开始生成黑名单数据")

        blacklist_ids = []

        # 生成IP黑名单
        for i in range(ip_count):
            ip_address = f"192.168.1.{fake.random_int(min=100, max=200)}"
            blacklist = Blacklist(
                target_type="ip",
                target_value=ip_address,
                is_active=True,
                reason="测试IP黑名单"
            )
            self.session.add(blacklist)
            await self.session.commit()
            blacklist_ids.append(blacklist.id)
            logger.info(f"已添加IP黑名单: {ip_address}")

        # 生成用户黑名单
        if user_ids and user_count > 0:
            selected_users = fake.random_elements(
                elements=user_ids,
                length=min(user_count, len(user_ids)),
                unique=True
            )

            for user_id in selected_users:
                blacklist = Blacklist(
                    target_type="user_id",
                    target_value=str(user_id),
                    is_active=True,
                    reason="测试用户黑名单"
                )
                self.session.add(blacklist)
                await self.session.commit()
                blacklist_ids.append(blacklist.id)
                logger.info(f"已添加用户黑名单: {user_id}")

        logger.info(f"黑名单数据生成完成，共生成 {len(blacklist_ids)} 条")
        return blacklist_ids


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("测试数据生成器启动")
    logger.info("=" * 60)

    # 初始化数据库
    logger.info("初始化数据库...")
    await init_db()

    # 创建会话
    async with async_session_maker() as session:
        generator = TestDataGenerator(session)

        # ========== 1. 生成用户数据 ==========
        logger.info("\n" + "=" * 60)
        logger.info("第1步: 生成用户数据")
        logger.info("=" * 60)

        user_count = 10000  # 默认生成1万个用户
        user_ids = await generator.generate_users(count=user_count)

        # ========== 2. 生成商品数据 ==========
        logger.info("\n" + "=" * 60)
        logger.info("第2步: 生成商品数据")
        logger.info("=" * 60)

        product_count = 10  # 默认生成10个商品
        product_ids = await generator.generate_products(count=product_count)

        # ========== 3. 生成抢单活动配置 ==========
        logger.info("\n" + "=" * 60)
        logger.info("第3步: 生成抢单活动配置")
        logger.info("=" * 60)

        config_ids = await generator.generate_seckill_configs(
            product_ids=product_ids,
            start_hours=0,  # 立即开始
            duration_hours=24
        )

        # ========== 4. 生成订单数据(可选) ==========
        logger.info("\n" + "=" * 60)
        logger.info("第4步: 生成订单数据(可选)")
        logger.info("=" * 60)

        order_count = 1000  # 默认生成1000个订单
        order_ids = await generator.generate_orders(
            user_ids=user_ids[:1000],  # 使用前1000个用户生成订单
            product_ids=product_ids,
            count=order_count
        )

        # ========== 5. 生成黑名单数据 ==========
        logger.info("\n" + "=" * 60)
        logger.info("第5步: 生成黑名单数据")
        logger.info("=" * 60)

        blacklist_ids = await generator.generate_blacklist(
            user_ids=user_ids,
            ip_count=10,
            user_count=5
        )

        # ========== 汇总 ==========
        logger.info("\n" + "=" * 60)
        logger.info("数据生成完成汇总")
        logger.info("=" * 60)
        logger.info(f"用户数据: {len(user_ids)} 条")
        logger.info(f"商品数据: {len(product_ids)} 条")
        logger.info(f"活动配置: {len(config_ids)} 条")
        logger.info(f"订单数据: {len(order_ids)} 条")
        logger.info(f"黑名单数据: {len(blacklist_ids)} 条")
        logger.info("=" * 60)

        # 输出测试账号信息
        logger.info("\n测试账号信息:")
        logger.info(f"  用户名格式: user_00000001 ~ user_{user_count:08d}")
        logger.info(f"  默认密码: 123456")
        logger.info(f"  管理员账号: 需要手动设置is_admin=True")

        # 输出活动商品信息
        logger.info("\n活动商品信息:")
        for pid in product_ids[:3]:
            stmt = select(Product).where(Product.id == pid)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if product:
                logger.info(f"  商品ID: {product.id}")
                logger.info(f"    名称: {product.product_name}")
                logger.info(f"    原价: {product.original_price}")
                logger.info(f"    秒杀价: {product.seckill_price}")
                logger.info(f"    库存: {product.stock_quantity}")


if __name__ == "__main__":
    asyncio.run(main())
