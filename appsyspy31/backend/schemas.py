"""
Pydantic数据模型定义文件
用于API请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from models import (
    UserRole, Gender, MessageType, ChatType,
    CourseCategory, CourseType, BookingStatus,
    NutritionProductCategory, RecommendationType, RecommendationReason
)

# ========================================
# 通用响应模型
# ========================================

class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[dict] = Field(default=None, description="响应数据")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="操作成功", description="响应消息")
    data: dict = Field(description="分页数据")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")

# ========================================
# 用户相关模型
# ========================================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[Gender] = Field(default=Gender.OTHER, description="性别")
    role: Optional[UserRole] = Field(default=UserRole.MEMBER, description="用户角色")

class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")

class UserLogin(BaseModel):
    """用户登录模型"""
    username: Optional[str] = Field(None, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[Gender] = Field(None, description="性别")

class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(description="用户ID")
    is_active: bool = Field(description="是否激活")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间（秒）")
    user: UserResponse = Field(description="用户信息")

# ========================================
# 教练相关模型
# ========================================

class CoachBase(BaseModel):
    """教练基础模型"""
    specialization: Optional[str] = Field(None, max_length=200, description="专长领域")
    experience_years: Optional[int] = Field(default=0, ge=0, description="从业年限")
    certifications: Optional[str] = Field(None, description="资质证书")
    bio: Optional[str] = Field(None, description="个人简介")
    hourly_rate: Optional[float] = Field(default=200.0, gt=0, description="课时费")
    is_available: Optional[bool] = Field(default=True, description="是否可预约")

class CoachCreate(CoachBase):
    """教练创建模型"""
    user_id: int = Field(..., description="关联用户ID")

class CoachUpdate(CoachBase):
    """教练更新模型"""
    pass

class CoachResponse(CoachBase):
    """教练响应模型"""
    id: int = Field(description="教练ID")
    user_id: int = Field(description="关联用户ID")
    rating: float = Field(description="平均评分")
    review_count: int = Field(description="评价数量")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    user: Optional[UserResponse] = Field(None, description="用户信息")

    class Config:
        from_attributes = True

# ========================================
# 课程相关模型
# ========================================

class CourseBase(BaseModel):
    """课程基础模型"""
    name: str = Field(..., min_length=2, max_length=100, description="课程名称")
    description: Optional[str] = Field(None, description="课程描述")
    category: CourseCategory = Field(..., description="课程分类")
    course_type: Optional[CourseType] = Field(default=CourseType.GROUP, description="课程类型")
    duration: Optional[int] = Field(default=60, gt=0, description="课程时长（分钟）")
    difficulty_level: Optional[int] = Field(default=1, ge=1, le=5, description="难度等级（1-5）")
    calories_burned: Optional[int] = Field(None, ge=0, description="预计消耗卡路里")
    image_url: Optional[str] = Field(None, max_length=255, description="课程图片URL")

class CourseCreate(CourseBase):
    """课程创建模型"""
    pass

class CourseUpdate(CourseBase):
    """课程更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="课程名称")
    category: Optional[CourseCategory] = Field(None, description="课程分类")

class CourseResponse(CourseBase):
    """课程响应模型"""
    id: int = Field(description="课程ID")
    is_active: bool = Field(description="是否启用")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

# ========================================
# 会员偏好相关模型
# ========================================

class MemberPreferenceBase(BaseModel):
    """会员偏好基础模型"""
    preferred_categories: Optional[str] = Field(None, max_length=255, description="偏好的课程分类")
    preferred_course_types: Optional[str] = Field(None, max_length=100, description="偏好的课程类型")
    preferred_difficulty: Optional[int] = Field(default=2, ge=1, le=5, description="偏好的难度等级")
    training_frequency_per_week: Optional[int] = Field(default=3, ge=0, description="每周训练次数")
    preferred_training_days: Optional[str] = Field(None, max_length=100, description="偏好的训练日")
    preferred_training_time: Optional[str] = Field(None, max_length=50, description="偏好的训练时间段")
    fitness_goals: Optional[str] = Field(None, max_length=255, description="健身目标")
    target_weight: Optional[float] = Field(None, gt=0, description="目标体重")
    current_weight: Optional[float] = Field(None, gt=0, description="当前体重")
    height: Optional[float] = Field(None, gt=0, description="身高")
    has_injuries: Optional[bool] = Field(default=False, description="是否有伤病史")
    injury_details: Optional[str] = Field(None, description="伤病详情")
    preferred_coach_gender: Optional[Gender] = Field(None, description="偏好的教练性别")

class MemberPreferenceCreate(MemberPreferenceBase):
    """会员偏好创建模型"""
    user_id: int = Field(..., description="关联用户ID")

class MemberPreferenceUpdate(MemberPreferenceBase):
    """会员偏好更新模型"""
    pass

class MemberPreferenceResponse(MemberPreferenceBase):
    """会员偏好响应模型"""
    id: int = Field(description="偏好ID")
    user_id: int = Field(description="关联用户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

# ========================================
# 预约相关模型
# ========================================

class BookingBase(BaseModel):
    """预约基础模型"""
    booking_date: date = Field(..., description="预约日期")
    start_time: str = Field(..., min_length=5, max_length=20, description="开始时间（如：09:00）")
    end_time: str = Field(..., min_length=5, max_length=20, description="结束时间（如：10:00）")
    notes: Optional[str] = Field(None, description="备注")

class BookingCreate(BookingBase):
    """预约创建模型"""
    user_id: int = Field(..., description="会员ID")
    course_id: int = Field(..., description="课程ID")
    coach_id: Optional[int] = Field(None, description="教练ID（私教课必填）")

class BookingUpdate(BaseModel):
    """预约更新模型"""
    status: Optional[BookingStatus] = Field(None, description="预约状态")
    notes: Optional[str] = Field(None, description="备注")

class BookingResponse(BookingBase):
    """预约响应模型"""
    id: int = Field(description="预约ID")
    user_id: int = Field(description="会员ID")
    course_id: int = Field(description="课程ID")
    coach_id: Optional[int] = Field(None, description="教练ID")
    status: BookingStatus = Field(description="预约状态")
    reminder_sent: bool = Field(description="是否已发送提醒")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    user: Optional[UserResponse] = Field(None, description="用户信息")
    course: Optional[CourseResponse] = Field(None, description="课程信息")

    class Config:
        from_attributes = True

# ========================================
# 消息相关模型
# ========================================

class MessageBase(BaseModel):
    """消息基础模型"""
    message_type: MessageType = Field(..., description="消息类型")
    title: str = Field(..., min_length=1, max_length=200, description="消息标题")
    content: str = Field(..., min_length=1, description="消息内容")
    image_url: Optional[str] = Field(None, max_length=255, description="消息图片URL")
    link_url: Optional[str] = Field(None, max_length=255, description="跳转链接")
    related_id: Optional[int] = Field(None, description="关联数据ID")
    related_type: Optional[str] = Field(None, max_length=50, description="关联数据类型")

class MessageCreate(MessageBase):
    """消息创建模型"""
    user_id: int = Field(..., description="接收用户ID")

class MessageUpdate(BaseModel):
    """消息更新模型"""
    is_read: Optional[bool] = Field(None, description="是否已读")

class MessageResponse(MessageBase):
    """消息响应模型"""
    id: int = Field(description="消息ID")
    user_id: int = Field(description="接收用户ID")
    is_read: bool = Field(description="是否已读")
    read_at: Optional[datetime] = Field(None, description="读取时间")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True

# ========================================
# 聊天相关模型
# ========================================

class ChatSessionBase(BaseModel):
    """聊天会话基础模型"""
    chat_type: Optional[ChatType] = Field(default=ChatType.CUSTOMER_SERVICE, description="聊天类型")
    subject: Optional[str] = Field(None, max_length=200, description="会话主题")

class ChatSessionCreate(ChatSessionBase):
    """聊天会话创建模型"""
    user_id: int = Field(..., description="用户ID（咨询者）")
    staff_id: int = Field(..., description="工作人员ID（客服/教练）")

class ChatSessionResponse(ChatSessionBase):
    """聊天会话响应模型"""
    id: int = Field(description="会话ID")
    user_id: int = Field(description="用户ID")
    staff_id: int = Field(description="工作人员ID")
    is_active: bool = Field(description="是否活跃")
    closed_at: Optional[datetime] = Field(None, description="关闭时间")
    last_message_at: datetime = Field(description="最后消息时间")
    created_at: datetime = Field(description="创建时间")
    user: Optional[UserResponse] = Field(None, description="用户信息")
    staff: Optional[UserResponse] = Field(None, description="工作人员信息")

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    """聊天消息基础模型"""
    message_type: Optional[str] = Field(default="text", max_length=20, description="消息类型")
    content: str = Field(..., min_length=1, description="消息内容")
    file_url: Optional[str] = Field(None, max_length=255, description="文件/图片URL")

class ChatMessageCreate(ChatMessageBase):
    """聊天消息创建模型"""
    session_id: int = Field(..., description="会话ID")
    sender_id: int = Field(..., description="发送者ID")

class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应模型"""
    id: int = Field(description="消息ID")
    session_id: int = Field(description="会话ID")
    sender_id: int = Field(description="发送者ID")
    is_read: bool = Field(description="是否已读")
    read_at: Optional[datetime] = Field(None, description="读取时间")
    created_at: datetime = Field(description="发送时间")
    sender: Optional[UserResponse] = Field(None, description="发送者信息")

    class Config:
        from_attributes = True

# ========================================
# 评价相关模型
# ========================================

class ReviewBase(BaseModel):
    """评价基础模型"""
    rating: int = Field(..., ge=1, le=5, description="总体评分（1-5）")
    professionalism_rating: Optional[int] = Field(default=5, ge=1, le=5, description="专业度评分")
    punctuality_rating: Optional[int] = Field(default=5, ge=1, le=5, description="准时度评分")
    attitude_rating: Optional[int] = Field(default=5, ge=1, le=5, description="态度评分")
    content: Optional[str] = Field(None, description="文字评价")
    image_urls: Optional[str] = Field(None, description="评价图片URL（逗号分隔）")
    is_anonymous: Optional[bool] = Field(default=False, description="是否匿名评价")

class ReviewCreate(ReviewBase):
    """评价创建模型"""
    user_id: int = Field(..., description="评价者ID")
    coach_id: int = Field(..., description="被评价教练ID")
    booking_id: int = Field(..., description="关联预约ID")

class ReviewUpdate(BaseModel):
    """评价更新模型"""
    content: Optional[str] = Field(None, description="文字评价")
    image_urls: Optional[str] = Field(None, description="评价图片URL（逗号分隔）")

class CoachReplyUpdate(BaseModel):
    """教练回复模型"""
    coach_reply: str = Field(..., min_length=1, description="教练回复内容")

class ReviewResponse(ReviewBase):
    """评价响应模型"""
    id: int = Field(description="评价ID")
    user_id: int = Field(description="评价者ID")
    coach_id: int = Field(description="被评价教练ID")
    booking_id: int = Field(description="关联预约ID")
    is_visible: bool = Field(description="是否可见")
    coach_reply: Optional[str] = Field(None, description="教练回复")
    coach_reply_at: Optional[datetime] = Field(None, description="教练回复时间")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    user: Optional[UserResponse] = Field(None, description="用户信息")
    coach: Optional[CoachResponse] = Field(None, description="教练信息")

    class Config:
        from_attributes = True

# ========================================
# 营养产品相关模型
# ========================================

class NutritionProductBase(BaseModel):
    """营养产品基础模型"""
    name: str = Field(..., min_length=1, max_length=150, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    category: NutritionProductCategory = Field(..., description="产品分类")
    description: Optional[str] = Field(None, description="产品描述")
    price: float = Field(..., gt=0, description="价格")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    stock: Optional[int] = Field(default=0, ge=0, description="库存")
    unit: Optional[str] = Field(default="件", max_length=20, description="单位")
    suitable_for: Optional[str] = Field(None, max_length=255, description="适用人群")
    benefits: Optional[str] = Field(None, description="功效说明")
    usage_method: Optional[str] = Field(None, description="使用方法")
    image_url: Optional[str] = Field(None, max_length=255, description="主图URL")
    image_urls: Optional[str] = Field(None, description="详情图片URL（逗号分隔）")
    is_recommended: Optional[bool] = Field(default=False, description="是否推荐")

class NutritionProductCreate(NutritionProductBase):
    """营养产品创建模型"""
    pass

class NutritionProductUpdate(NutritionProductBase):
    """营养产品更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=150, description="产品名称")
    category: Optional[NutritionProductCategory] = Field(None, description="产品分类")
    price: Optional[float] = Field(None, gt=0, description="价格")
    stock: Optional[int] = Field(None, ge=0, description="库存")
    is_active: Optional[bool] = Field(None, description="是否上架")

class NutritionProductResponse(NutritionProductBase):
    """营养产品响应模型"""
    id: int = Field(description="产品ID")
    is_active: bool = Field(description="是否上架")
    rating: float = Field(description="平均评分")
    review_count: int = Field(description="评价数量")
    sales_count: int = Field(description="销量")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

# ========================================
# 推荐相关模型
# ========================================

class RecommendationBase(BaseModel):
    """推荐基础模型"""
    recommendation_type: RecommendationType = Field(..., description="推荐类型")
    reason: Optional[RecommendationReason] = Field(default=RecommendationReason.PERSONAL, description="推荐原因")
    explanation: Optional[str] = Field(None, description="推荐解释")

class RecommendationCreate(RecommendationBase):
    """推荐创建模型"""
    user_id: int = Field(..., description="会员ID")
    course_id: Optional[int] = Field(None, description="推荐课程ID")
    coach_id: Optional[int] = Field(None, description="推荐教练ID")
    product_id: Optional[int] = Field(None, description="推荐产品ID")

class RecommendationResponse(RecommendationBase):
    """推荐响应模型"""
    id: int = Field(description="推荐ID")
    user_id: int = Field(description="会员ID")
    course_id: Optional[int] = Field(None, description="推荐课程ID")
    coach_id: Optional[int] = Field(None, description="推荐教练ID")
    product_id: Optional[int] = Field(None, description="推荐产品ID")
    score: float = Field(description="推荐分数")
    is_viewed: bool = Field(description="是否已查看")
    is_clicked: bool = Field(description="是否已点击")
    is_purchased: bool = Field(description="是否已购买/预约")
    created_at: datetime = Field(description="创建时间")
    course: Optional[CourseResponse] = Field(None, description="课程信息")
    coach: Optional[CoachResponse] = Field(None, description="教练信息")
    product: Optional[NutritionProductResponse] = Field(None, description="产品信息")

    class Config:
        from_attributes = True
