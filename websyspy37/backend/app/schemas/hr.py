"""
人事模块Pydantic schemas
用于API的数据验证和序列化
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime, date
from app.validators import is_valid_phone, is_valid_email, is_valid_id_card


# 部门相关schemas
class DepartmentBase(BaseModel):
    """
    部门基础schema
    """
    dept_no: str
    name: str
    parent_id: Optional[int] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

    @field_validator('dept_no')
    @classmethod
    def validate_dept_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('部门编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('部门编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('部门名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('部门名称长度不能超过100个字符')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v

    @field_validator('manager')
    @classmethod
    def validate_manager(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('负责人姓名长度不能超过50个字符')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class DepartmentCreate(DepartmentBase):
    """
    部门创建schema
    """
    pass


class DepartmentUpdate(BaseModel):
    """
    部门更新schema
    """
    dept_no: Optional[str] = None
    name: Optional[str] = None
    parent_id: Optional[int] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

    @field_validator('dept_no')
    @classmethod
    def validate_dept_no_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('部门编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 100:
            raise ValueError('部门名称长度不能超过100个字符')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v


class DepartmentResponse(DepartmentBase):
    """
    部门响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 职位相关schemas
class PositionBase(BaseModel):
    """
    职位基础schema
    """
    position_no: str
    name: str
    level: int = 1
    base_salary: float = 0.0
    description: Optional[str] = None

    @field_validator('position_no')
    @classmethod
    def validate_position_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('职位编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('职位编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('职位名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('职位名称长度不能超过100个字符')
        return v

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            return 1
        if v < 1 or v > 10:
            raise ValueError('职位级别必须在1-10之间')
        return v

    @field_validator('base_salary')
    @classmethod
    def validate_base_salary(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('基本工资不能为负数')
        if v > 100000000:
            raise ValueError('基本工资不能超过100000000')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class PositionCreate(PositionBase):
    """
    职位创建schema
    """
    pass


class PositionUpdate(BaseModel):
    """
    职位更新schema
    """
    position_no: Optional[str] = None
    name: Optional[str] = None
    level: Optional[int] = None
    base_salary: Optional[float] = None
    description: Optional[str] = None

    @field_validator('level')
    @classmethod
    def validate_level_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 1 or v > 10:
            raise ValueError('职位级别必须在1-10之间')
        return v

    @field_validator('base_salary')
    @classmethod
    def validate_base_salary_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('基本工资不能为负数')
        if v > 100000000:
            raise ValueError('基本工资不能超过100000000')
        return round(v, 2)


class PositionResponse(PositionBase):
    """
    职位响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 员工相关schemas
class EmployeeBase(BaseModel):
    """
    员工基础schema
    """
    employee_no: str
    name: str
    gender: Optional[str] = None
    birthday: Optional[date] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    entry_date: Optional[date] = None
    status: str = "在职"
    salary: float = 0.0

    @field_validator('employee_no')
    @classmethod
    def validate_employee_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('员工编号不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('员工编号长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('员工姓名不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('员工姓名长度不能超过50个字符')
        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if v not in ['男', '女', '未知']:
            raise ValueError('性别必须是"男"、"女"或"未知"')
        return v

    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().upper()
        if not is_valid_id_card(v):
            raise ValueError('身份证号格式不正确')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 254:
            raise ValueError('邮箱长度不能超过254个字符')
        if not is_valid_email(v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('地址长度不能超过500个字符')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "在职"
        v = v.strip()
        valid_statuses = ["在职", "离职", "休假", "退休"]
        if v not in valid_statuses:
            raise ValueError(f'员工状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('薪资不能为负数')
        if v > 100000000:
            raise ValueError('薪资不能超过100000000')
        return round(v, 2)


class EmployeeCreate(EmployeeBase):
    """
    员工创建schema
    """
    pass


class EmployeeUpdate(BaseModel):
    """
    员工更新schema
    """
    employee_no: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    entry_date: Optional[date] = None
    status: Optional[str] = None
    salary: Optional[float] = None

    @field_validator('id_card')
    @classmethod
    def validate_id_card_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().upper()
        if not is_valid_id_card(v):
            raise ValueError('身份证号格式不正确')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v

    @field_validator('email')
    @classmethod
    def validate_email_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 254:
            raise ValueError('邮箱长度不能超过254个字符')
        if not is_valid_email(v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["在职", "离职", "休假", "退休"]
        if v not in valid_statuses:
            raise ValueError(f'员工状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('salary')
    @classmethod
    def validate_salary_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('薪资不能为负数')
        if v > 100000000:
            raise ValueError('薪资不能超过100000000')
        return round(v, 2)


class EmployeeResponse(EmployeeBase):
    """
    员工响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentResponse] = None
    position: Optional[PositionResponse] = None

    class Config:
        from_attributes = True


# 考勤相关schemas
class AttendanceBase(BaseModel):
    """
    考勤基础schema
    """
    employee_id: int
    attendance_date: date = date.today()
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str = "正常"
    remark: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "正常"
        v = v.strip()
        valid_statuses = ["正常", "迟到", "早退", "旷工", "请假"]
        if v not in valid_statuses:
            raise ValueError(f'考勤状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('remark')
    @classmethod
    def validate_remark(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('备注长度不能超过500个字符')
        return v


class AttendanceCreate(AttendanceBase):
    """
    考勤创建schema
    """
    pass


class AttendanceUpdate(BaseModel):
    """
    考勤更新schema
    """
    employee_id: Optional[int] = None
    attendance_date: Optional[date] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["正常", "迟到", "早退", "旷工", "请假"]
        if v not in valid_statuses:
            raise ValueError(f'考勤状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class AttendanceResponse(AttendanceBase):
    """
    考勤响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 薪资记录相关schemas
class SalaryRecordBase(BaseModel):
    """
    薪资记录基础schema
    """
    employee_id: int
    year: int
    month: int
    base_salary: float = 0.0
    bonus: float = 0.0
    allowance: float = 0.0
    deduction: float = 0.0
    tax: float = 0.0
    actual_salary: float = 0.0
    status: str = "待发放"

    @field_validator('year')
    @classmethod
    def validate_year(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('年份不能为空')
        if v < 2000 or v > 2100:
            raise ValueError('年份必须在2000-2100之间')
        return v

    @field_validator('month')
    @classmethod
    def validate_month(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('月份不能为空')
        if v < 1 or v > 12:
            raise ValueError('月份必须在1-12之间')
        return v

    @field_validator('base_salary', 'bonus', 'allowance', 'deduction', 'tax', 'actual_salary')
    @classmethod
    def validate_amounts(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('金额不能为负数')
        if v > 100000000:
            raise ValueError('金额不能超过100000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待发放"
        v = v.strip()
        valid_statuses = ["待发放", "已发放", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'薪资状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class SalaryRecordCreate(SalaryRecordBase):
    """
    薪资记录创建schema
    """
    pass


class SalaryRecordUpdate(BaseModel):
    """
    薪资记录更新schema
    """
    employee_id: Optional[int] = None
    year: Optional[int] = None
    month: Optional[int] = None
    base_salary: Optional[float] = None
    bonus: Optional[float] = None
    allowance: Optional[float] = None
    deduction: Optional[float] = None
    tax: Optional[float] = None
    actual_salary: Optional[float] = None
    status: Optional[str] = None

    @field_validator('year')
    @classmethod
    def validate_year_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 2000 or v > 2100:
            raise ValueError('年份必须在2000-2100之间')
        return v

    @field_validator('month')
    @classmethod
    def validate_month_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 1 or v > 12:
            raise ValueError('月份必须在1-12之间')
        return v

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待发放", "已发放", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'薪资状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class SalaryRecordResponse(SalaryRecordBase):
    """
    薪资记录响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime
    employee: Optional[EmployeeResponse] = None

    class Config:
        from_attributes = True
