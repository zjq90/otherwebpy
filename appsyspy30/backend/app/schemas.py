"""
Pydantic数据模型模块
用于API的请求参数验证和响应数据序列化
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserCreate(UserBase):
    """用户注册模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    invite_code: Optional[str] = Field(None, description="邀请码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    avatar: Optional[str] = None
    points: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    """用户公开信息模型（用于好友查看等场景）"""
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    points: int

    class Config:
        orm_mode = True


# ==================== Token相关模型 ====================

class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[int] = None


# ==================== 动态相关模型 ====================

class PostBase(BaseModel):
    """动态基础模型"""
    content: str = Field(..., min_length=1, description="动态内容")
    post_type: str = Field(default="training", description="动态类型: training, diet, achievement")
    images: Optional[str] = Field(None, description="图片URL列表(逗号分隔)")
    is_public: bool = Field(default=True, description="是否公开")


class PostCreate(PostBase):
    """动态创建模型"""
    pass


class PostUpdate(BaseModel):
    """动态更新模型"""
    content: Optional[str] = None
    post_type: Optional[str] = None
    images: Optional[str] = None
    is_public: Optional[bool] = None


class PostResponse(PostBase):
    """动态响应模型"""
    id: int
    user_id: int
    likes_count: int
    comments_count: int
    shares_count: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserPublic] = None
    is_liked: Optional[bool] = None

    class Config:
        orm_mode = True


# ==================== 点赞相关模型 ====================

class LikeResponse(BaseModel):
    """点赞响应模型"""
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    user: Optional[UserPublic] = None

    class Config:
        orm_mode = True


# ==================== 评论相关模型 ====================

class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., min_length=1, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID")


class CommentCreate(CommentBase):
    """评论创建模型"""
    post_id: int = Field(..., description="动态ID")


class CommentResponse(CommentBase):
    """评论响应模型"""
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    user: Optional[UserPublic] = None

    class Config:
        orm_mode = True


# ==================== 好友关系相关模型 ====================

class FriendshipCreate(BaseModel):
    """好友关系创建模型"""
    user_id_2: int = Field(..., description="要添加的用户ID")


class FriendshipResponse(BaseModel):
    """好友关系响应模型"""
    id: int
    user_id_1: int
    user_id_2: int
    status: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserPublic] = None

    class Config:
        orm_mode = True


# ==================== 私信相关模型 ====================

class MessageBase(BaseModel):
    """私信基础模型"""
    content: str = Field(..., min_length=1, description="消息内容")


class MessageCreate(MessageBase):
    """私信创建模型"""
    receiver_id: int = Field(..., description="接收者ID")


class MessageResponse(MessageBase):
    """私信响应模型"""
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime
    sender: Optional[UserPublic] = None
    receiver: Optional[UserPublic] = None

    class Config:
        orm_mode = True


class MessageConversation(BaseModel):
    """会话列表模型"""
    user: UserPublic
    last_message: MessageResponse
    unread_count: int


# ==================== 挑战活动相关模型 ====================

class ChallengeBase(BaseModel):
    """挑战活动基础模型"""
    title: str = Field(..., max_length=100, description="活动标题")
    description: str = Field(..., description="活动描述")
    challenge_type: str = Field(..., description="挑战类型")
    duration_days: int = Field(..., gt=0, description="活动持续天数")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    reward_points: int = Field(default=0, ge=0, description="奖励积分")
    reward_description: Optional[str] = Field(None, description="奖励描述")
    max_participants: Optional[int] = Field(None, gt=0, description="最大参与人数")


class ChallengeCreate(ChallengeBase):
    """挑战活动创建模型"""
    pass


class ChallengeResponse(ChallengeBase):
    """挑战活动响应模型"""
    id: int
    current_participants: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ==================== 用户挑战参与相关模型 ====================

class UserChallengeCreate(BaseModel):
    """用户挑战参与创建模型"""
    challenge_id: int = Field(..., description="挑战活动ID")


class UserChallengeUpdate(BaseModel):
    """用户挑战进度更新模型"""
    progress: float = Field(..., ge=0, le=100, description="完成进度")
    daily_data: Optional[str] = Field(None, description="每日数据(JSON)")


class UserChallengeResponse(BaseModel):
    """用户挑战响应模型"""
    id: int
    user_id: int
    challenge_id: int
    progress: float
    daily_data: Optional[str]
    is_completed: bool
    reward_claimed: bool
    joined_at: datetime
    completed_at: Optional[datetime]
    challenge: Optional[ChallengeResponse] = None

    class Config:
        orm_mode = True


# ==================== 邀请记录相关模型 ====================

class InvitationCreate(BaseModel):
    """邀请创建模型"""
    invitee_phone: Optional[str] = Field(None, description="被邀请者手机号")
    invitee_email: Optional[str] = Field(None, description="被邀请者邮箱")


class InvitationCode(BaseModel):
    """邀请码模型"""
    invite_code: str = Field(..., description="邀请码")


class InvitationResponse(BaseModel):
    """邀请响应模型"""
    id: int
    inviter_id: int
    invitee_id: Optional[int]
    invite_code: str
    invitee_phone: Optional[str]
    invitee_email: Optional[str]
    status: str
    reward_points: int
    reward_description: Optional[str]
    created_at: datetime
    updated_at: datetime
    invitee: Optional[UserPublic] = None

    class Config:
        orm_mode = True


# ==================== 通用响应模型 ====================

class APIResponse(BaseModel):
    """通用API响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
