"""
系统配置模块
使用Pydantic Settings管理环境变量和配置项
支持环境变量覆盖配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    应用配置类
    
    所有配置项都可以通过环境变量进行覆盖
    例如: 设置环境变量 DATABASE_URL 可以覆盖默认的数据库路径
    """

    # ==================== 应用基础配置 ====================
    APP_NAME: str = "高并发抢单系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ==================== 数据库配置 ====================
    # SQLite数据库文件路径
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/seckill.db"
    # 数据库连接池大小
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # ==================== Redis配置 ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_CONNECTION_POOL_SIZE: int = 50

    # ==================== JWT身份认证配置 ====================
    # 密钥: 生产环境应该使用强随机字符串
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    # Token过期时间(秒): 2小时
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 7200

    # ==================== 限流配置 ====================
    # 全局每秒最大请求数
    GLOBAL_RATE_LIMIT_PER_SECOND: int = 10000
    # 单个IP每秒最大请求数
    IP_RATE_LIMIT_PER_SECOND: int = 10
    # 单个用户每秒最大请求数
    USER_RATE_LIMIT_PER_SECOND: int = 5

    # ==================== 抢单活动配置 ====================
    # 活动开始时间(格式: YYYY-MM-DD HH:MM:SS)
    # 为空表示立即开始
    SECKILL_START_TIME: Optional[str] = None
    # 活动结束时间
    SECKILL_END_TIME: Optional[str] = None
    # 每个用户限购数量
    MAX_PURCHASE_PER_USER: int = 1

    # ==================== 异步队列配置 ====================
    # 异步写入队列大小
    ASYNC_QUEUE_MAX_SIZE: int = 10000
    # 异步处理worker数量
    ASYNC_WORKER_COUNT: int = 5
    # 批量写入数据库的批次大小
    DB_BATCH_WRITE_SIZE: int = 100

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "./logs/app.log"

    class Config:
        """Pydantic配置类"""
        # 环境变量文件
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 忽略额外的环境变量
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    
    使用lru_cache确保整个应用只创建一个Settings实例
    提高性能并保证配置一致性
    
    Returns:
        Settings: 配置对象
    """
    return Settings()


# 导出配置实例
settings = get_settings()
