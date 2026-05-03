"""
工作人员数据模型
存储工作人员的基本信息和人脸照片
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Staff(Base):
    """
    工作人员表模型
    存储工作人员的基本信息，包括人脸照片
    """
    __tablename__ = "staff"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 工号，唯一标识
    staff_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 姓名
    name = Column(String(100), nullable=False)
    
    # 性别：男/女
    gender = Column(String(10), nullable=True)
    
    # 部门
    department = Column(String(100), nullable=True)
    
    # 职位
    position = Column(String(100), nullable=True)
    
    # 手机号码
    phone = Column(String(20), nullable=True)
    
    # 邮箱
    email = Column(String(100), nullable=True)
    
    # 身份证号
    id_card = Column(String(18), nullable=True)
    
    # 人脸照片存储路径
    face_photo_path = Column(String(500), nullable=True)
    
    # 状态：1-在职，0-离职
    status = Column(Integer, default=1)
    
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
            "staff_no": self.staff_no,
            "name": self.name,
            "gender": self.gender,
            "department": self.department,
            "position": self.position,
            "phone": self.phone,
            "email": self.email,
            "id_card": self.id_card,
            "face_photo_path": self.face_photo_path,
            "status": self.status,
            "remark": self.remark,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }
