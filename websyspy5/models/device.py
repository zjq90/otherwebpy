"""
门禁设备数据模型
存储门禁设备的基本信息和工作状态
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Device(Base):
    """
    门禁设备表模型
    存储门禁设备的信息，包括位置、工作状态等
    """
    __tablename__ = "device"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 设备编号，唯一标识
    device_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 设备名称
    device_name = Column(String(100), nullable=False)
    
    # 设备型号
    device_model = Column(String(100), nullable=True)
    
    # 设备位置描述
    location = Column(String(200), nullable=True)
    
    # IP地址
    ip_address = Column(String(50), nullable=True)
    
    # MAC地址
    mac_address = Column(String(50), nullable=True)
    
    # 工作状态：1-在线，0-离线，2-故障
    status = Column(Integer, default=1)
    
    # 最后一次在线时间
    last_online_time = Column(DateTime, nullable=True)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    
    # 更新时间
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 状态描述映射
    STATUS_MAP = {
        0: "离线",
        1: "在线",
        2: "故障"
    }

    def to_dict(self):
        """
        将模型对象转换为字典
        用于API响应
        """
        return {
            "id": self.id,
            "device_no": self.device_no,
            "device_name": self.device_name,
            "device_model": self.device_model,
            "location": self.location,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "status": self.status,
            "status_text": self.STATUS_MAP.get(self.status, "未知"),
            "last_online_time": self.last_online_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_online_time else None,
            "remark": self.remark,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }
