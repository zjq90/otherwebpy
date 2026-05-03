"""
数据模型模块
包含所有数据库表对应的ORM模型
"""
from models.staff import Staff
from models.device import Device
from models.access_record import AccessRecord
from models.attendance_setting import AttendanceSetting
from models.attendance_record import AttendanceRecord

__all__ = ["Staff", "Device", "AccessRecord", "AttendanceSetting", "AttendanceRecord"]
