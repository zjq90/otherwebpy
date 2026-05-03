"""
测试数据生成脚本
用于生成系统测试所需的模拟数据
"""

import asyncio
import random
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker, init_db
from models import User, Crop, Plot, ProductionRecord, FinancialRecord, EnvironmentRecord
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    return pwd_context.hash(password)


def generate_random_date(start_year: int = 2022, end_year: int = 2024) -> date:
    """
    生成随机日期
    """
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


async def generate_users(session: AsyncSession):
    """
    生成用户测试数据
    """
    users_data = [
        {
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "real_name": "系统管理员",
            "email": "admin@farm.com",
            "phone": "13800138000",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "manager",
            "password_hash": get_password_hash("manager123"),
            "real_name": "农场经理",
            "email": "manager@farm.com",
            "phone": "13800138001",
            "role": "user",
            "is_active": True
        },
        {
            "username": "viewer",
            "password_hash": get_password_hash("viewer123"),
            "real_name": "数据查看员",
            "email": "viewer@farm.com",
            "phone": "13800138002",
            "role": "viewer",
            "is_active": True
        }
    ]

    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
    
    await session.commit()
    print("用户数据生成完成")


async def generate_crops(session: AsyncSession):
    """
    生成作物测试数据
    """
    crops_data = [
        {"name": "小麦", "variety": "冬小麦", "category": "粮食作物", "unit": "公斤", "growth_cycle": 180, "description": "优质冬小麦品种"},
        {"name": "玉米", "variety": "郑单958", "category": "粮食作物", "unit": "公斤", "growth_cycle": 120, "description": "高产玉米品种"},
        {"name": "水稻", "variety": "杂交稻", "category": "粮食作物", "unit": "公斤", "growth_cycle": 140, "description": "优质杂交水稻"},
        {"name": "大豆", "variety": "高蛋白大豆", "category": "经济作物", "unit": "公斤", "growth_cycle": 100, "description": "高蛋白大豆品种"},
        {"name": "番茄", "variety": "西红柿", "category": "蔬菜作物", "unit": "公斤", "growth_cycle": 90, "description": "大棚种植番茄"},
        {"name": "黄瓜", "variety": "刺黄瓜", "category": "蔬菜作物", "unit": "公斤", "growth_cycle": 60, "description": "优质黄瓜品种"},
        {"name": "苹果", "variety": "红富士", "category": "水果作物", "unit": "公斤", "growth_cycle": 180, "description": "红富士苹果"},
        {"name": "葡萄", "variety": "巨峰", "category": "水果作物", "unit": "公斤", "growth_cycle": 150, "description": "巨峰葡萄"}
    ]

    for crop_data in crops_data:
        crop = Crop(**crop_data)
        session.add(crop)
    
    await session.commit()
    print("作物数据生成完成")


async def generate_plots(session: AsyncSession):
    """
    生成地块测试数据
    """
    plots_data = [
        {"name": "东地块一号", "code": "PLOT-001", "area": 50.0, "location": "农场东部", "soil_type": "壤土", "irrigation_type": "滴灌", "description": "优质壤土，适合种植粮食作物"},
        {"name": "东地块二号", "code": "PLOT-002", "area": 45.0, "location": "农场东部", "soil_type": "砂壤土", "irrigation_type": "喷灌", "description": "砂壤土，适合种植蔬菜"},
        {"name": "西地块一号", "code": "PLOT-003", "area": 60.0, "location": "农场西部", "soil_type": "黏土", "irrigation_type": "漫灌", "description": "黏土，保水性好"},
        {"name": "西地块二号", "code": "PLOT-004", "area": 35.0, "location": "农场西部", "soil_type": "壤土", "irrigation_type": "滴灌", "description": "优质种植区"},
        {"name": "南地块一号", "code": "PLOT-005", "area": 40.0, "location": "农场南部", "soil_type": "砂质土", "irrigation_type": "喷灌", "description": "适合水果种植"},
        {"name": "北地块一号", "code": "PLOT-006", "area": 55.0, "location": "农场北部", "soil_type": "黑土", "irrigation_type": "滴灌", "description": "肥沃黑土地"}
    ]

    for plot_data in plots_data:
        plot = Plot(**plot_data)
        session.add(plot)
    
    await session.commit()
    print("地块数据生成完成")


async def generate_production_records(session: AsyncSession):
    """
    生成生产记录测试数据
    """
    # 获取所有作物和地块
    from sqlalchemy import select
    crops_result = await session.execute(select(Crop).where(Crop.is_active == True))
    crops = crops_result.scalars().all()
    
    plots_result = await session.execute(select(Plot).where(Plot.is_active == True))
    plots = plots_result.scalars().all()

    seasons = ["春季", "夏季", "秋季", "冬季"]
    
    for year in [2022, 2023, 2024]:
        for season in seasons:
            for _ in range(random.randint(2, 5)):
                crop = random.choice(crops)
                plot = random.choice(plots)
                
                # 根据季节生成种植日期
                if season == "春季":
                    planting_month = random.randint(3, 5)
                elif season == "夏季":
                    planting_month = random.randint(6, 8)
                elif season == "秋季":
                    planting_month = random.randint(9, 11)
                else:
                    planting_month = random.randint(12, 12)
                
                planting_date = date(year, planting_month, random.randint(1, 28))
                harvest_date = planting_date + timedelta(days=random.randint(90, 180))
                
                # 根据作物类型生成产量
                if crop.category == "粮食作物":
                    yield_amount = round(random.uniform(500, 1500), 2)
                    selling_price = round(random.uniform(2.0, 4.0), 2)
                elif crop.category == "经济作物":
                    yield_amount = round(random.uniform(200, 800), 2)
                    selling_price = round(random.uniform(4.0, 8.0), 2)
                elif crop.category == "蔬菜":
                    yield_amount = round(random.uniform(1000, 3000), 2)
                    selling_price = round(random.uniform(3.0, 6.0), 2)
                else:
                    yield_amount = round(random.uniform(800, 2000), 2)
                    selling_price = round(random.uniform(5.0, 10.0), 2)
                
                input_cost = round(random.uniform(500, 2000), 2)
                revenue = round(yield_amount * selling_price, 2)
                profit = round(revenue - input_cost, 2)
                
                production_record = ProductionRecord(
                    crop_id=crop.id,
                    plot_id=plot.id,
                    planting_date=planting_date,
                    harvest_date=harvest_date if harvest_date.year <= 2024 else None,
                    season=season,
                    year=year,
                    yield_amount=yield_amount,
                    yield_unit="公斤",
                    input_cost=input_cost,
                    selling_price=selling_price,
                    revenue=revenue,
                    profit=profit,
                    notes=f"{crop.name}在{plot.name}的{season}种植记录"
                )
                session.add(production_record)
    
    await session.commit()
    print("生产记录数据生成完成")


async def generate_financial_records(session: AsyncSession):
    """
    生成财务记录测试数据
    """
    from sqlalchemy import select
    
    # 收入分类
    income_categories = ["农产品销售", "政府补贴", "租金收入", "其他收入"]
    # 支出分类
    expense_categories = ["种子", "化肥", "农药", "水电", "人工", "机械", "运输", "其他支出"]
    
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            # 每个月生成3-8条收入记录
            for _ in range(random.randint(3, 8)):
                category = random.choice(income_categories)
                if category == "农产品销售":
                    amount = round(random.uniform(5000, 30000), 2)
                elif category == "政府补贴":
                    amount = round(random.uniform(1000, 5000), 2)
                else:
                    amount = round(random.uniform(500, 3000), 2)
                
                record_date = date(year, month, random.randint(1, 28))
                quarter = (month - 1) // 3 + 1
                
                financial_record = FinancialRecord(
                    record_date=record_date,
                    record_type="income",
                    category=category,
                    amount=amount,
                    description=f"{year}年{month}月{category}",
                    payment_method=random.choice(["银行转账", "现金", "微信支付", "支付宝"]),
                    year=year,
                    month=month,
                    quarter=quarter
                )
                session.add(financial_record)
            
            # 每个月生成5-12条支出记录
            for _ in range(random.randint(5, 12)):
                category = random.choice(expense_categories)
                if category in ["种子", "化肥", "农药", "人工"]:
                    amount = round(random.uniform(2000, 10000), 2)
                elif category in ["水电", "机械", "运输"]:
                    amount = round(random.uniform(1000, 5000), 2)
                else:
                    amount = round(random.uniform(500, 3000), 2)
                
                record_date = date(year, month, random.randint(1, 28))
                quarter = (month - 1) // 3 + 1
                
                financial_record = FinancialRecord(
                    record_date=record_date,
                    record_type="expense",
                    category=category,
                    amount=amount,
                    description=f"{year}年{month}月{category}支出",
                    payment_method=random.choice(["银行转账", "现金", "微信支付", "支付宝"]),
                    year=year,
                    month=month,
                    quarter=quarter
                )
                session.add(financial_record)
    
    await session.commit()
    print("财务记录数据生成完成")


async def generate_environment_records(session: AsyncSession):
    """
    生成环境资源记录测试数据
    """
    from sqlalchemy import select
    
    plots_result = await session.execute(select(Plot).where(Plot.is_active == True))
    plots = plots_result.scalars().all()
    
    water_sources = ["地下水", "河水", "水库水", "自来水"]
    fertilizer_types = ["尿素", "复合肥", "有机肥", "钾肥", "磷肥"]
    pesticide_types = ["杀虫剂", "杀菌剂", "除草剂", "植物生长调节剂"]
    fuel_types = ["柴油", "汽油", "天然气"]
    
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            for plot in plots:
                # 每个地块每个月生成一条环境记录
                record_date = date(year, month, random.randint(1, 28))
                
                # 根据地块面积生成资源使用量
                area_factor = plot.area / 50.0  # 以50亩为基准
                
                # 水资源
                water_usage = round(random.uniform(50, 200) * area_factor, 2)
                water_cost = round(water_usage * random.uniform(3.0, 5.0), 2)
                
                # 能源
                electricity_usage = round(random.uniform(100, 500) * area_factor, 2)
                electricity_cost = round(electricity_usage * random.uniform(0.8, 1.2), 2)
                fuel_usage = round(random.uniform(20, 100) * area_factor, 2)
                fuel_cost = round(fuel_usage * random.uniform(6.0, 8.0), 2)
                
                # 农资（根据季节调整）
                if month in [3, 4, 5, 6]:  # 春夏季是农资使用高峰期
                    fertilizer_factor = 1.5
                    pesticide_factor = 1.5
                    seed_factor = 1.5
                else:
                    fertilizer_factor = 1.0
                    pesticide_factor = 1.0
                    seed_factor = 1.0
                
                fertilizer_usage = round(random.uniform(50, 200) * area_factor * fertilizer_factor, 2)
                fertilizer_cost = round(fertilizer_usage * random.uniform(3.0, 5.0), 2)
                pesticide_usage = round(random.uniform(10, 50) * area_factor * pesticide_factor, 2)
                pesticide_cost = round(pesticide_usage * random.uniform(20.0, 50.0), 2)
                seed_usage = round(random.uniform(5, 30) * area_factor * seed_factor, 2)
                seed_cost = round(seed_usage * random.uniform(30.0, 80.0), 2)
                
                environment_record = EnvironmentRecord(
                    plot_id=plot.id,
                    record_date=record_date,
                    year=year,
                    month=month,
                    water_usage=water_usage,
                    water_source=random.choice(water_sources),
                    water_cost=water_cost,
                    electricity_usage=electricity_usage,
                    electricity_cost=electricity_cost,
                    fuel_usage=fuel_usage,
                    fuel_type=random.choice(fuel_types),
                    fuel_cost=fuel_cost,
                    fertilizer_usage=fertilizer_usage,
                    fertilizer_type=random.choice(fertilizer_types),
                    fertilizer_cost=fertilizer_cost,
                    pesticide_usage=pesticide_usage,
                    pesticide_type=random.choice(pesticide_types),
                    pesticide_cost=pesticide_cost,
                    seed_usage=seed_usage,
                    seed_type=random.choice(["常规种", "杂交种", "转基因种"]),
                    seed_cost=seed_cost,
                    notes=f"{plot.name}{year}年{month}月资源使用记录"
                )
                session.add(environment_record)
    
    await session.commit()
    print("环境资源记录数据生成完成")


async def main():
    """
    主函数：初始化数据库并生成测试数据
    """
    print("开始初始化数据库...")
    await init_db()
    
    async with async_session_maker() as session:
        print("开始生成测试数据...")
        
        await generate_users(session)
        await generate_crops(session)
        await generate_plots(session)
        await generate_production_records(session)
        await generate_financial_records(session)
        await generate_environment_records(session)
        
        print("所有测试数据生成完成！")
        print("\n系统管理员账号：admin / admin123")
        print("农场经理账号：manager / manager123")
        print("数据查看员账号：viewer / viewer123")


if __name__ == "__main__":
    # 确保data目录存在
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    asyncio.run(main())
