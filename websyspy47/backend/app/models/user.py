from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    用户表模型
    存储系统用户信息，包括普通用户和管理员
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    phone = Column(String(20), unique=True, nullable=True, index=True, comment="手机号")
    email = Column(String(100), unique=True, nullable=True, index=True, comment="邮箱")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    address = Column(String(500), nullable=True, comment="地址")
    
    # 用户类型：0-普通用户，1-管理员，2-客服
    user_type = Column(Integer, default=0, comment="用户类型")
    # 用户状态：0-禁用，1-正常
    status = Column(Integer, default=1, comment="状态")
    
    # 积分相关
    points = Column(Integer, default=0, comment="积分数")
    total_points = Column(Integer, default=0, comment="累计积分")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

class Feedback(Base):
    """
    用户反馈/投诉表模型
    存储用户的投诉和反馈信息
    """
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="反馈ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    
    # 反馈类型：0-投诉，1-建议，2-咨询
    feedback_type = Column(Integer, default=1, comment="反馈类型")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    contact = Column(String(100), nullable=True, comment="联系方式")
    
    # 状态：0-待处理，1-处理中，2-已处理，3-已关闭
    status = Column(Integer, default=0, comment="状态")
    reply = Column(Text, nullable=True, comment="回复内容")
    reply_user_id = Column(Integer, nullable=True, comment="回复人ID")
    reply_time = Column(DateTime, nullable=True, comment="回复时间")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
