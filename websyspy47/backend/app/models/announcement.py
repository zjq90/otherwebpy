from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Announcement(Base):
    """
    公告表模型
    存储系统公告、环保活动信息等
    """
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="公告ID")
    title = Column(String(200), nullable=False, comment="公告标题")
    summary = Column(String(500), nullable=True, comment="公告摘要")
    content = Column(Text, nullable=False, comment="公告内容")
    
    # 公告类型：0-系统公告，1-环保活动，2-政策通知，3-其他
    announcement_type = Column(Integer, default=0, index=True, comment="公告类型")
    
    # 封面和图片
    cover_image = Column(String(500), nullable=True, comment="封面图片")
    images = Column(Text, nullable=True, comment="图片列表(JSON格式)")
    
    # 发布状态
    # 0-草稿，1-已发布，2-已撤回
    status = Column(Integer, default=0, index=True, comment="发布状态")
    
    # 排序和置顶
    sort = Column(Integer, default=0, comment="排序")
    is_top = Column(Integer, default=0, comment="是否置顶")
    
    # 发布时间
    publish_time = Column(DateTime, nullable=True, comment="发布时间")
    expire_time = Column(DateTime, nullable=True, comment="过期时间")
    
    # 浏览次数
    view_count = Column(Integer, default=0, comment="浏览次数")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
