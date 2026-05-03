"""
数据库模型定义
包含所有数据表的ORM模型
"""

from datetime import datetime, date
from sqlalchemy import String, Float, Integer, Date, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    """
    用户表模型
    存储系统用户信息
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")  # admin, user, viewer
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Crop(Base):
    """
    作物表模型
    存储作物基本信息
    """
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # 作物名称
    variety: Mapped[str] = mapped_column(String(100), nullable=True)  # 品种
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # 分类：粮食、蔬菜、水果等
    unit: Mapped[str] = mapped_column(String(20), default="公斤")  # 计量单位
    growth_cycle: Mapped[int] = mapped_column(Integer, nullable=True)  # 生长周期（天）
    description: Mapped[str] = mapped_column(Text, nullable=True)  # 描述
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    production_records: Mapped[list["ProductionRecord"]] = relationship(
        "ProductionRecord", back_populates="crop", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Crop(id={self.id}, name={self.name})>"


class Plot(Base):
    """
    地块表模型
    存储地块基本信息
    """
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # 地块名称
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 地块编号
    area: Mapped[float] = mapped_column(Float, nullable=False)  # 面积（亩）
    location: Mapped[str] = mapped_column(String(255), nullable=True)  # 位置
    soil_type: Mapped[str] = mapped_column(String(50), nullable=True)  # 土壤类型
    irrigation_type: Mapped[str] = mapped_column(String(50), nullable=True)  # 灌溉方式
    description: Mapped[str] = mapped_column(Text, nullable=True)  # 描述
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    production_records: Mapped[list["ProductionRecord"]] = relationship(
        "ProductionRecord", back_populates="plot", cascade="all, delete-orphan"
    )
    environment_records: Mapped[list["EnvironmentRecord"]] = relationship(
        "EnvironmentRecord", back_populates="plot", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Plot(id={self.id}, name={self.name})>"


class ProductionRecord(Base):
    """
    生产记录表模型
    存储生产相关数据，用于生成生产报表
    """
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), nullable=False, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey("plots.id"), nullable=False, index=True)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)  # 种植日期
    harvest_date: Mapped[date] = mapped_column(Date, nullable=True)  # 收获日期
    season: Mapped[str] = mapped_column(String(20), nullable=True)  # 季节：春、夏、秋、冬
    year: Mapped[int] = mapped_column(Integer, nullable=False)  # 年份
    yield_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 产量
    yield_unit: Mapped[str] = mapped_column(String(20), default="公斤")  # 产量单位
    input_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 投入成本
    input_details: Mapped[str] = mapped_column(Text, nullable=True)  # 投入明细（JSON格式）
    selling_price: Mapped[float] = mapped_column(Float, default=0.0)  # 销售单价
    revenue: Mapped[float] = mapped_column(Float, default=0.0)  # 收入
    profit: Mapped[float] = mapped_column(Float, default=0.0)  # 利润
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    crop: Mapped["Crop"] = relationship("Crop", back_populates="production_records")
    plot: Mapped["Plot"] = relationship("Plot", back_populates="production_records")
    financial_records: Mapped[list["FinancialRecord"]] = relationship(
        "FinancialRecord", back_populates="production_record", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ProductionRecord(id={self.id}, crop_id={self.crop_id}, year={self.year})>"


class FinancialRecord(Base):
    """
    财务记录表模型
    存储收入支出数据，用于生成财务报表
    """
    __tablename__ = "financial_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)  # 记录日期
    record_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 类型：income(收入), expense(支出)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 分类
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # 金额
    currency: Mapped[str] = mapped_column(String(10), default="CNY")  # 货币
    description: Mapped[str] = mapped_column(String(255), nullable=True)  # 描述
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)  # 支付方式
    production_record_id: Mapped[int] = mapped_column(ForeignKey("production_records.id"), nullable=True)  # 关联生产记录
    year: Mapped[int] = mapped_column(Integer, nullable=False)  # 年份
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 月份
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)  # 季度
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    production_record: Mapped["ProductionRecord"] = relationship(
        "ProductionRecord", back_populates="financial_records"
    )

    def __repr__(self):
        return f"<FinancialRecord(id={self.id}, type={self.record_type}, amount={self.amount})>"


class EnvironmentRecord(Base):
    """
    环境资源记录表模型
    存储水资源、能源、农资使用数据，用于生成环境报表
    """
    __tablename__ = "environment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey("plots.id"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)  # 记录日期
    year: Mapped[int] = mapped_column(Integer, nullable=False)  # 年份
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 月份

    # 水资源使用
    water_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 用水量（立方米）
    water_source: Mapped[str] = mapped_column(String(50), nullable=True)  # 水源
    water_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 用水成本

    # 能源使用
    electricity_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 用电量（度）
    electricity_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 用电成本
    fuel_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 燃料使用（升）
    fuel_type: Mapped[str] = mapped_column(String(50), nullable=True)  # 燃料类型
    fuel_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 燃料成本

    # 农资使用
    fertilizer_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 化肥使用量（公斤）
    fertilizer_type: Mapped[str] = mapped_column(String(100), nullable=True)  # 化肥类型
    fertilizer_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 化肥成本
    pesticide_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 农药使用量（公斤）
    pesticide_type: Mapped[str] = mapped_column(String(100), nullable=True)  # 农药类型
    pesticide_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 农药成本
    seed_usage: Mapped[float] = mapped_column(Float, default=0.0)  # 种子使用量（公斤）
    seed_type: Mapped[str] = mapped_column(String(100), nullable=True)  # 种子类型
    seed_cost: Mapped[float] = mapped_column(Float, default=0.0)  # 种子成本

    # 其他
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    plot: Mapped["Plot"] = relationship("Plot", back_populates="environment_records")

    def __repr__(self):
        return f"<EnvironmentRecord(id={self.id}, plot_id={self.plot_id}, year={self.year})>"
