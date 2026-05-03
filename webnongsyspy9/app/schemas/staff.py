from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date


class StaffBase(BaseModel):
    """
    人员管理基础模型
    包含员工信息的公共字段
    """
    
    # 员工工号
    staff_number: str = Field(..., min_length=1, max_length=50, description="员工工号")
    
    # 员工姓名
    name: str = Field(..., min_length=1, max_length=100, description="员工姓名")
    
    # 性别
    gender: Optional[str] = Field(None, pattern="^(男|女|其他)?$", description="性别")
    
    # 年龄
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    
    # 联系电话
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    
    # 邮箱
    email: Optional[EmailStr] = Field(None, description="邮箱")
    
    # 身份证号
    id_card: Optional[str] = Field(None, max_length=50, description="身份证号")
    
    # 所属角色ID
    role_id: Optional[int] = Field(None, description="所属角色ID")
    
    # 岗位职责
    position: str = Field(..., min_length=1, max_length=200, description="岗位职责")
    
    # 所属部门
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    
    # 操作权限（以逗号分隔的权限列表）
    # 当员工有自定义权限时使用，否则使用角色权限
    permissions: Optional[str] = Field(None, description="操作权限")
    
    # 入职日期
    join_date: Optional[date] = Field(None, description="入职日期")
    
    # 员工状态（在职/离职/休假等）
    status: str = Field(default="在职", min_length=1, max_length=50, description="员工状态")
    
    # 备注信息
    remarks: Optional[str] = Field(None, description="备注信息")


class StaffCreate(StaffBase):
    """
    创建员工时使用的模型
    继承自StaffBase，无需额外字段
    """
    pass


class StaffUpdate(BaseModel):
    """
    更新员工时使用的模型
    所有字段都是可选的
    """
    
    staff_number: Optional[str] = Field(None, min_length=1, max_length=50, description="员工工号")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="员工姓名")
    gender: Optional[str] = Field(None, pattern="^(男|女|其他)?$", description="性别")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    id_card: Optional[str] = Field(None, max_length=50, description="身份证号")
    role_id: Optional[int] = Field(None, description="所属角色ID")
    position: Optional[str] = Field(None, min_length=1, max_length=200, description="岗位职责")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    permissions: Optional[str] = Field(None, description="操作权限")
    join_date: Optional[date] = Field(None, description="入职日期")
    status: Optional[str] = Field(None, min_length=1, max_length=50, description="员工状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class StaffRoleInfo(BaseModel):
    """
    员工角色信息
    """
    role_id: Optional[int] = Field(None, description="角色ID")
    role_name: Optional[str] = Field(None, description="角色名称")
    role_code: Optional[str] = Field(None, description="角色代码")
    role_permissions: Optional[List[str]] = Field(None, description="角色权限列表")


class StaffResponse(StaffBase):
    """
    员工响应模型
    包含从数据库读取时返回的所有字段
    """
    
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 角色信息
    role_info: Optional[StaffRoleInfo] = Field(None, description="角色信息")
    
    # 解析后的权限列表
    permission_list: Optional[List[str]] = Field(None, description="自定义权限列表")
    
    # 实际生效的权限（角色权限 + 自定义权限）
    effective_permissions: Optional[List[str]] = Field(None, description="实际生效权限")
    
    class Config:
        from_attributes = True
