# -*- coding: utf-8 -*-
"""
数据库模型定义
==============
包含所有业务相关的数据表模型

表结构设计：
1. suppliers - 供应商表
2. raw_materials - 原材料表
3. material_inspections - 原材料检验记录表
4. mix_designs - 配比设计表
5. production_batches - 生产批次表
6. production_records - 生产记录表
7. test_blocks - 成品试块表
8. strength_tests - 强度检测表
9. quality_reports - 质量报告表
10. supplier_ratings - 供应商评级表
11. settlement_orders - 结算单表
"""

import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Supplier(Base):
    """
    供应商表
    存储供应商基本信息，用于供应商评级和结算管理
    """
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="供应商ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="供应商名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="供应商编码")
    contact_person: Mapped[Optional[str]] = mapped_column(String(50), comment="联系人")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="联系电话")
    address: Mapped[Optional[str]] = mapped_column(Text, comment="地址")
    supplier_type: Mapped[str] = mapped_column(String(50), default="原材料供应商", comment="供应商类型")
    rating: Mapped[Optional[float]] = mapped_column(Float, comment="综合评分(0-100)")
    rating_level: Mapped[Optional[str]] = mapped_column(String(20), comment="评级等级(A/B/C/D)")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态(是否启用)")
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    raw_materials = relationship("RawMaterial", back_populates="supplier")
    material_inspections = relationship("MaterialInspection", back_populates="supplier")
    supplier_ratings = relationship("SupplierRating", back_populates="supplier")
    settlement_orders = relationship("SettlementOrder", back_populates="supplier")

    __table_args__ = (
        Index("ix_suppliers_code", "code"),
        Index("ix_suppliers_name", "name"),
    )


class RawMaterial(Base):
    """
    原材料表
    存储水泥、骨料、外加剂等原材料信息
    """
    __tablename__ = "raw_materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="原材料ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="原材料名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="原材料编码")
    material_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="材料类型(水泥/骨料/外加剂等)")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="计量单位")
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), comment="供应商ID")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    supplier = relationship("Supplier", back_populates="raw_materials")
    material_inspections = relationship("MaterialInspection", back_populates="raw_material")

    __table_args__ = (
        Index("ix_raw_materials_code", "code"),
        Index("ix_raw_materials_type", "material_type"),
    )


class MaterialInspection(Base):
    """
    原材料检验记录表
    实验室数据录入，对进场原材料进行质量检测
    """
    __tablename__ = "material_inspections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="检验记录ID")
    inspection_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="检验单号")
    material_id: Mapped[int] = mapped_column(ForeignKey("raw_materials.id"), nullable=False, comment="原材料ID")
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), comment="供应商ID")
    batch_no: Mapped[str] = mapped_column(String(50), comment="进场批次号")
    sample_no: Mapped[str] = mapped_column(String(50), comment="样品编号")
    sample_date: Mapped[datetime.date] = mapped_column(Date, comment="取样日期")
    inspector: Mapped[str] = mapped_column(String(50), comment="检验员")
    inspection_date: Mapped[datetime.date] = mapped_column(Date, comment="检验日期")
    
    # 检验项目 - 根据材料类型不同会有不同检验项目
    inspection_items: Mapped[Optional[str]] = mapped_column(Text, comment="检验项目(JSON格式)")
    test_data: Mapped[Optional[str]] = mapped_column(Text, comment="检测数据(JSON格式)")
    standard_value: Mapped[Optional[str]] = mapped_column(Text, comment="标准值(JSON格式)")
    
    # 检验结果
    result: Mapped[str] = mapped_column(String(20), default="待检", comment="检验结果(合格/不合格/待检)")
    conclusion: Mapped[Optional[str]] = mapped_column(Text, comment="检验结论")
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否合格")
    
    # 实验室数据
    lab_temperature: Mapped[Optional[float]] = mapped_column(Float, comment="实验室温度(℃)")
    lab_humidity: Mapped[Optional[float]] = mapped_column(Float, comment="实验室湿度(%)")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="草稿", comment="状态(草稿/已提交/已审核)")
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(50), comment="审核人")
    review_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="审核日期")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    raw_material = relationship("RawMaterial", back_populates="material_inspections")
    supplier = relationship("Supplier", back_populates="material_inspections")

    __table_args__ = (
        Index("ix_material_inspections_no", "inspection_no"),
        Index("ix_material_inspections_batch", "batch_no"),
        Index("ix_material_inspections_date", "inspection_date"),
    )


class MixDesign(Base):
    """
    配比设计表
    存储混凝土配合比设计信息
    """
    __tablename__ = "mix_designs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="配比设计ID")
    design_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="设计编号")
    mix_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="配合比名称")
    strength_grade: Mapped[str] = mapped_column(String(20), comment="强度等级")
    design_age: Mapped[int] = mapped_column(Integer, default=28, comment="设计龄期(天)")
    slump: Mapped[Optional[float]] = mapped_column(Float, comment="坍落度要求(mm)")
    
    # 配合比数据 - 每立方米材料用量
    cement_content: Mapped[float] = mapped_column(Float, comment="水泥用量(kg/m³)")
    sand_content: Mapped[float] = mapped_column(Float, comment="砂用量(kg/m³)")
    stone_content: Mapped[float] = mapped_column(Float, comment="石用量(kg/m³)")
    water_content: Mapped[float] = mapped_column(Float, comment="水用量(kg/m³)")
    admixture_content: Mapped[Optional[float]] = mapped_column(Float, comment="外加剂用量(kg/m³)")
    fly_ash_content: Mapped[Optional[float]] = mapped_column(Float, comment="粉煤灰用量(kg/m³)")
    
    # 配合比参数
    water_cement_ratio: Mapped[float] = mapped_column(Float, comment="水胶比")
    sand_ratio: Mapped[float] = mapped_column(Float, comment="砂率(%)")
    
    designed_by: Mapped[str] = mapped_column(String(50), comment="设计人")
    design_date: Mapped[datetime.date] = mapped_column(Date, comment="设计日期")
    approved_by: Mapped[Optional[str]] = mapped_column(String(50), comment="批准人")
    approval_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="批准日期")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="草稿", comment="状态(草稿/已审批/已启用)")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否启用")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    production_batches = relationship("ProductionBatch", back_populates="mix_design")

    __table_args__ = (
        Index("ix_mix_designs_no", "design_no"),
        Index("ix_mix_designs_strength", "strength_grade"),
    )


class ProductionBatch(Base):
    """
    生产批次表
    存储混凝土生产批次信息
    """
    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="生产批次ID")
    batch_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="生产批号")
    mix_design_id: Mapped[int] = mapped_column(ForeignKey("mix_designs.id"), comment="配比设计ID")
    project_name: Mapped[str] = mapped_column(String(200), comment="工程名称")
    construction_site: Mapped[str] = mapped_column(String(200), comment="施工部位")
    strength_grade: Mapped[str] = mapped_column(String(20), comment="强度等级")
    
    # 生产参数
    planned_volume: Mapped[float] = mapped_column(Float, comment="计划方量(m³)")
    actual_volume: Mapped[Optional[float]] = mapped_column(Float, comment="实际方量(m³)")
    
    # 时间信息
    production_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment="生产开始时间")
    production_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment="生产结束时间")
    
    # 运输信息
    truck_no: Mapped[Optional[str]] = mapped_column(String(50), comment="车号")
    driver: Mapped[Optional[str]] = mapped_column(String(50), comment="司机")
    
    operator: Mapped[str] = mapped_column(String(50), comment="操作员")
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="待生产", comment="状态(待生产/生产中/已完成)")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    mix_design = relationship("MixDesign", back_populates="production_batches")
    production_records = relationship("ProductionRecord", back_populates="production_batch")
    test_blocks = relationship("TestBlock", back_populates="production_batch")

    __table_args__ = (
        Index("ix_production_batches_no", "batch_no"),
        Index("ix_production_batches_date", "created_at"),
    )


class ProductionRecord(Base):
    """
    生产记录表
    实时采集搅拌时间、投料顺序、水胶比等关键参数
    """
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="生产记录ID")
    batch_id: Mapped[int] = mapped_column(ForeignKey("production_batches.id"), comment="生产批次ID")
    record_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="记录编号")
    mix_no: Mapped[int] = mapped_column(Integer, comment="盘数序号(第几盘)")
    
    # 搅拌参数
    mixing_time: Mapped[float] = mapped_column(Float, comment="搅拌时间(秒)")
    feeding_sequence: Mapped[Optional[str]] = mapped_column(Text, comment="投料顺序(JSON格式)")
    
    # 实际投料数据
    actual_cement: Mapped[float] = mapped_column(Float, comment="实际水泥用量(kg)")
    actual_sand: Mapped[float] = mapped_column(Float, comment="实际砂用量(kg)")
    actual_stone: Mapped[float] = mapped_column(Float, comment="实际石用量(kg)")
    actual_water: Mapped[float] = mapped_column(Float, comment="实际水用量(kg)")
    actual_admixture: Mapped[Optional[float]] = mapped_column(Float, comment="实际外加剂用量(kg)")
    actual_fly_ash: Mapped[Optional[float]] = mapped_column(Float, comment="实际粉煤灰用量(kg)")
    
    # 配合比参数
    actual_water_cement_ratio: Mapped[float] = mapped_column(Float, comment="实际水胶比")
    design_water_cement_ratio: Mapped[float] = mapped_column(Float, comment="设计水胶比")
    deviation_rate: Mapped[float] = mapped_column(Float, comment="偏差率(%)")
    
    # 检测参数
    slump_actual: Mapped[Optional[float]] = mapped_column(Float, comment="实际坍落度(mm)")
    temperature: Mapped[Optional[float]] = mapped_column(Float, comment="出机温度(℃)")
    
    # 质量判定
    is_normal: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否正常")
    anomaly_reason: Mapped[Optional[str]] = mapped_column(Text, comment="异常原因")
    
    operator: Mapped[str] = mapped_column(String(50), comment="操作员")
    record_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, comment="记录时间")
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    production_batch = relationship("ProductionBatch", back_populates="production_records")

    __table_args__ = (
        Index("ix_production_records_batch", "batch_id"),
        Index("ix_production_records_time", "record_time"),
    )


class TestBlock(Base):
    """
    成品试块表
    存储混凝土试块信息
    """
    __tablename__ = "test_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="试块ID")
    block_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="试块编号")
    batch_id: Mapped[int] = mapped_column(ForeignKey("production_batches.id"), comment="生产批次ID")
    
    # 试块信息
    sample_date: Mapped[datetime.date] = mapped_column(Date, comment="取样日期")
    casting_date: Mapped[datetime.date] = mapped_column(Date, comment="成型日期")
    test_age: Mapped[int] = mapped_column(Integer, comment="试验龄期(天)")
    planned_test_date: Mapped[datetime.date] = mapped_column(Date, comment="计划试验日期")
    
    # 试块规格
    block_size: Mapped[str] = mapped_column(String(50), default="150x150x150", comment="试块规格(mm)")
    quantity: Mapped[int] = mapped_column(Integer, default=3, comment="试块数量")
    
    # 养护条件
    curing_condition: Mapped[str] = mapped_column(String(50), default="标准养护", comment="养护条件")
    
    # 取样位置
    sample_location: Mapped[Optional[str]] = mapped_column(String(100), comment="取样部位")
    sampler: Mapped[str] = mapped_column(String(50), comment="取样人")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="待试验", comment="状态(待试验/已试验/已作废)")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    production_batch = relationship("ProductionBatch", back_populates="test_blocks")
    strength_tests = relationship("StrengthTest", back_populates="test_block")

    __table_args__ = (
        Index("ix_test_blocks_no", "block_no"),
        Index("ix_test_blocks_batch", "batch_id"),
    )


class StrengthTest(Base):
    """
    强度检测表
    存储混凝土试块强度检测结果
    """
    __tablename__ = "strength_tests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="强度检测ID")
    test_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="试验编号")
    block_id: Mapped[int] = mapped_column(ForeignKey("test_blocks.id"), comment="试块ID")
    
    test_date: Mapped[datetime.date] = mapped_column(Date, comment="试验日期")
    actual_age: Mapped[int] = mapped_column(Integer, comment="实际龄期(天)")
    tester: Mapped[str] = mapped_column(String(50), comment="试验人")
    
    # 试验环境
    lab_temperature: Mapped[Optional[float]] = mapped_column(Float, comment="实验室温度(℃)")
    lab_humidity: Mapped[Optional[float]] = mapped_column(Float, comment="实验室湿度(%)")
    
    # 试块破坏荷载数据
    load_1: Mapped[float] = mapped_column(Float, comment="试块1破坏荷载(kN)")
    load_2: Mapped[float] = mapped_column(Float, comment="试块2破坏荷载(kN)")
    load_3: Mapped[Optional[float]] = mapped_column(Float, comment="试块3破坏荷载(kN)")
    
    # 强度计算
    strength_1: Mapped[float] = mapped_column(Float, comment="试块1强度(MPa)")
    strength_2: Mapped[float] = mapped_column(Float, comment="试块2强度(MPa)")
    strength_3: Mapped[Optional[float]] = mapped_column(Float, comment="试块3强度(MPa)")
    
    avg_strength: Mapped[float] = mapped_column(Float, comment="平均强度(MPa)")
    strength_deviation: Mapped[Optional[float]] = mapped_column(Float, comment="强度偏差(%)")
    
    # 评定结果
    design_strength: Mapped[float] = mapped_column(Float, comment="设计强度值(MPa)")
    strength_ratio: Mapped[float] = mapped_column(Float, comment="强度比(%)")
    result: Mapped[str] = mapped_column(String(20), default="待评定", comment="结果(合格/不合格/待评定)")
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否合格")
    
    conclusion: Mapped[Optional[str]] = mapped_column(Text, comment="试验结论")
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="草稿", comment="状态(草稿/已提交/已审核)")
    
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(50), comment="审核人")
    review_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="审核日期")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    test_block = relationship("TestBlock", back_populates="strength_tests")

    __table_args__ = (
        Index("ix_strength_tests_no", "test_no"),
        Index("ix_strength_tests_block", "block_id"),
    )


class QualityReport(Base):
    """
    质量报告表
    生成可追溯的质量报告
    """
    __tablename__ = "quality_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="质量报告ID")
    report_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="报告编号")
    batch_id: Mapped[int] = mapped_column(ForeignKey("production_batches.id"), comment="生产批次ID")
    
    # 报告信息
    report_type: Mapped[str] = mapped_column(String(50), comment="报告类型(出厂合格证/质量追溯报告)")
    report_date: Mapped[datetime.date] = mapped_column(Date, comment="报告日期")
    generated_by: Mapped[str] = mapped_column(String(50), comment="生成人")
    
    # 关联数据
    material_inspection_ids: Mapped[Optional[str]] = mapped_column(Text, comment="关联原材料检验ID(逗号分隔)")
    production_record_ids: Mapped[Optional[str]] = mapped_column(Text, comment="关联生产记录ID(逗号分隔)")
    strength_test_ids: Mapped[Optional[str]] = mapped_column(Text, comment="关联强度试验ID(逗号分隔)")
    
    # 报告内容摘要
    summary: Mapped[Optional[str]] = mapped_column(Text, comment="报告摘要")
    conclusion: Mapped[Optional[str]] = mapped_column(Text, comment="报告结论")
    
    # 质量评定
    overall_result: Mapped[str] = mapped_column(String(20), default="待评定", comment="综合评定结果")
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否合格")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(String(20), default="草稿", comment="状态(草稿/已发布/已作废)")
    
    approved_by: Mapped[Optional[str]] = mapped_column(String(50), comment="批准人")
    approval_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="批准日期")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    __table_args__ = (
        Index("ix_quality_reports_no", "report_no"),
        Index("ix_quality_reports_batch", "batch_id"),
    )


class SupplierRating(Base):
    """
    供应商评级表
    对供应商的供货及时性、材料质量建立评分机制
    """
    __tablename__ = "supplier_ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="评级记录ID")
    rating_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="评级编号")
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), comment="供应商ID")
    
    # 评级周期
    rating_period: Mapped[str] = mapped_column(String(50), comment="评级周期(如:2024年第一季度)")
    rating_date: Mapped[datetime.date] = mapped_column(Date, comment="评级日期")
    
    # 评分项 - 满分100
    quality_score: Mapped[float] = mapped_column(Float, comment="材料质量评分(0-40)")
    delivery_score: Mapped[float] = mapped_column(Float, comment="供货及时性评分(0-30)")
    price_score: Mapped[float] = mapped_column(Float, comment="价格合理性评分(0-20)")
    service_score: Mapped[float] = mapped_column(Float, comment="售后服务评分(0-10)")
    
    # 综合评分
    total_score: Mapped[float] = mapped_column(Float, comment="综合评分(0-100)")
    
    # 评级标准
    # A级: 90-100分
    # B级: 75-89分
    # C级: 60-74分
    # D级: 0-59分
    rating_level: Mapped[str] = mapped_column(String(20), comment="评级等级(A/B/C/D)")
    
    # 统计数据
    inspection_count: Mapped[int] = mapped_column(Integer, default=0, comment="检验批次数量")
    pass_rate: Mapped[float] = mapped_column(Float, default=100.0, comment="合格率(%)")
    delivery_count: Mapped[int] = mapped_column(Integer, default=0, comment="供货次数")
    on_time_rate: Mapped[float] = mapped_column(Float, default=100.0, comment="准时率(%)")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="评级说明")
    rater: Mapped[str] = mapped_column(String(50), comment="评级人")
    status: Mapped[str] = mapped_column(String(20), default="草稿", comment="状态(草稿/已生效)")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    supplier = relationship("Supplier", back_populates="supplier_ratings")

    __table_args__ = (
        Index("ix_supplier_ratings_no", "rating_no"),
        Index("ix_supplier_ratings_supplier", "supplier_id"),
        Index("ix_supplier_ratings_period", "rating_period"),
    )


class SettlementOrder(Base):
    """
    结算单表
    自动生成供应商结算单
    """
    __tablename__ = "settlement_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="结算单ID")
    settlement_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="结算单号")
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), comment="供应商ID")
    
    # 结算周期
    settlement_period: Mapped[str] = mapped_column(String(50), comment="结算周期")
    start_date: Mapped[datetime.date] = mapped_column(Date, comment="开始日期")
    end_date: Mapped[datetime.date] = mapped_column(Date, comment="结束日期")
    
    # 结算明细 - 按材料类型汇总
    material_summary: Mapped[Optional[str]] = mapped_column(Text, comment="材料汇总(JSON格式)")
    
    # 金额
    total_quantity: Mapped[float] = mapped_column(Float, comment="总数量")
    total_amount: Mapped[float] = mapped_column(Float, comment="总金额(元)")
    discount_amount: Mapped[Optional[float]] = mapped_column(Float, comment="优惠金额(元)")
    final_amount: Mapped[float] = mapped_column(Float, comment="应付金额(元)")
    
    # 结算状态
    status: Mapped[str] = mapped_column(String(20), default="待确认", comment="状态(待确认/已确认/已付款)")
    
    created_by: Mapped[str] = mapped_column(String(50), comment="制单人")
    created_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today, comment="制单日期")
    
    confirmed_by: Mapped[Optional[str]] = mapped_column(String(50), comment="确认人")
    confirm_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="确认日期")
    
    paid_by: Mapped[Optional[str]] = mapped_column(String(50), comment="付款人")
    paid_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment="付款日期")
    
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间"
    )

    # 关联关系
    supplier = relationship("Supplier", back_populates="settlement_orders")

    __table_args__ = (
        Index("ix_settlement_orders_no", "settlement_no"),
        Index("ix_settlement_orders_supplier", "supplier_id"),
        Index("ix_settlement_orders_date", "created_date"),
    )
