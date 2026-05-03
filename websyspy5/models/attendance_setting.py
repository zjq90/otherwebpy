"""
考勤设置数据模型
存储上下班时间等考勤配置
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class AttendanceSetting(Base):
    """
    考勤设置表模型
    存储上下班时间点、考勤规则等配置
    """
    __tablename__ = "attendance_setting"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 上午上班时间（格式：HH:MM）
    morning_start_time = Column(String(10), default="09:00")
    
    # 上午下班时间（格式：HH:MM）
    morning_end_time = Column(String(10), default="12:00")
    
    # 下午上班时间（格式：HH:MM）
    afternoon_start_time = Column(String(10), default="14:00")
    
    # 下午下班时间（格式：HH:MM）
    afternoon_end_time = Column(String(10), default="18:00")
    
    # 考勤宽容时间（分钟）
    # 在此时间内迟到/早退不算异常
    grace_minutes = Column(Integer, default=30)
    
    # 是否启用下午考勤
    enable_afternoon = Column(Integer, default=1)
    
    # 工作日设置（1-7代表周一到周日，多个用逗号分隔）
    work_days = Column(String(50), default="1,2,3,4,5")
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    
    # 更新时间
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """
        将模型对象转换为字典
        用于API响应
        """
        return {
            "id": self.id,
            "morning_start_time": self.morning_start_time,
            "morning_end_time": self.morning_end_time,
            "afternoon_start_time": self.afternoon_start_time,
            "afternoon_end_time": self.afternoon_end_time,
            "grace_minutes": self.grace_minutes,
            "enable_afternoon": self.enable_afternoon,
            "work_days": self.work_days,
            "remark": self.remark,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }
