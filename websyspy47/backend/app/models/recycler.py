from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base

class Recycler(Base):
    """
    回收人员表模型
    存储回收人员的基本信息和账号信息
    """
    __tablename__ = "recyclers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="回收人员ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    id_card = Column(String(18), nullable=True, comment="身份证号")
    
    # 负责区域
    area = Column(String(200), nullable=True, comment="负责区域")
    # 状态：0-禁用，1-正常，2-休假
    status = Column(Integer, default=1, comment="状态")
    
    # 业绩统计
    total_orders = Column(Integer, default=0, comment="总订单数")
    completed_orders = Column(Integer, default=0, comment="完成订单数")
    total_weight = Column(Numeric(10, 2), default=0, comment="总回收重量(kg)")
    total_amount = Column(Numeric(10, 2), default=0, comment="总回收金额(元)")
    
    # 绩效考核
    performance_score = Column(Numeric(5, 2), default=100.00, comment="绩效考核分数")
    performance_level = Column(String(20), nullable=True, comment="绩效等级")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class RecyclerPerformance(Base):
    """
    回收人员绩效考核记录表模型
    存储每次绩效考核的详细记录
    """
    __tablename__ = "recycler_performances"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="记录ID")
    recycler_id = Column(Integer, nullable=False, index=True, comment="回收人员ID")
    
    # 考核周期
    period_type = Column(String(20), nullable=False, comment="周期类型：month/quarter/year")
    period_year = Column(Integer, nullable=False, comment="年份")
    period_month = Column(Integer, nullable=True, comment="月份")
    
    # 考核指标
    order_count = Column(Integer, default=0, comment="订单数量")
    complete_rate = Column(Numeric(5, 2), default=0, comment="完成率")
    avg_response_time = Column(Integer, default=0, comment="平均响应时间(分钟)")
    user_satisfaction = Column(Numeric(3, 2), default=5.00, comment="用户满意度")
    
    # 考核结果
    score = Column(Numeric(5, 2), default=0, comment="总分")
    level = Column(String(20), nullable=True, comment="等级")
    comments = Column(Text, nullable=True, comment="评价")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
