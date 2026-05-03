"""
Pydantic模型定义模块
用于API请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== 用户相关模型 ====================

PHONE_REGEX = r'^1[3-9]\d{9}$'

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    phone: Optional[str] = Field(
        None, 
        pattern=PHONE_REGEX,
        max_length=20, 
        description="手机号（中国大陆手机号格式）"
    )


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=64, description="密码（最大64个字符）")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None


# ==================== 产品相关模型 ====================

class ProductBase(BaseModel):
    """产品基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    short_desc: Optional[str] = Field(None, max_length=500, description="产品简短描述")
    description: Optional[str] = Field(None, description="产品详细描述")
    image_url: Optional[str] = Field(None, max_length=255, description="产品图片URL")
    price: Optional[str] = Field(None, max_length=50, description="产品价格")
    category: Optional[str] = Field(None, max_length=50, description="产品分类")
    sort_order: Optional[int] = Field(0, description="排序权重")


class ProductCreate(ProductBase):
    """产品创建模型"""
    pass


class ProductUpdate(ProductBase):
    """产品更新模型"""
    is_active: Optional[bool] = Field(None, description="是否上架")


class ProductResponse(ProductBase):
    """产品响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 服务相关模型 ====================

class ServiceBase(BaseModel):
    """服务基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="服务名称")
    short_desc: Optional[str] = Field(None, max_length=500, description="服务简短描述")
    description: Optional[str] = Field(None, description="服务详细描述")
    icon: Optional[str] = Field(None, max_length=100, description="服务图标")
    image_url: Optional[str] = Field(None, max_length=255, description="服务图片URL")
    sort_order: Optional[int] = Field(0, description="排序权重")


class ServiceCreate(ServiceBase):
    """服务创建模型"""
    pass


class ServiceUpdate(ServiceBase):
    """服务更新模型"""
    is_active: Optional[bool] = Field(None, description="是否启用")


class ServiceResponse(ServiceBase):
    """服务响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 案例相关模型 ====================

class CaseBase(BaseModel):
    """案例基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="案例标题")
    short_desc: Optional[str] = Field(None, max_length=500, description="案例简短描述")
    description: Optional[str] = Field(None, description="案例详细描述")
    content: Optional[str] = Field(None, description="案例详细内容")
    image_url: Optional[str] = Field(None, max_length=255, description="案例封面图片")
    client: Optional[str] = Field(None, max_length=100, description="客户名称")
    category: Optional[str] = Field(None, max_length=50, description="案例分类")
    is_featured: Optional[bool] = Field(False, description="是否推荐")
    sort_order: Optional[int] = Field(0, description="排序权重")


class CaseCreate(CaseBase):
    """案例创建模型"""
    pass


class CaseUpdate(CaseBase):
    """案例更新模型"""
    is_active: Optional[bool] = Field(None, description="是否启用")


class CaseResponse(CaseBase):
    """案例响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 文档相关模型 ====================

class DocumentBase(BaseModel):
    """文档基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    short_desc: Optional[str] = Field(None, max_length=500, description="文档简短描述")
    description: Optional[str] = Field(None, description="文档简介")
    content: Optional[str] = Field(None, description="文档内容")
    category: Optional[str] = Field(None, max_length=50, description="文档分类")
    tags: Optional[str] = Field(None, max_length=500, description="文档标签")
    file_url: Optional[str] = Field(None, max_length=255, description="文档附件URL")
    sort_order: Optional[int] = Field(0, description="排序权重")


class DocumentCreate(DocumentBase):
    """文档创建模型"""
    pass


class DocumentUpdate(DocumentBase):
    """文档更新模型"""
    is_active: Optional[bool] = Field(None, description="是否启用")


class DocumentResponse(DocumentBase):
    """文档响应模型"""
    id: int
    view_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 秘钥申请相关模型 ====================

class KeyApplicationBase(BaseModel):
    """秘钥申请基础模型"""
    application_type: str = Field(default="trial", description="申请类型：trial(试用版), basic(基础版), pro(专业版), enterprise(企业版)")
    company_name: Optional[str] = Field(None, max_length=200, description="公司名称")
    website: Optional[str] = Field(None, max_length=255, description="公司网站")
    use_case: str = Field(..., description="使用场景说明")
    expected_calls: Optional[str] = Field(None, max_length=50, description="预计API调用量")


class KeyApplicationCreate(KeyApplicationBase):
    """秘钥申请创建模型"""
    pass


class KeyApplicationUpdate(BaseModel):
    """秘钥申请更新模型（管理员用）"""
    status: Optional[str] = Field(None, description="申请状态")
    review_notes: Optional[str] = Field(None, description="审核备注")


class KeyApplicationResponse(KeyApplicationBase):
    """秘钥申请响应模型"""
    id: int
    user_id: int
    status: str
    api_key: Optional[str]
    valid_until: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 通用响应模型 ====================

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
