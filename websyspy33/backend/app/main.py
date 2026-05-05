# -*- coding: utf-8 -*-
"""
FastAPI主应用入口
==================
混凝土质量管理系统 - 后端API服务器
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    await init_db()
    yield


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["供应商管理"])
app.include_router(raw_materials.router, prefix="/api/raw-materials", tags=["原材料管理"])
app.include_router(material_inspections.router, prefix="/api/material-inspections", tags=["原材料检验"])
app.include_router(mix_designs.router, prefix="/api/mix-designs", tags=["配比设计"])
app.include_router(production_batches.router, prefix="/api/production-batches", tags=["生产批次"])
app.include_router(production_records.router, prefix="/api/production-records", tags=["生产记录"])
app.include_router(test_blocks.router, prefix="/api/test-blocks", tags=["成品试块"])
app.include_router(strength_tests.router, prefix="/api/strength-tests", tags=["强度检测"])
app.include_router(quality_reports.router, prefix="/api/quality-reports", tags=["质量报告"])
app.include_router(supplier_ratings.router, prefix="/api/supplier-ratings", tags=["供应商评级"])
app.include_router(settlement_orders.router, prefix="/api/settlement-orders", tags=["结算管理"])


@app.get("/")
async def root():
    """
    根路径
    返回系统基本信息
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy"}
