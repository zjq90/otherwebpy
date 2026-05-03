"""
出入记录数据模型
存储人员通过门禁设备的出入记录
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class AccessRecord(Base):
    """
    出入记录表模型
    存储工作人员通过门禁设备的扫脸记录
    """
    __tablename__ = "access_record"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的工作人员ID
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    
    # 关联的设备ID
    device_id = Column(Integer, ForeignKey("device.id"), nullable=False, index=True)
    
    # 出入类型：1-进入，0-离开
    access_type = Column(Integer, default=1)
    
    # 出入时间
    access_time = Column(DateTime, nullable=False, index=True)
    
    # 人脸识别相似度（0-1之间）
    similarity = Column(Float, default=0.0)
    
    # 抓拍照片存储路径
    capture_photo_path = Column(String(500), nullable=True)
    
    # 识别结果：1-成功，0-失败
    verify_result = Column(Integer, default=1)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())

    # 定义关系，方便联表查询
    staff = relationship("Staff", backref="access_records")
    device = relationship("Device", backref="access_records")

    # 出入类型描述映射
    ACCESS_TYPE_MAP = {
        0: "离开",
        1: "进入"
    }

    # 验证结果描述映射
    VERIFY_RESULT_MAP = {
        0: "失败",
        1: "成功"
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
            "device_id": self.device_id,
            "device_name": self.device.device_name if self.device else None,
            "device_no": self.device.device_no if self.device else None,
            "location": self.device.location if self.device else None,
            "access_type": self.access_type,
            "access_type_text": self.ACCESS_TYPE_MAP.get(self.access_type, "未知"),
            "access_time": self.access_time.strftime("%Y-%m-%d %H:%M:%S") if self.access_time else None,
            "similarity": self.similarity,
            "capture_photo_path": self.capture_photo_path,
            "verify_result": self.verify_result,
            "verify_result_text": self.VERIFY_RESULT_MAP.get(self.verify_result, "未知"),
            "remark": self.remark,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }
