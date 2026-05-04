"""
Pydantic数据模型定义
用于API的输入验证和输出序列化
包含严格的表单数据校验规则
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import re


class PropertyStatus(str, Enum):
    """
    房产状态枚举
    """
    VACANT = "vacant"
    RENTED = "rented"
    OCCUPIED = "occupied"


# 正则表达式模式
PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ID_CARD_PATTERN = re.compile(r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$')
CHINESE_NAME_PATTERN = re.compile(r'^[\u4e00-\u9fa5]{2,10}$')
PLATE_NUMBER_PATTERN = re.compile(r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{5}$')


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    验证手机号格式
    """
    if phone is None or phone == '':
        return None
    if not PHONE_PATTERN.match(phone):
        raise ValueError('手机号格式不正确，应为11位数字，以1开头')
    return phone


def validate_email(email: Optional[str]) -> Optional[str]:
    """
    验证邮箱格式
    """
    if email is None or email == '':
        return None
    if not EMAIL_PATTERN.match(email):
        raise ValueError('邮箱格式不正确')
    return email


def validate_id_card(id_card: Optional[str]) -> Optional[str]:
    """
    验证身份证号格式
    """
    if id_card is None or id_card == '':
        return None
    if not ID_CARD_PATTERN.match(id_card.upper()):
        raise ValueError('身份证号格式不正确')
    return id_card.upper()


def validate_chinese_name(name: str) -> str:
    """
    验证中文姓名格式
    """
    if not name or len(name.strip()) == 0:
        raise ValueError('姓名不能为空')
    name = name.strip()
    if len(name) < 2:
        raise ValueError('姓名至少需要2个字符')
    if len(name) > 20:
        raise ValueError('姓名不能超过20个字符')
    return name


def validate_plate_number(plate: str) -> str:
    """
    验证车牌号格式
    """
    if not plate or len(plate.strip()) == 0:
        raise ValueError('车牌号不能为空')
    plate = plate.strip().upper()
    if len(plate) < 7 or len(plate) > 8:
        raise ValueError('车牌号长度不正确')
    return plate


# ==================== 物业项目相关模型 ====================


class PropertyProjectBase(BaseModel):
    """
    物业项目基础模型
    """
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="小区名称（2-100个字符）"
    )
    location: Optional[str] = Field(
        None, 
        max_length=200, 
        description="地理位置（最多200个字符）"
    )
    total_buildings: Optional[int] = Field(
        0, 
        ge=0, 
        le=1000, 
        description="楼栋总数（0-1000）"
    )
    total_houses: Optional[int] = Field(
        0, 
        ge=0, 
        le=100000, 
        description="房屋总数（0-100000）"
    )
    developer: Optional[str] = Field(
        None, 
        max_length=100, 
        description="开发商（最多100个字符）"
    )
    property_company: Optional[str] = Field(
        None, 
        max_length=100, 
        description="物业公司（最多100个字符）"
    )
    built_year: Optional[int] = Field(
        None, 
        ge=1900, 
        le=2100, 
        description="建成年份（1900-2100）"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="项目描述（最多1000个字符）"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v or len(v) < 2:
            raise ValueError('项目名称不能为空且至少2个字符')
        if len(v) > 100:
            raise ValueError('项目名称不能超过100个字符')
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('地理位置不能超过200个字符')
        return v if v else None


class PropertyProjectCreate(PropertyProjectBase):
    """
    创建物业项目模型
    """
    pass


class PropertyProjectUpdate(BaseModel):
    """
    更新物业项目模型
    """
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100, 
        description="小区名称（2-100个字符）"
    )
    location: Optional[str] = Field(
        None, 
        max_length=200, 
        description="地理位置（最多200个字符）"
    )
    total_buildings: Optional[int] = Field(
        None, 
        ge=0, 
        le=1000, 
        description="楼栋总数（0-1000）"
    )
    total_houses: Optional[int] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="房屋总数（0-100000）"
    )
    developer: Optional[str] = Field(
        None, 
        max_length=100, 
        description="开发商（最多100个字符）"
    )
    property_company: Optional[str] = Field(
        None, 
        max_length=100, 
        description="物业公司（最多100个字符）"
    )
    built_year: Optional[int] = Field(
        None, 
        ge=1900, 
        le=2100, 
        description="建成年份（1900-2100）"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="项目描述（最多1000个字符）"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v or len(v) < 2:
            raise ValueError('项目名称不能为空且至少2个字符')
        if len(v) > 100:
            raise ValueError('项目名称不能超过100个字符')
        return v


class PropertyProject(PropertyProjectBase):
    """
    物业项目响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyProjectList(BaseModel):
    """
    物业项目列表响应模型
    """
    items: List[PropertyProject]
    total: int


# ==================== 房产信息相关模型 ====================


class PropertyBase(BaseModel):
    """
    房产信息基础模型
    """
    project_id: int = Field(
        ..., 
        ge=1, 
        description="所属项目ID（必须大于0）"
    )
    building_number: str = Field(
        ..., 
        min_length=1, 
        max_length=20, 
        description="楼栋号（1-20个字符）"
    )
    room_number: str = Field(
        ..., 
        min_length=1, 
        max_length=20, 
        description="房间号（1-20个字符）"
    )
    floor: Optional[int] = Field(
        None, 
        ge=1, 
        le=500, 
        description="楼层（1-500层）"
    )
    total_floors: Optional[int] = Field(
        None, 
        ge=1, 
        le=500, 
        description="总楼层（1-500层）"
    )
    house_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="户型（最多50个字符）"
    )
    area: Optional[float] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="建筑面积（0-100000平方米）"
    )
    usable_area: Optional[float] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="使用面积（0-100000平方米）"
    )
    property_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="产权性质（最多50个字符）"
    )
    status: Optional[PropertyStatus] = Field(
        PropertyStatus.VACANT, 
        description="状态：空置/出租/自住"
    )
    orientation: Optional[str] = Field(
        None, 
        max_length=20, 
        description="朝向（最多20个字符）"
    )
    decoration: Optional[str] = Field(
        None, 
        max_length=50, 
        description="装修情况（最多50个字符）"
    )
    remarks: Optional[str] = Field(
        None, 
        max_length=500, 
        description="备注（最多500个字符）"
    )

    @field_validator('building_number')
    @classmethod
    def validate_building_number(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v:
            raise ValueError('楼栋号不能为空')
        if len(v) > 20:
            raise ValueError('楼栋号不能超过20个字符')
        return v

    @field_validator('room_number')
    @classmethod
    def validate_room_number(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v:
            raise ValueError('房间号不能为空')
        if len(v) > 20:
            raise ValueError('房间号不能超过20个字符')
        return v

    @field_validator('usable_area')
    @classmethod
    def validate_usable_area(cls, v: Optional[float], info) -> Optional[float]:
        if v is None:
            return v
        area = info.data.get('area')
        if area is not None and v > area:
            raise ValueError('使用面积不能大于建筑面积')
        return v


class PropertyCreate(PropertyBase):
    """
    创建房产信息模型
    """
    pass


class PropertyUpdate(BaseModel):
    """
    更新房产信息模型
    """
    building_number: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=20, 
        description="楼栋号（1-20个字符）"
    )
    room_number: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=20, 
        description="房间号（1-20个字符）"
    )
    floor: Optional[int] = Field(
        None, 
        ge=1, 
        le=500, 
        description="楼层（1-500层）"
    )
    total_floors: Optional[int] = Field(
        None, 
        ge=1, 
        le=500, 
        description="总楼层（1-500层）"
    )
    house_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="户型（最多50个字符）"
    )
    area: Optional[float] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="建筑面积（0-100000平方米）"
    )
    usable_area: Optional[float] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="使用面积（0-100000平方米）"
    )
    property_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="产权性质（最多50个字符）"
    )
    status: Optional[PropertyStatus] = Field(
        None, 
        description="状态：空置/出租/自住"
    )
    orientation: Optional[str] = Field(
        None, 
        max_length=20, 
        description="朝向（最多20个字符）"
    )
    decoration: Optional[str] = Field(
        None, 
        max_length=50, 
        description="装修情况（最多50个字符）"
    )
    remarks: Optional[str] = Field(
        None, 
        max_length=500, 
        description="备注（最多500个字符）"
    )

    @field_validator('building_number')
    @classmethod
    def validate_building_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError('楼栋号不能为空')
        if len(v) > 20:
            raise ValueError('楼栋号不能超过20个字符')
        return v

    @field_validator('room_number')
    @classmethod
    def validate_room_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError('房间号不能为空')
        if len(v) > 20:
            raise ValueError('房间号不能超过20个字符')
        return v


class Property(PropertyBase):
    """
    房产信息响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[PropertyProject] = None

    class Config:
        from_attributes = True


class PropertyList(BaseModel):
    """
    房产信息列表响应模型
    """
    items: List[Property]
    total: int


# ==================== 业主/住户相关模型 ====================


class FamilyMemberBase(BaseModel):
    """
    家庭成员基础模型
    """
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="姓名（2-50个字符）"
    )
    relation: Optional[str] = Field(
        None, 
        max_length=50, 
        description="与业主关系（最多50个字符）"
    )
    phone: Optional[str] = Field(
        None, 
        max_length=20, 
        description="联系电话（最多20个字符）"
    )
    id_card: Optional[str] = Field(
        None, 
        max_length=18, 
        description="身份证号（18位）"
    )
    gender: Optional[str] = Field(
        None, 
        max_length=10, 
        description="性别（男/女）"
    )
    birth_date: Optional[datetime] = Field(
        None, 
        description="出生日期"
    )
    is_emergency_contact: Optional[bool] = Field(
        False, 
        description="是否为紧急联系人"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_chinese_name(v)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        return validate_id_card(v)

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v not in ['男', '女']:
            raise ValueError('性别只能是"男"或"女"')
        return v


class FamilyMemberCreate(FamilyMemberBase):
    """
    创建家庭成员模型
    """
    pass


class FamilyMember(FamilyMemberBase):
    """
    家庭成员响应模型
    """
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    """
    车辆信息基础模型
    """
    plate_number: str = Field(
        ..., 
        min_length=7, 
        max_length=20, 
        description="车牌号（7-20个字符）"
    )
    vehicle_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="车辆类型（最多50个字符）"
    )
    brand: Optional[str] = Field(
        None, 
        max_length=50, 
        description="品牌（最多50个字符）"
    )
    model: Optional[str] = Field(
        None, 
        max_length=50, 
        description="型号（最多50个字符）"
    )
    color: Optional[str] = Field(
        None, 
        max_length=20, 
        description="颜色（最多20个字符）"
    )
    parking_space: Optional[str] = Field(
        None, 
        max_length=50, 
        description="停车位编号（最多50个字符）"
    )

    @field_validator('plate_number')
    @classmethod
    def validate_plate_number(cls, v: str) -> str:
        return validate_plate_number(v)


class VehicleCreate(VehicleBase):
    """
    创建车辆信息模型
    """
    pass


class Vehicle(VehicleBase):
    """
    车辆信息响应模型
    """
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OwnerBase(BaseModel):
    """
    业主/住户基础模型
    """
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="姓名（2-50个字符）"
    )
    id_card: Optional[str] = Field(
        None, 
        max_length=18, 
        description="身份证号（18位）"
    )
    phone: Optional[str] = Field(
        None, 
        max_length=20, 
        description="联系电话（最多20个字符）"
    )
    email: Optional[str] = Field(
        None, 
        max_length=100, 
        description="电子邮箱（最多100个字符）"
    )
    address: Optional[str] = Field(
        None, 
        max_length=200, 
        description="联系地址（最多200个字符）"
    )
    is_owner: Optional[bool] = Field(
        True, 
        description="是否为业主（True:业主, False:住户）"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_chinese_name(v)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return validate_email(v)

    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        return validate_id_card(v)

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('联系地址不能超过200个字符')
        return v if v else None


class OwnerCreate(OwnerBase):
    """
    创建业主/住户模型
    """
    pass


class OwnerUpdate(BaseModel):
    """
    更新业主/住户模型
    """
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=50, 
        description="姓名（2-50个字符）"
    )
    id_card: Optional[str] = Field(
        None, 
        max_length=18, 
        description="身份证号（18位）"
    )
    phone: Optional[str] = Field(
        None, 
        max_length=20, 
        description="联系电话（最多20个字符）"
    )
    email: Optional[str] = Field(
        None, 
        max_length=100, 
        description="电子邮箱（最多100个字符）"
    )
    address: Optional[str] = Field(
        None, 
        max_length=200, 
        description="联系地址（最多200个字符）"
    )
    is_owner: Optional[bool] = Field(
        None, 
        description="是否为业主（True:业主, False:住户）"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_chinese_name(v)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return validate_email(v)

    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        return validate_id_card(v)


class Owner(OwnerBase):
    """
    业主/住户响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    family_members: List[FamilyMember] = []
    vehicles: List[Vehicle] = []

    class Config:
        from_attributes = True


class OwnerList(BaseModel):
    """
    业主/住户列表响应模型
    """
    items: List[Owner]
    total: int


# ==================== 业主-房产关联模型 ====================


class OwnerPropertyBase(BaseModel):
    """
    业主-房产关联基础模型
    """
    owner_id: int = Field(
        ..., 
        ge=1, 
        description="业主ID（必须大于0）"
    )
    property_id: int = Field(
        ..., 
        ge=1, 
        description="房产ID（必须大于0）"
    )
    ownership_type: Optional[str] = Field(
        None, 
        max_length=50, 
        description="权属类型（最多50个字符）"
    )
    share_ratio: Optional[float] = Field(
        100.0, 
        ge=0, 
        le=100, 
        description="产权比例（0-100%）"
    )
    start_date: Optional[datetime] = Field(
        None, 
        description="开始日期"
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="结束日期"
    )
    is_primary: Optional[bool] = Field(
        True, 
        description="是否为主要居所"
    )


class OwnerPropertyCreate(OwnerPropertyBase):
    """
    创建业主-房产关联模型
    """
    pass


class OwnerProperty(OwnerPropertyBase):
    """
    业主-房产关联响应模型
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 统计模型 ====================


class DashboardStats(BaseModel):
    """
    首页统计数据模型
    """
    total_projects: int
    total_properties: int
    total_owners: int
    vacant_properties: int
    rented_properties: int
    occupied_properties: int
