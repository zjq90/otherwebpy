from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Equipment(Base):
    """
    设备档案表
    存储设备的基本信息，包括搅拌主机、皮带秤、空压机等关键设备
    """
    
    __tablename__ = "equipment"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 设备编号（唯一标识）
    equipment_code = Column(String(50), unique=True, index=True, nullable=False, comment="设备编号")
    
    # 设备名称
    name = Column(String(100), nullable=False, comment="设备名称")
    
    # 设备类型：搅拌主机、皮带秤、空压机等
    equipment_type = Column(String(50), nullable=False, comment="设备类型")
    
    # 设备型号
    model = Column(String(100), comment="设备型号")
    
    # 设备规格
    specification = Column(String(200), comment="设备规格")
    
    # 生产厂家
    manufacturer = Column(String(100), comment="生产厂家")
    
    # 出厂日期
    production_date = Column(DateTime, comment="出厂日期")
    
    # 投入使用日期
    installation_date = Column(DateTime, comment="投入使用日期")
    
    # 安装位置
    location = Column(String(200), comment="安装位置")
    
    # 设备状态：运行中、停机、维护中、故障
    status = Column(String(20), default="运行中", comment="设备状态")
    
    # 负责人
    responsible_person = Column(String(50), comment="负责人")
    
    # 联系电话
    contact_phone = Column(String(20), comment="联系电话")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：关联传感器
    sensors = relationship("Sensor", back_populates="equipment", cascade="all, delete-orphan")
    
    # 关系：关联运行日志
    operation_logs = relationship("OperationLog", back_populates="equipment", cascade="all, delete-orphan")
    
    # 关系：关联保养任务
    maintenance_tasks = relationship("MaintenanceTask", back_populates="equipment", cascade="all, delete-orphan")


class Sensor(Base):
    """
    传感器表
    存储传感器信息，用于采集设备的电流、温度、振动等数据
    """
    
    __tablename__ = "sensor"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 传感器编号（唯一标识）
    sensor_code = Column(String(50), unique=True, index=True, nullable=False, comment="传感器编号")
    
    # 传感器名称
    name = Column(String(100), nullable=False, comment="传感器名称")
    
    # 传感器类型：电流、温度、振动等
    sensor_type = Column(String(50), nullable=False, comment="传感器类型")
    
    # 关联的设备ID
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="关联设备ID")
    
    # 安装位置
    installation_location = Column(String(200), comment="安装位置")
    
    # 数据单位（如：A、℃、mm/s）
    unit = Column(String(20), comment="数据单位")
    
    # 正常范围最小值
    min_value = Column(Float, comment="正常范围最小值")
    
    # 正常范围最大值
    max_value = Column(Float, comment="正常范围最大值")
    
    # 预警阈值
    warning_threshold = Column(Float, comment="预警阈值")
    
    # 报警阈值
    alarm_threshold = Column(Float, comment="报警阈值")
    
    # 传感器状态：正常、故障、离线
    status = Column(String(20), default="正常", comment="传感器状态")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：关联设备
    equipment = relationship("Equipment", back_populates="sensors")
    
    # 关系：关联传感器数据
    sensor_data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")
