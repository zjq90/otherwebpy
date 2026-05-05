from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class CustomerServiceStaff(Base):
    """
    客服人员表模型
    存储客服人员的账号和基本信息
    """
    __tablename__ = "cs_staffs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="客服人员ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="手机号")
    avatar = Column(String(255), nullable=True, comment="头像")
    
    # 分组：0-普通客服，1-投诉处理，2-技术支持
    group_type = Column(Integer, default=0, comment="分组类型")
    
    # 状态：0-禁用，1-正常，2-离线
    status = Column(Integer, default=1, index=True, comment="状态")
    
    # 工作统计
    total_consultations = Column(Integer, default=0, comment="总咨询数")
    resolved_count = Column(Integer, default=0, comment="已解决数")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class Consultation(Base):
    """
    用户咨询记录表模型
    存储用户与客服的咨询对话记录
    """
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="咨询ID")
    consultation_no = Column(String(50), unique=True, nullable=False, comment="咨询编号")
    
    # 用户信息
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=True, comment="用户姓名")
    user_phone = Column(String(20), nullable=True, comment="用户电话")
    
    # 客服信息
    cs_staff_id = Column(Integer, nullable=True, index=True, comment="客服人员ID")
    cs_staff_name = Column(String(50), nullable=True, comment="客服人员姓名")
    
    # 咨询信息
    # 咨询类型：0-订单问题，1-积分问题，2-回收问题，3-其他
    consultation_type = Column(Integer, default=0, index=True, comment="咨询类型")
    title = Column(String(200), nullable=True, comment="标题")
    question = Column(Text, nullable=False, comment="问题描述")
    
    # 状态：0-待分配，1-处理中，2-已解决，3-已关闭
    status = Column(Integer, default=0, index=True, comment="状态")
    
    # 评分
    rating = Column(Integer, nullable=True, comment="满意度评分(1-5)")
    rating_comment = Column(Text, nullable=True, comment="评价内容")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    assign_time = Column(DateTime, nullable=True, comment="分配时间")
    resolve_time = Column(DateTime, nullable=True, comment="解决时间")
    close_time = Column(DateTime, nullable=True, comment="关闭时间")

class ConsultationMessage(Base):
    """
    咨询消息记录表模型
    存储咨询中的消息对话
    """
    __tablename__ = "consultation_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="消息ID")
    consultation_id = Column(Integer, nullable=False, index=True, comment="咨询ID")
    
    # 发送者类型：0-用户，1-客服
    sender_type = Column(Integer, nullable=False, comment="发送者类型")
    sender_id = Column(Integer, nullable=True, comment="发送者ID")
    sender_name = Column(String(50), nullable=True, comment="发送者名称")
    
    # 消息内容
    # 消息类型：0-文本，1-图片，2-文件
    message_type = Column(Integer, default=0, comment="消息类型")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # 是否已读
    is_read = Column(Integer, default=0, comment="是否已读")
    read_time = Column(DateTime, nullable=True, comment="阅读时间")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
