"""
Pydantic模型定义模块
用于API请求参数验证和响应数据序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GoalTypeEnum(str, Enum):
    """
    目标类型枚举
    """
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    shape = "shape"
    endurance = "endurance"


class GoalStatusEnum(str, Enum):
    """
    目标状态枚举
    """
    active = "active"
    completed = "completed"
    failed = "failed"


class GenderEnum(str, Enum):
    """
    性别枚举
    """
    male = "male"
    female = "female"


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像路径")
    gender: Optional[GenderEnum] = Field(None, description="性别")
    birthday: Optional[datetime] = Field(None, description="生日")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=6, max_length=255, description="密码")


class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像路径")
    gender: Optional[GenderEnum] = Field(None, description="性别")
    birthday: Optional[datetime] = Field(None, description="生日")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="密码")


class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


# ==================== 体测记录相关模型 ====================

class BodyMeasurementBase(BaseModel):
    """
    体测记录基础模型
    """
    weight: float = Field(..., gt=0, description="体重(kg)")
    body_fat_rate: float = Field(..., ge=0, le=100, description="体脂率(%)")
    muscle_mass: float = Field(..., gt=0, description="肌肉量(kg)")
    bmi: Optional[float] = Field(None, description="BMI指数")
    waist_circumference: Optional[float] = Field(None, description="腰围(cm)")
    hip_circumference: Optional[float] = Field(None, description="臀围(cm)")
    chest_circumference: Optional[float] = Field(None, description="胸围(cm)")
    measurement_date: Optional[datetime] = Field(None, description="测量日期")
    source: Optional[str] = Field("manual", description="数据来源: manual/gym_sync")


class BodyMeasurementCreate(BodyMeasurementBase):
    """
    体测记录创建模型
    """
    pass


class BodyMeasurementUpdate(BaseModel):
    """
    体测记录更新模型
    """
    weight: Optional[float] = Field(None, gt=0, description="体重(kg)")
    body_fat_rate: Optional[float] = Field(None, ge=0, le=100, description="体脂率(%)")
    muscle_mass: Optional[float] = Field(None, gt=0, description="肌肉量(kg)")
    bmi: Optional[float] = Field(None, description="BMI指数")
    waist_circumference: Optional[float] = Field(None, description="腰围(cm)")
    hip_circumference: Optional[float] = Field(None, description="臀围(cm)")
    chest_circumference: Optional[float] = Field(None, description="胸围(cm)")
    measurement_date: Optional[datetime] = Field(None, description="测量日期")
    source: Optional[str] = Field(None, description="数据来源: manual/gym_sync")


class BodyMeasurementResponse(BodyMeasurementBase):
    """
    体测记录响应模型
    """
    id: int = Field(..., description="体测记录ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


# ==================== 训练项目相关模型 ====================

class ExerciseBase(BaseModel):
    """
    训练项目基础模型
    """
    name: str = Field(..., max_length=100, description="训练项目名称")
    category: str = Field(..., max_length=50, description="分类: 力量/有氧/柔韧等")
    description: Optional[str] = Field(None, description="项目描述")
    default_calories_per_hour: Optional[float] = Field(None, description="每小时消耗卡路里参考值")
    icon: Optional[str] = Field(None, description="图标路径")


class ExerciseCreate(ExerciseBase):
    """
    训练项目创建模型
    """
    pass


class ExerciseUpdate(BaseModel):
    """
    训练项目更新模型
    """
    name: Optional[str] = Field(None, max_length=100, description="训练项目名称")
    category: Optional[str] = Field(None, max_length=50, description="分类: 力量/有氧/柔韧等")
    description: Optional[str] = Field(None, description="项目描述")
    default_calories_per_hour: Optional[float] = Field(None, description="每小时消耗卡路里参考值")
    icon: Optional[str] = Field(None, description="图标路径")


class ExerciseResponse(ExerciseBase):
    """
    训练项目响应模型
    """
    id: int = Field(..., description="训练项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


# ==================== 训练日志相关模型 ====================

class TrainingLogItemBase(BaseModel):
    """
    训练日志详情基础模型
    """
    exercise_id: int = Field(..., description="训练项目ID")
    sets: int = Field(default=0, ge=0, description="组数")
    reps: int = Field(default=0, ge=0, description="每组次数")
    weight: float = Field(default=0, ge=0, description="重量(kg)")
    duration: int = Field(default=0, ge=0, description="时长(分钟)")
    calories: float = Field(default=0, ge=0, description="消耗卡路里")
    notes: Optional[str] = Field(None, description="该项训练备注")


class TrainingLogItemCreate(TrainingLogItemBase):
    """
    训练日志详情创建模型
    """
    pass


class TrainingLogItemResponse(TrainingLogItemBase):
    """
    训练日志详情响应模型
    """
    id: int = Field(..., description="训练日志详情ID")
    training_log_id: int = Field(..., description="训练日志ID")
    exercise_name: Optional[str] = Field(None, description="训练项目名称")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class TrainingLogBase(BaseModel):
    """
    训练日志基础模型
    """
    training_date: Optional[datetime] = Field(None, description="训练日期")
    duration: int = Field(..., gt=0, description="训练时长(分钟)")
    total_calories: float = Field(default=0, ge=0, description="总消耗卡路里")
    notes: Optional[str] = Field(None, description="训练备注")
    mood: Optional[str] = Field(None, description="训练心情: 好/一般/差")


class TrainingLogCreate(TrainingLogBase):
    """
    训练日志创建模型
    """
    items: List[TrainingLogItemCreate] = Field(default_factory=list, description="训练详情列表")


class TrainingLogUpdate(BaseModel):
    """
    训练日志更新模型
    """
    training_date: Optional[datetime] = Field(None, description="训练日期")
    duration: Optional[int] = Field(None, gt=0, description="训练时长(分钟)")
    total_calories: Optional[float] = Field(None, ge=0, description="总消耗卡路里")
    notes: Optional[str] = Field(None, description="训练备注")
    mood: Optional[str] = Field(None, description="训练心情: 好/一般/差")


class TrainingLogResponse(TrainingLogBase):
    """
    训练日志响应模型
    """
    id: int = Field(..., description="训练日志ID")
    user_id: int = Field(..., description="用户ID")
    items: List[TrainingLogItemResponse] = Field(default_factory=list, description="训练详情列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


# ==================== 目标设定相关模型 ====================

class TrainingPlanBase(BaseModel):
    """
    训练计划基础模型
    """
    plan_name: str = Field(..., max_length=100, description="计划名称")
    description: Optional[str] = Field(None, description="计划描述")
    frequency: Optional[str] = Field(None, max_length=50, description="训练频率: 每周3次等")
    duration: Optional[int] = Field(None, description="每次训练时长(分钟)")
    exercises: Optional[str] = Field(None, description="推荐训练项目(JSON格式)")


class TrainingPlanCreate(TrainingPlanBase):
    """
    训练计划创建模型
    """
    pass


class TrainingPlanResponse(TrainingPlanBase):
    """
    训练计划响应模型
    """
    id: int = Field(..., description="训练计划ID")
    goal_id: int = Field(..., description="目标ID")
    is_active: int = Field(..., description="是否有效: 1有效 0无效")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class DietAdviceBase(BaseModel):
    """
    饮食建议基础模型
    """
    advice_type: str = Field(..., max_length=50, description="建议类型: breakfast/lunch/dinner/snack")
    title: str = Field(..., max_length=100, description="建议标题")
    content: str = Field(..., description="建议内容")
    calories_range: Optional[str] = Field(None, max_length=50, description="卡路里范围")


class DietAdviceCreate(DietAdviceBase):
    """
    饮食建议创建模型
    """
    pass


class DietAdviceResponse(DietAdviceBase):
    """
    饮食建议响应模型
    """
    id: int = Field(..., description="饮食建议ID")
    goal_id: int = Field(..., description="目标ID")
    is_active: int = Field(..., description="是否有效: 1有效 0无效")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class GoalProgressBase(BaseModel):
    """
    目标进度基础模型
    """
    progress_value: float = Field(..., description="当前进度值")
    progress_percent: Optional[float] = Field(None, description="进度百分比")
    notes: Optional[str] = Field(None, description="进度备注")
    record_date: Optional[datetime] = Field(None, description="记录日期")


class GoalProgressCreate(GoalProgressBase):
    """
    目标进度创建模型
    """
    pass


class GoalProgressResponse(GoalProgressBase):
    """
    目标进度响应模型
    """
    id: int = Field(..., description="目标进度ID")
    goal_id: int = Field(..., description="目标ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    """
    目标基础模型
    """
    goal_type: GoalTypeEnum = Field(..., description="目标类型")
    goal_name: str = Field(..., max_length=100, description="目标名称")
    description: Optional[str] = Field(None, description="目标描述")
    target_value: Optional[float] = Field(None, description="目标值(如目标体重)")
    current_value: Optional[float] = Field(None, description="当前值")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class GoalCreate(GoalBase):
    """
    目标创建模型
    """
    training_plans: List[TrainingPlanCreate] = Field(default_factory=list, description="训练计划列表")
    diet_advices: List[DietAdviceCreate] = Field(default_factory=list, description="饮食建议列表")


class GoalUpdate(BaseModel):
    """
    目标更新模型
    """
    goal_name: Optional[str] = Field(None, max_length=100, description="目标名称")
    description: Optional[str] = Field(None, description="目标描述")
    target_value: Optional[float] = Field(None, description="目标值(如目标体重)")
    current_value: Optional[float] = Field(None, description="当前值")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    status: Optional[GoalStatusEnum] = Field(None, description="状态: active/completed/failed")


class GoalResponse(GoalBase):
    """
    目标响应模型
    """
    id: int = Field(..., description="目标ID")
    user_id: int = Field(..., description="用户ID")
    status: str = Field(..., description="状态: active/completed/failed")
    progress: float = Field(..., description="进度百分比(0-100)")
    training_plans: List[TrainingPlanResponse] = Field(default_factory=list, description="训练计划列表")
    diet_advices: List[DietAdviceResponse] = Field(default_factory=list, description="饮食建议列表")
    progress_records: List[GoalProgressResponse] = Field(default_factory=list, description="进度记录列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


# ==================== 通用响应模型 ====================

class ApiResponse(BaseModel):
    """
    通用API响应模型
    """
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[dict] = Field(None, description="数据")


class TokenResponse(BaseModel):
    """
    登录令牌响应模型
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


# ==================== 体测数据统计模型 ====================

class BodyMeasurementStats(BaseModel):
    """
    体测数据统计模型
    用于折线图展示
    """
    dates: List[str] = Field(default_factory=list, description="日期列表")
    weights: List[float] = Field(default_factory=list, description="体重列表")
    body_fat_rates: List[float] = Field(default_factory=list, description="体脂率列表")
    muscle_masses: List[float] = Field(default_factory=list, description="肌肉量列表")
    bmis: List[float] = Field(default_factory=list, description="BMI列表")
