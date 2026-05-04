from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Time, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SecurityPersonnel(Base):
    __tablename__ = "security_personnel"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), comment="性别")
    phone = Column(String(20), comment="联系电话")
    id_card = Column(String(18), unique=True, comment="身份证号")
    position = Column(String(50), comment="职位")
    status = Column(String(20), default="在职", comment="状态：在职/离职")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    schedules = relationship("SecuritySchedule", back_populates="personnel")


class SecuritySchedule(Base):
    __tablename__ = "security_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("security_personnel.id"), nullable=False, comment="安保人员ID")
    schedule_date = Column(Date, nullable=False, comment="排班日期")
    shift_type = Column(String(20), nullable=False, comment="班次：早班/中班/晚班")
    start_time = Column(Time, comment="开始时间")
    end_time = Column(Time, comment="结束时间")
    post = Column(String(100), comment="岗位")
    status = Column(String(20), default="待执行", comment="状态：待执行/执行中/已完成/取消")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    personnel = relationship("SecurityPersonnel", back_populates="schedules")


class PatrolRoute(Base):
    __tablename__ = "patrol_route"
    
    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(100), nullable=False, comment="路线名称")
    route_code = Column(String(50), unique=True, comment="路线编号")
    description = Column(Text, comment="路线描述")
    checkpoints = Column(Text, comment="巡检点列表(JSON格式)")
    patrol_frequency = Column(String(50), comment="巡逻频次")
    status = Column(String(20), default="启用", comment="状态：启用/停用")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    records = relationship("PatrolRecord", back_populates="route")


class PatrolRecord(Base):
    __tablename__ = "patrol_record"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("patrol_route.id"), nullable=False, comment="路线ID")
    personnel_id = Column(Integer, ForeignKey("security_personnel.id"), nullable=False, comment="安保人员ID")
    patrol_date = Column(Date, nullable=False, comment="巡逻日期")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    checkpoints_completed = Column(Text, comment="已完成巡检点")
    abnormalities = Column(Text, comment="异常情况")
    status = Column(String(20), default="进行中", comment="状态：进行中/已完成/异常")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    route = relationship("PatrolRoute", back_populates="records")


class MonitorDevice(Base):
    __tablename__ = "monitor_device"
    
    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_code = Column(String(50), unique=True, comment="设备编号")
    location = Column(String(200), comment="安装位置")
    ip_address = Column(String(50), comment="IP地址")
    device_type = Column(String(50), comment="设备类型：枪机/球机/门禁等")
    status = Column(String(20), default="正常", comment="状态：正常/离线/故障")
    installation_date = Column(Date, comment="安装日期")
    last_maintenance = Column(Date, comment="上次维护时间")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class VehicleRecord(Base):
    __tablename__ = "vehicle_record"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), nullable=False, comment="车牌号")
    vehicle_type = Column(String(50), comment="车辆类型")
    owner_name = Column(String(50), comment="车主姓名")
    owner_phone = Column(String(20), comment="车主电话")
    entry_time = Column(DateTime, default=datetime.now, comment="进入时间")
    exit_time = Column(DateTime, comment="离开时间")
    entry_gate = Column(String(50), comment="入口门岗")
    exit_gate = Column(String(50), comment="出口门岗")
    purpose = Column(String(100), comment="来访目的")
    remarks = Column(Text, comment="备注")
    status = Column(String(20), default="在场", comment="状态：在场/已离开")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class VisitorRecord(Base):
    __tablename__ = "visitor_record"
    
    id = Column(Integer, primary_key=True, index=True)
    visitor_name = Column(String(50), nullable=False, comment="访客姓名")
    visitor_phone = Column(String(20), comment="访客电话")
    visitor_id_card = Column(String(18), comment="访客身份证号")
    visit_unit = Column(String(100), comment="访问单位")
    visited_person = Column(String(50), comment="被访人")
    visit_purpose = Column(String(100), comment="来访目的")
    entry_time = Column(DateTime, default=datetime.now, comment="进入时间")
    exit_time = Column(DateTime, comment="离开时间")
    visitor_count = Column(Integer, default=1, comment="访客人数")
    credentials = Column(Text, comment="携带证件")
    remarks = Column(Text, comment="备注")
    status = Column(String(20), default="在场", comment="状态：在场/已离开")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class EmergencyReport(Base):
    __tablename__ = "emergency_report"
    
    id = Column(Integer, primary_key=True, index=True)
    report_title = Column(String(200), nullable=False, comment="事件标题")
    event_type = Column(String(50), comment="事件类型：火灾/盗窃/斗殴/其他")
    location = Column(String(200), comment="发生地点")
    reporter_name = Column(String(50), comment="上报人姓名")
    reporter_phone = Column(String(20), comment="上报人电话")
    report_time = Column(DateTime, default=datetime.now, comment="上报时间")
    event_description = Column(Text, comment="事件描述")
    handle_person = Column(String(50), comment="处理人")
    handle_time = Column(DateTime, comment="处理时间")
    handle_result = Column(Text, comment="处理结果")
    status = Column(String(20), default="待处理", comment="状态：待处理/处理中/已处理")
    priority = Column(String(20), default="一般", comment="优先级：紧急/重要/一般")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class CleaningArea(Base):
    __tablename__ = "cleaning_area"
    
    id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String(100), nullable=False, comment="区域名称")
    area_code = Column(String(50), unique=True, comment="区域编号")
    parent_id = Column(Integer, ForeignKey("cleaning_area.id"), comment="父区域ID")
    area_type = Column(String(50), comment="区域类型：楼栋/楼层/公共区域/道路等")
    area_size = Column(Integer, comment="区域面积(平方米)")
    cleaning_frequency = Column(String(50), comment="清洁频次")
    cleaning_standard = Column(Text, comment="清洁标准")
    responsible_person = Column(String(50), comment="责任人")
    responsible_phone = Column(String(20), comment="责任人电话")
    status = Column(String(20), default="启用", comment="状态：启用/停用")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    children = relationship("CleaningArea", backref="parent", remote_side=[id])
    records = relationship("CleaningRecord", back_populates="area")


class CleaningRecord(Base):
    __tablename__ = "cleaning_record"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("cleaning_area.id"), nullable=False, comment="区域ID")
    cleaning_date = Column(Date, nullable=False, comment="清洁日期")
    cleaner_name = Column(String(50), comment="清洁员姓名")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    cleaning_items = Column(Text, comment="清洁项目")
    cleaning_quality = Column(String(50), comment="清洁质量：优秀/良好/合格/不合格")
    remarks = Column(Text, comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    area = relationship("CleaningArea", back_populates="records")


class GreenPlant(Base):
    __tablename__ = "green_plant"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_name = Column(String(100), nullable=False, comment="植物名称")
    plant_code = Column(String(50), unique=True, comment="植物编号")
    plant_type = Column(String(50), comment="植物类型：乔木/灌木/花卉/草坪等")
    scientific_name = Column(String(100), comment="学名")
    location = Column(String(200), comment="种植位置")
    planting_date = Column(Date, comment="种植日期")
    quantity = Column(Integer, default=1, comment="数量")
    growth_status = Column(String(50), default="良好", comment="生长状态：良好/一般/较差/死亡")
    responsible_person = Column(String(50), comment="责任人")
    remarks = Column(Text, comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    maintenance_plans = relationship("MaintenancePlan", back_populates="plant")


class MaintenancePlan(Base):
    __tablename__ = "maintenance_plan"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("green_plant.id"), nullable=False, comment="植物ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    maintenance_type = Column(String(50), comment="养护类型：浇水/施肥/修剪/病虫害防治等")
    frequency = Column(String(50), comment="养护频次")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    description = Column(Text, comment="养护描述")
    responsible_person = Column(String(50), comment="责任人")
    status = Column(String(20), default="待执行", comment="状态：待执行/执行中/已完成/取消")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    plant = relationship("GreenPlant", back_populates="maintenance_plans")
    records = relationship("MaintenanceRecord", back_populates="plan")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_record"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("maintenance_plan.id"), comment="养护计划ID")
    plant_id = Column(Integer, ForeignKey("green_plant.id"), nullable=False, comment="植物ID")
    maintenance_date = Column(Date, nullable=False, comment="养护日期")
    maintenance_type = Column(String(50), comment="养护类型")
    operator = Column(String(50), comment="操作人")
    work_content = Column(Text, comment="工作内容")
    materials_used = Column(Text, comment="使用材料")
    quality = Column(String(50), comment="养护质量")
    remarks = Column(Text, comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    plan = relationship("MaintenancePlan", back_populates="records")
