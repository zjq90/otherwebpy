"""
令牌数据模式
定义JWT令牌相关的Pydantic模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    令牌响应模型
    用于返回登录成功后的JWT令牌信息
    """
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒�?)
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class TokenPayload(BaseModel):
    """
    令牌载荷模型
    用于解析JWT令牌中的载荷信息
    """
    
    sub: Optional[str] = Field(None, description="主题（通常是用户ID�?)
    exp: Optional[int] = Field(None, description="过期时间�?)
    
    class Config:
        json_schema_extra = {
            "example": {
                "sub": "1",
                "exp": 1704067200
            }
        }
