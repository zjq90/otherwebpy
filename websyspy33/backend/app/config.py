# -*- coding: utf-8 -*-
"""
系统配置模块
============
包含数据库连接配置、API配置等
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """系统配置类"""
    
    # 项目基础路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/quality_management.db"
    
    # API配置
    API_TITLE: str = "混凝土质量管理系统 API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = """
    混凝土质量管理系统 - 后端API接口
    
    ## 功能模块
    1. 原材料检验
    2. 生产质量追踪
    3. 成品质量检验与报告生成
    4. 供应商评级与结算管理
    """
    
    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# 全局配置实例
settings = Settings()
