"""
数据库模型定义文件
包含所有数据表的ORM模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class UserRole(str, enum.Enum):
    """用户角色枚举"""
    MEMBER = "member"        # 会员
    COACH = "coach"          # 教练
    STAFF = "staff"          # 工作人员
    ADMIN = "admin"          # 管理员

class Gender(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MessageType(str, enum.Enum):
    """消息类型枚举"""
    COURSE_REMINDER = "course_reminder"    # 课程提醒
    RENEWAL_NOTICE = "renewal_notice"      # 续费通知
    ACTIVITY_PUSH = "activity_push"         # 活动推送
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统公告

class ChatType(str, enum.Enum):
    """聊天类型枚举"""
    CUSTOMER_SERVICE = "customer_service"    # 客服咨询
    COACH_CONSULT = "coach_consult"          # 教练咨询

class User(Base):
    """
    用户表模型
    存储会员、教练、工作人员等所有用户的基本信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    gender = Column(Enum(Gender), default=Gender.OTHER, comment="性别")
    birth_date = Column(DateTime, nullable=True, comment="出生日期")
    role = Column(Enum(UserRole), default=UserRole.MEMBER, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    coach_profile = relationship("Coach", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("MemberPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    chat_sessions_as_user = relationship("ChatSession", back_populates="user", foreign_keys="ChatSession.user_id")
    chat_sessions_as_staff = relationship("ChatSession", back_populates="staff", foreign_keys="ChatSession.staff_id")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

class Coach(Base):
    """
    教练表模型
    存储教练的专业信息、简介等
    """
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True, comment="教练ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    specialization = Column(String(200), nullable=True, comment="专长领域（如：力量训练、瑜伽、康复等）")
    experience_years = Column(Integer, default=0, comment="从业年限")
    certifications = Column(Text, nullable=True, comment="资质证书")
    bio = Column(Text, nullable=True, comment="个人简介")
    rating = Column(Float, default=5.0, comment="平均评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    hourly_rate = Column(Float, default=200.0, comment="课时费")
    is_available = Column(Boolean, default=True, comment="是否可预约")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="coach_profile")
    reviews = relationship("Review", back_populates="coach", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="coach", cascade="all, delete-orphan")

class CourseCategory(str, enum.Enum):
    """课程分类枚举"""
    STRENGTH = "strength"          # 力量训练
    CARDIO = "cardio"              # 有氧训练
    YOGA = "yoga"                  # 瑜伽
    PILATES = "pilates"            # 普拉提
    DANCE = "dance"                # 舞蹈
    BOXING = "boxing"              # 拳击
    SWIMMING = "swimming"          # 游泳
    REHABILITATION = "rehabilitation"  # 康复训练

class CourseType(str, enum.Enum):
    """课程类型枚举"""
    GROUP = "group"                # 团课
    PRIVATE = "private"            # 私教课
    SEMI_PRIVATE = "semi_private"  # 小团体课

class Course(Base):
    """
    课程表模型
    存储课程的基本信息
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, comment="课程ID")
    name = Column(String(100), nullable=False, comment="课程名称")
    description = Column(Text, nullable=True, comment="课程描述")
    category = Column(Enum(CourseCategory), nullable=False, comment="课程分类")
    course_type = Column(Enum(CourseType), default=CourseType.GROUP, comment="课程类型")
    duration = Column(Integer, default=60, comment="课程时长（分钟）")
    difficulty_level = Column(Integer, default=1, comment="难度等级（1-5）")
    calories_burned = Column(Integer, nullable=True, comment="预计消耗卡路里")
    image_url = Column(String(255), nullable=True, comment="课程图片URL")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    bookings = relationship("Booking", back_populates="course", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="course", cascade="all, delete-orphan")

class MemberPreference(Base):
    """
    会员偏好表模型
    存储会员的课程偏好、训练频率与目标，用于智能推荐
    """
    __tablename__ = "member_preferences"

    id = Column(Integer, primary_key=True, index=True, comment="偏好ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 课程偏好（用逗号分隔的分类枚举值列表）
    preferred_categories = Column(String(255), nullable=True, comment="偏好的课程分类")
    preferred_course_types = Column(String(100), nullable=True, comment="偏好的课程类型")
    preferred_difficulty = Column(Integer, default=2, comment="偏好的难度等级")
    
    # 训练频率
    training_frequency_per_week = Column(Integer, default=3, comment="每周训练次数")
    preferred_training_days = Column(String(100), nullable=True, comment="偏好的训练日（如：周一,周三,周五）")
    preferred_training_time = Column(String(50), nullable=True, comment="偏好的训练时间段（如：早上,下午,晚上）")
    
    # 训练目标
    fitness_goals = Column(String(255), nullable=True, comment="健身目标（如：增肌,减脂,塑形）")
    target_weight = Column(Float, nullable=True, comment="目标体重")
    
    # 身体状况
    current_weight = Column(Float, nullable=True, comment="当前体重")
    height = Column(Float, nullable=True, comment="身高")
    has_injuries = Column(Boolean, default=False, comment="是否有伤病史")
    injury_details = Column(Text, nullable=True, comment="伤病详情")
    
    # 教练偏好
    preferred_coach_gender = Column(Enum(Gender), nullable=True, comment="偏好的教练性别")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="preferences")

class BookingStatus(str, enum.Enum):
    """预约状态枚举"""
    PENDING = "pending"            # 待确认
    CONFIRMED = "confirmed"        # 已确认
    COMPLETED = "completed"        # 已完成
    CANCELLED = "cancelled"        # 已取消
    NO_SHOW = "no_show"            # 未出席

class Booking(Base):
    """
    预约表模型
    存储会员预约课程的记录
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, comment="预约ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="会员ID")
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, comment="课程ID")
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True, comment="教练ID（私教课必填）")
    
    # 预约时间
    booking_date = Column(DateTime, nullable=False, comment="预约日期")
    start_time = Column(String(20), nullable=False, comment="开始时间（如：09:00）")
    end_time = Column(String(20), nullable=False, comment="结束时间（如：10:00）")
    
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, comment="预约状态")
    notes = Column(Text, nullable=True, comment="备注")
    reminder_sent = Column(Boolean, default=False, comment="是否已发送提醒")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="bookings")
    course = relationship("Course", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class Message(Base):
    """
    消息表模型
    存储消息中心的所有消息
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, comment="消息ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收用户ID")
    message_type = Column(Enum(MessageType), nullable=False, comment="消息类型")
    
    title = Column(String(200), nullable=False, comment="消息标题")
    content = Column(Text, nullable=False, comment="消息内容")
    image_url = Column(String(255), nullable=True, comment="消息图片URL")
    link_url = Column(String(255), nullable=True, comment="跳转链接")
    
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_at = Column(DateTime, nullable=True, comment="读取时间")
    
    # 关联数据（可选，用于详情跳转）
    related_id = Column(Integer, nullable=True, comment="关联数据ID")
    related_type = Column(String(50), nullable=True, comment="关联数据类型")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系定义
    user = relationship("User", back_populates="messages")

class ChatSession(Base):
    """
    聊天会话表模型
    存储在线客服/教练咨询的会话记录
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, comment="会话ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID（咨询者）")
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="工作人员ID（客服/教练）")
    chat_type = Column(Enum(ChatType), default=ChatType.CUSTOMER_SERVICE, comment="聊天类型")
    
    # 会话主题
    subject = Column(String(200), nullable=True, comment="会话主题")
    
    # 会话状态
    is_active = Column(Boolean, default=True, comment="是否活跃")
    closed_at = Column(DateTime, nullable=True, comment="关闭时间")
    
    # 最后消息时间，用于排序
    last_message_at = Column(DateTime, default=datetime.utcnow, comment="最后消息时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系定义
    user = relationship("User", back_populates="chat_sessions_as_user", foreign_keys=[user_id])
    staff = relationship("User", back_populates="chat_sessions_as_staff", foreign_keys=[staff_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    聊天消息表模型
    存储具体的聊天消息内容
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, comment="消息ID")
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, comment="会话ID")
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    
    # 消息内容
    message_type = Column(String(20), default="text", comment="消息类型：text, image, file")
    content = Column(Text, nullable=False, comment="消息内容")
    file_url = Column(String(255), nullable=True, comment="文件/图片URL")
    
    # 消息状态
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_at = Column(DateTime, nullable=True, comment="读取时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="发送时间")

    # 关系定义
    session = relationship("ChatSession", back_populates="messages")

class Review(Base):
    """
    评价表模型
    存储会员对教练/课程的评价
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, comment="评价ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评价者ID")
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, comment="被评价教练ID")
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, comment="关联预约ID")
    
    # 评分（1-5星）
    rating = Column(Integer, nullable=False, comment="总体评分（1-5）")
    professionalism_rating = Column(Integer, default=5, comment="专业度评分")
    punctuality_rating = Column(Integer, default=5, comment="准时度评分")
    attitude_rating = Column(Integer, default=5, comment="态度评分")
    
    # 评价内容
    content = Column(Text, nullable=True, comment="文字评价")
    image_urls = Column(Text, nullable=True, comment="评价图片URL（逗号分隔）")
    
    # 评价状态
    is_anonymous = Column(Boolean, default=False, comment="是否匿名评价")
    is_visible = Column(Boolean, default=True, comment="是否可见")
    
    # 教练回复
    coach_reply = Column(Text, nullable=True, comment="教练回复")
    coach_reply_at = Column(DateTime, nullable=True, comment="教练回复时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="reviews")
    coach = relationship("Coach", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")

class NutritionProductCategory(str, enum.Enum):
    """营养产品分类枚举"""
    PROTEIN = "protein"            # 蛋白粉
    VITAMIN = "vitamin"            # 维生素
    SUPPLEMENT = "supplement"      # 运动补剂
    MEAL_REPLACEMENT = "meal_replacement"  # 代餐
    ENERGY = "energy"              # 能量补充

class NutritionProduct(Base):
    """
    营养产品表模型
    存储可推荐的营养产品信息
    """
    __tablename__ = "nutrition_products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    name = Column(String(150), nullable=False, comment="产品名称")
    brand = Column(String(100), nullable=True, comment="品牌")
    category = Column(Enum(NutritionProductCategory), nullable=False, comment="产品分类")
    
    # 产品信息
    description = Column(Text, nullable=True, comment="产品描述")
    price = Column(Float, nullable=False, comment="价格")
    original_price = Column(Float, nullable=True, comment="原价")
    stock = Column(Integer, default=0, comment="库存")
    unit = Column(String(20), default="件", comment="单位")
    
    # 适用人群/功效
    suitable_for = Column(String(255), nullable=True, comment="适用人群")
    benefits = Column(Text, nullable=True, comment="功效说明")
    usage_method = Column(Text, nullable=True, comment="使用方法")
    
    # 图片
    image_url = Column(String(255), nullable=True, comment="主图URL")
    image_urls = Column(Text, nullable=True, comment="详情图片URL（逗号分隔）")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否上架")
    is_recommended = Column(Boolean, default=False, comment="是否推荐")
    
    # 评分
    rating = Column(Float, default=5.0, comment="平均评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    sales_count = Column(Integer, default=0, comment="销量")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    recommendations = relationship("Recommendation", back_populates="product", cascade="all, delete-orphan")

class RecommendationType(str, enum.Enum):
    """推荐类型枚举"""
    COURSE = "course"              # 课程推荐
    COACH = "coach"                # 教练推荐
    PRODUCT = "product"            # 营养产品推荐

class RecommendationReason(str, enum.Enum):
    """推荐原因枚举"""
    PREFERENCE = "preference"      # 基于偏好
    HISTORY = "history"            # 基于历史
    POPULAR = "popular"            # 热门推荐
    NEW = "new"                    # 新品/新课程
    PERSONAL = "personal"          # 个性化推荐

class Recommendation(Base):
    """
    推荐记录表模型
    存储系统对会员的推荐记录
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, comment="推荐ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="会员ID")
    
    # 推荐类型
    recommendation_type = Column(Enum(RecommendationType), nullable=False, comment="推荐类型")
    
    # 推荐的目标（根据类型，其中一个有值）
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, comment="推荐课程ID")
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True, comment="推荐教练ID")
    product_id = Column(Integer, ForeignKey("nutrition_products.id"), nullable=True, comment="推荐产品ID")
    
    # 推荐信息
    reason = Column(Enum(RecommendationReason), default=RecommendationReason.PERSONAL, comment="推荐原因")
    score = Column(Float, default=0.0, comment="推荐分数（用于排序）")
    explanation = Column(Text, nullable=True, comment="推荐解释（展示给用户）")
    
    # 用户行为
    is_viewed = Column(Boolean, default=False, comment="是否已查看")
    is_clicked = Column(Boolean, default=False, comment="是否已点击")
    is_purchased = Column(Boolean, default=False, comment="是否已购买/预约")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系定义
    user = relationship("User", back_populates="recommendations")
    course = relationship("Course", back_populates="recommendations")
    coach = relationship("Coach", back_populates="recommendations")
    product = relationship("NutritionProduct", back_populates="recommendations")
