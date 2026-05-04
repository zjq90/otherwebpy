"""
数据库模型定义模块
定义所有数据表结构
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import Base


class User(Base):
    """
    用户表
    存储用户基本信息
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像路径")
    gender = Column(String(10), nullable=True, comment="性别: male/female")
    birthday = Column(DateTime, nullable=True, comment="生日")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    body_measurements = relationship("BodyMeasurement", back_populates="user", cascade="all, delete-orphan")
    training_logs = relationship("TrainingLog", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class BodyMeasurement(Base):
    """
    体测记录表
    存储体脂率、肌肉量、体重等数据
    """
    __tablename__ = "body_measurements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    weight = Column(Float, nullable=False, comment="体重(kg)")
    body_fat_rate = Column(Float, nullable=False, comment="体脂率(%)")
    muscle_mass = Column(Float, nullable=False, comment="肌肉量(kg)")
    bmi = Column(Float, nullable=True, comment="BMI指数")
    waist_circumference = Column(Float, nullable=True, comment="腰围(cm)")
    hip_circumference = Column(Float, nullable=True, comment="臀围(cm)")
    chest_circumference = Column(Float, nullable=True, comment="胸围(cm)")
    measurement_date = Column(DateTime, default=datetime.now, comment="测量日期")
    source = Column(String(50), default="manual", comment="数据来源: manual/gym_sync")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    user = relationship("User", back_populates="body_measurements")


class Exercise(Base):
    """
    训练项目表
    存储训练项目基本信息
    """
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="训练项目名称")
    category = Column(String(50), nullable=False, comment="分类: 力量/有氧/柔韧等")
    description = Column(Text, nullable=True, comment="项目描述")
    default_calories_per_hour = Column(Float, nullable=True, comment="每小时消耗卡路里参考值")
    icon = Column(String(255), nullable=True, comment="图标路径")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    training_log_items = relationship("TrainingLogItem", back_populates="exercise")


class TrainingLog(Base):
    """
    训练日志表
    存储训练日志基本信息
    """
    __tablename__ = "training_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    training_date = Column(DateTime, default=datetime.now, comment="训练日期")
    duration = Column(Integer, nullable=False, comment="训练时长(分钟)")
    total_calories = Column(Float, default=0, comment="总消耗卡路里")
    notes = Column(Text, nullable=True, comment="训练备注")
    mood = Column(String(20), nullable=True, comment="训练心情: 好/一般/差")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    user = relationship("User", back_populates="training_logs")
    items = relationship("TrainingLogItem", back_populates="training_log", cascade="all, delete-orphan")


class TrainingLogItem(Base):
    """
    训练日志详情表
    存储每次训练的具体内容
    """
    __tablename__ = "training_log_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    training_log_id = Column(Integer, ForeignKey("training_logs.id"), nullable=False, comment="训练日志ID")
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, comment="训练项目ID")
    sets = Column(Integer, default=0, comment="组数")
    reps = Column(Integer, default=0, comment="每组次数")
    weight = Column(Float, default=0, comment="重量(kg)")
    duration = Column(Integer, default=0, comment="时长(分钟)")
    calories = Column(Float, default=0, comment="消耗卡路里")
    notes = Column(Text, nullable=True, comment="该项训练备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    training_log = relationship("TrainingLog", back_populates="items")
    exercise = relationship("Exercise", back_populates="training_log_items")


class Goal(Base):
    """
    目标设定表
    存储用户健身目标
    """
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_type = Column(String(50), nullable=False, comment="目标类型: lose_weight/gain_muscle/shape/endurance")
    goal_name = Column(String(100), nullable=False, comment="目标名称")
    description = Column(Text, nullable=True, comment="目标描述")
    target_value = Column(Float, nullable=True, comment="目标值(如目标体重)")
    current_value = Column(Float, nullable=True, comment="当前值")
    start_date = Column(DateTime, default=datetime.now, comment="开始日期")
    end_date = Column(DateTime, nullable=True, comment="结束日期")
    status = Column(String(20), default="active", comment="状态: active/completed/failed")
    progress = Column(Float, default=0, comment="进度百分比(0-100)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    user = relationship("User", back_populates="goals")
    training_plans = relationship("TrainingPlan", back_populates="goal", cascade="all, delete-orphan")
    diet_advices = relationship("DietAdvice", back_populates="goal", cascade="all, delete-orphan")
    progress_records = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")


class TrainingPlan(Base):
    """
    训练计划表
    存储系统推荐的训练计划
    """
    __tablename__ = "training_plans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, comment="目标ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    description = Column(Text, nullable=True, comment="计划描述")
    frequency = Column(String(50), nullable=True, comment="训练频率: 每周3次等")
    duration = Column(Integer, nullable=True, comment="每次训练时长(分钟)")
    exercises = Column(Text, nullable=True, comment="推荐训练项目(JSON格式)")
    is_active = Column(Integer, default=1, comment="是否有效: 1有效 0无效")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    goal = relationship("Goal", back_populates="training_plans")


class DietAdvice(Base):
    """
    饮食建议表
    存储系统推荐的饮食建议
    """
    __tablename__ = "diet_advices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, comment="目标ID")
    advice_type = Column(String(50), nullable=False, comment="建议类型: breakfast/lunch/dinner/snack")
    title = Column(String(100), nullable=False, comment="建议标题")
    content = Column(Text, nullable=False, comment="建议内容")
    calories_range = Column(String(50), nullable=True, comment="卡路里范围")
    is_active = Column(Integer, default=1, comment="是否有效: 1有效 0无效")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    goal = relationship("Goal", back_populates="diet_advices")


class GoalProgress(Base):
    """
    目标进度记录表
    存储目标的定期进度反馈
    """
    __tablename__ = "goal_progress"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, comment="目标ID")
    progress_value = Column(Float, nullable=False, comment="当前进度值")
    progress_percent = Column(Float, nullable=True, comment="进度百分比")
    notes = Column(Text, nullable=True, comment="进度备注")
    record_date = Column(DateTime, default=datetime.now, comment="记录日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    goal = relationship("Goal", back_populates="progress_records")
