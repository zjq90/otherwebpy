# -*- coding: utf-8 -*-
"""
API路由模块
===========
包含所有业务模块的API路由

路由模块列表：
- suppliers: 供应商管理
- raw_materials: 原材料管理
- material_inspections: 原材料检验
- mix_designs: 配比设计
- production_batches: 生产批次
- production_records: 生产记录
- test_blocks: 成品试块
- strength_tests: 强度检测
- quality_reports: 质量报告
- supplier_ratings: 供应商评级
- settlement_orders: 结算管理
"""

from app.routers import (
    suppliers,
    raw_materials,
    material_inspections,
    mix_designs,
    production_batches,
    production_records,
    test_blocks,
    strength_tests,
    quality_reports,
    supplier_ratings,
    settlement_orders,
)

__all__ = [
    "suppliers",
    "raw_materials",
    "material_inspections",
    "mix_designs",
    "production_batches",
    "production_records",
    "test_blocks",
    "strength_tests",
    "quality_reports",
    "supplier_ratings",
    "settlement_orders",
]
