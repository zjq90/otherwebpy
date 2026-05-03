"""
考勤记录数据模型
存储根据出入记录生成的考勤信息
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class AttendanceRecord(Base):
    """
    考勤记录表模型
    根据出入记录和考勤设置生成的考勤信息
    """
    __tablename__ = "attendance_record"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的工作人员ID
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    
    # 考勤日期
    attendance_date = Column(Date, nullable=False, index=True)
    
    # 上午签到时间
    morning_check_in = Column(DateTime, nullable=True)
    
    # 上午签退时间
    morning_check_out = Column(DateTime, nullable=True)
    
    # 下午签到时间
    afternoon_check_in = Column(DateTime, nullable=True)
    
    # 下午签退时间
    afternoon_check_out = Column(DateTime, nullable=True)
    
    # 上午考勤状态
    # 0: 缺勤, 1: 正常, 2: 迟到, 3: 早退
    morning_status = Column(Integer, default=0)
    
    # 下午考勤状态
    afternoon_status = Column(Integer, default=0)
    
    # 当日总状态
    # 0: 缺勤, 1: 正常, 2: 迟到, 3: 早退, 4: 迟到+早退
    day_status = Column(Integer, default=0)
    
    # 工作时长（分钟）
    work_duration = Column(Integer, default=0)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    
    # 更新时间
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 定义关系
    staff = relationship("Staff", backref="attendance_records")

    # 状态描述映射
    STATUS_MAP = {
        0: "缺勤",
        1: "正常",
        2: "迟到",
        3: "早退",
        4: "迟到+早退"
    }

    def to_dict(self):
        """
        将模型对象转换为字典
        用于API响应
        """
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.staff.name if self.staff else None,
            "staff_no": self.staff.staff_no if self.staff else None,
            "department": self.staff.department if self.staff else None,
            "attendance_date": self.attendance_date.strftime("%Y-%m-%d") if self.attendance_date else None,
            "morning_check_in": self.morning_check_in.strftime("%H:%M:%S") if self.morning_check_in else None,
            "morning_check_out": self.morning_check_out.strftime("%H:%M:%S") if self.morning_check_out else None,
            "afternoon_check_in": self.afternoon_check_in.strftime("%H:%M:%S") if self.afternoon_check_in else None,
            "afternoon_check_out": self.afternoon_check_out.strftime("%H:%M:%S") if self.afternoon_check_out else None,
            "morning_status": self.morning_status,
            "morning_status_text": self.STATUS_MAP.get(self.morning_status, "未知"),
            "afternoon_status": self.afternoon_status,
            "afternoon_status_text": self.STATUS_MAP.get(self.afternoon_status, "未知"),
            "day_status": self.day_status,
            "day_status_text": self.STATUS_MAP.get(self.day_status, "未知"),
            "work_duration": self.work_duration,
            "work_duration_text": self._format_duration(self.work_duration),
            "remark": self.remark,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }

    def _format_duration(self, minutes):
        """
        格式化工作时长
        将分钟转换为小时分钟格式
        """
        if minutes <= 0:
            return "0小时"
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours}小时{mins}分钟"
        elif hours > 0:
            return f"{hours}小时"
        else:
            return f"{mins}分钟"
