# -*- coding: utf-8 -*-
"""
数据验证模型模块
================
包含所有Pydantic数据模型
用于API请求参数验证和响应数据序列化
"""

from app.schemas.suppliers import SupplierBase, SupplierCreate, SupplierUpdate, SupplierResponse
from app.schemas.raw_materials import RawMaterialBase, RawMaterialCreate, RawMaterialUpdate, RawMaterialResponse
from app.schemas.material_inspections import (
    MaterialInspectionBase,
    MaterialInspectionCreate,
    MaterialInspectionUpdate,
    MaterialInspectionResponse,
)
from app.schemas.mix_designs import MixDesignBase, MixDesignCreate, MixDesignUpdate, MixDesignResponse
from app.schemas.production_batches import (
    ProductionBatchBase,
    ProductionBatchCreate,
    ProductionBatchUpdate,
    ProductionBatchResponse,
)
from app.schemas.production_records import (
    ProductionRecordBase,
    ProductionRecordCreate,
    ProductionRecordUpdate,
    ProductionRecordResponse,
)
from app.schemas.test_blocks import TestBlockBase, TestBlockCreate, TestBlockUpdate, TestBlockResponse
from app.schemas.strength_tests import StrengthTestBase, StrengthTestCreate, StrengthTestUpdate, StrengthTestResponse
from app.schemas.quality_reports import QualityReportBase, QualityReportCreate, QualityReportUpdate, QualityReportResponse
from app.schemas.supplier_ratings import SupplierRatingBase, SupplierRatingCreate, SupplierRatingUpdate, SupplierRatingResponse
from app.schemas.settlement_orders import SettlementOrderBase, SettlementOrderCreate, SettlementOrderUpdate, SettlementOrderResponse

__all__ = [
    # 供应商
    "SupplierBase",
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierResponse",
    # 原材料
    "RawMaterialBase",
    "RawMaterialCreate",
    "RawMaterialUpdate",
    "RawMaterialResponse",
    # 原材料检验
    "MaterialInspectionBase",
    "MaterialInspectionCreate",
    "MaterialInspectionUpdate",
    "MaterialInspectionResponse",
    # 配比设计
    "MixDesignBase",
    "MixDesignCreate",
    "MixDesignUpdate",
    "MixDesignResponse",
    # 生产批次
    "ProductionBatchBase",
    "ProductionBatchCreate",
    "ProductionBatchUpdate",
    "ProductionBatchResponse",
    # 生产记录
    "ProductionRecordBase",
    "ProductionRecordCreate",
    "ProductionRecordUpdate",
    "ProductionRecordResponse",
    # 试块
    "TestBlockBase",
    "TestBlockCreate",
    "TestBlockUpdate",
    "TestBlockResponse",
    # 强度检测
    "StrengthTestBase",
    "StrengthTestCreate",
    "StrengthTestUpdate",
    "StrengthTestResponse",
    # 质量报告
    "QualityReportBase",
    "QualityReportCreate",
    "QualityReportUpdate",
    "QualityReportResponse",
    # 供应商评级
    "SupplierRatingBase",
    "SupplierRatingCreate",
    "SupplierRatingUpdate",
    "SupplierRatingResponse",
    # 结算单
    "SettlementOrderBase",
    "SettlementOrderCreate",
    "SettlementOrderUpdate",
    "SettlementOrderResponse",
]
