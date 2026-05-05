"""
数据模型模块
包含所有Pydantic数据模型定义
"""
from schemas.schemas import (
    UserBase, UserCreate, UserLogin, UserResponse, Token,
    MaterialBase, MaterialCreate, MaterialUpdate, MaterialResponse,
    MaterialInspectionBase, MaterialInspectionCreate, MaterialInspectionResponse,
    ProductionFormulaBase, ProductionFormulaCreate, ProductionFormulaResponse,
    ProductionRecordBase, ProductionRecordCreate, ProductionRecordResponse,
    QualityAlertBase, QualityAlertCreate, QualityAlertUpdate, QualityAlertResponse,
    InspectionReportBase, InspectionReportCreate, InspectionReportResponse,
    FeedingRecordBase, FeedingRecordCreate, FeedingRecordResponse,
    QualityTraceResponse, ApiResponse, PaginatedResponse
)
