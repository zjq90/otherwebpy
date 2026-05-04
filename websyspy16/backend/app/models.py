"""
数据库模型定义
包含物业项目、房产信息、业主信息等核心模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base
import enum


class PropertyStatus(str, enum.Enum):
    """
    房产状态枚举
    """
    VACANT = "vacant"  # 空置
    RENTED = "rented"  # 出租
    OCCUPIED = "occupied"  # 自住


class PropertyProject(Base):
    """
    物业项目档案模型
    管理小区名称、地理位置、楼栋结构、开发商等基础数据
    """
    __tablename__ = "property_projects"

    id = Column(Integer, primary_key=True, index=True, comment="项目ID")
    name = Column(String(100), nullable=False, comment="小区名称")
    location = Column(String(200), comment="地理位置")
    total_buildings = Column(Integer, default=0, comment="楼栋总数")
    total_houses = Column(Integer, default=0, comment="房屋总数")
    developer = Column(String(100), comment="开发商")
    property_company = Column(String(100), comment="物业公司")
    built_year = Column(Integer, comment="建成年份")
    description = Column(Text, comment="项目描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个项目包含多个房产
    properties = relationship("Property", back_populates="project")


class Property(Base):
    """
    房产信息模型
    记录房号、户型、面积、产权性质等，支持空置/出租状态标识
    """
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True, comment="房产ID")
    project_id = Column(Integer, ForeignKey("property_projects.id"), nullable=False, comment="所属项目ID")
    building_number = Column(String(20), nullable=False, comment="楼栋号")
    room_number = Column(String(20), nullable=False, comment="房间号")
    floor = Column(Integer, comment="楼层")
    total_floors = Column(Integer, comment="总楼层")
    house_type = Column(String(50), comment="户型（如：三室一厅）")
    area = Column(Float, comment="建筑面积（平方米）")
    usable_area = Column(Float, comment="使用面积（平方米）")
    property_type = Column(String(50), comment="产权性质（如：商品房、经济适用房）")
    status = Column(String(20), default=PropertyStatus.VACANT.value, comment="状态：空置/出租/自住")
    orientation = Column(String(20), comment="朝向")
    decoration = Column(String(50), comment="装修情况")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    project = relationship("PropertyProject", back_populates="properties")
    owners = relationship("OwnerProperty", back_populates="property_info")


class Owner(Base):
    """
    业主/住户信息模型
    登记姓名、联系方式、家庭成员、车辆信息等
    """
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True, comment="业主ID")
    name = Column(String(50), nullable=False, comment="姓名")
    id_card = Column(String(18), comment="身份证号")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="电子邮箱")
    address = Column(String(200), comment="联系地址")
    is_owner = Column(Boolean, default=True, comment="是否为业主（True:业主, False:住户）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    properties = relationship("OwnerProperty", back_populates="owner")
    family_members = relationship("FamilyMember", back_populates="owner")
    vehicles = relationship("Vehicle", back_populates="owner")


class OwnerProperty(Base):
    """
    业主-房产关联模型
    实现业主与房产的多对多关系
    """
    __tablename__ = "owner_properties"

    id = Column(Integer, primary_key=True, index=True, comment="关联ID")
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False, comment="业主ID")
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, comment="房产ID")
    ownership_type = Column(String(50), comment="权属类型（如：全部所有、部分所有）")
    share_ratio = Column(Float, default=100.0, comment="产权比例（%）")
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="结束日期（如租赁到期）")
    is_primary = Column(Boolean, default=True, comment="是否为主要居所")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    owner = relationship("Owner", back_populates="properties")
    property_info = relationship("Property", back_populates="owners")


class FamilyMember(Base):
    """
    家庭成员模型
    """
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True, comment="成员ID")
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False, comment="所属业主ID")
    name = Column(String(50), nullable=False, comment="姓名")
    relation = Column(String(50), comment="与业主关系")
    phone = Column(String(20), comment="联系电话")
    id_card = Column(String(18), comment="身份证号")
    gender = Column(String(10), comment="性别")
    birth_date = Column(DateTime, comment="出生日期")
    is_emergency_contact = Column(Boolean, default=False, comment="是否为紧急联系人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    owner = relationship("Owner", back_populates="family_members")


class Vehicle(Base):
    """
    车辆信息模型
    """
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True, comment="车辆ID")
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False, comment="所属业主ID")
    plate_number = Column(String(20), nullable=False, comment="车牌号")
    vehicle_type = Column(String(50), comment="车辆类型（如：轿车、SUV）")
    brand = Column(String(50), comment="品牌")
    model = Column(String(50), comment="型号")
    color = Column(String(20), comment="颜色")
    parking_space = Column(String(50), comment="停车位编号")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    owner = relationship("Owner", back_populates="vehicles")
