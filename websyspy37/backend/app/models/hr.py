"""
人事模块数据模型
包含部门、员工、职位等模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.config import Base


class Department(Base):
    """
    部门模型
    存储部门基本信息
    """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, comment="部门ID")
    dept_no = Column(String(50), unique=True, nullable=False, comment="部门编号")
    name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="上级部门ID")
    manager = Column(String(50), comment="部门负责人")
    phone = Column(String(20), comment="部门电话")
    description = Column(Text, comment="部门描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个部门可以有多个下级部门
    children = relationship("Department", backref="parent", remote_side=[id])
    # 关系：一个部门可以有多个员工
    employees = relationship("Employee", back_populates="department")


class Position(Base):
    """
    职位模型
    存储职位基本信息
    """
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True, comment="职位ID")
    position_no = Column(String(50), unique=True, nullable=False, comment="职位编号")
    name = Column(String(100), nullable=False, comment="职位名称")
    level = Column(Integer, default=1, comment="职位级别")
    base_salary = Column(Float, default=0.0, comment="基本工资")
    description = Column(Text, comment="职位描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个职位可以有多个员工
    employees = relationship("Employee", back_populates="position")


class Employee(Base):
    """
    员工模型
    存储员工基本信息
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, comment="员工ID")
    employee_no = Column(String(50), unique=True, nullable=False, comment="员工编号")
    name = Column(String(50), nullable=False, comment="员工姓名")
    gender = Column(String(10), comment="性别：男/女")
    birthday = Column(Date, comment="出生日期")
    id_card = Column(String(18), comment="身份证号")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    address = Column(String(255), comment="住址")
    department_id = Column(Integer, ForeignKey("departments.id"), comment="部门ID")
    position_id = Column(Integer, ForeignKey("positions.id"), comment="职位ID")
    entry_date = Column(Date, comment="入职日期")
    status = Column(String(20), default="在职", comment="状态：在职/离职/休假")
    salary = Column(Float, default=0.0, comment="薪资")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：员工属于一个部门
    department = relationship("Department", back_populates="employees")
    # 关系：员工属于一个职位
    position = relationship("Position", back_populates="employees")


class Attendance(Base):
    """
    考勤模型
    存储员工考勤记录
    """
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True, comment="考勤ID")
    employee_id = Column(Integer, ForeignKey("employees.id"), comment="员工ID")
    attendance_date = Column(Date, default=date.today, comment="考勤日期")
    check_in = Column(DateTime, comment="上班打卡时间")
    check_out = Column(DateTime, comment="下班打卡时间")
    status = Column(String(20), default="正常", comment="状态：正常/迟到/早退/缺勤/请假")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class SalaryRecord(Base):
    """
    薪资发放记录模型
    存储员工薪资发放记录
    """
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    employee_id = Column(Integer, ForeignKey("employees.id"), comment="员工ID")
    year = Column(Integer, nullable=False, comment="年份")
    month = Column(Integer, nullable=False, comment="月份")
    base_salary = Column(Float, default=0.0, comment="基本工资")
    bonus = Column(Float, default=0.0, comment="奖金")
    allowance = Column(Float, default=0.0, comment="补贴")
    deduction = Column(Float, default=0.0, comment="扣款")
    tax = Column(Float, default=0.0, comment="个税")
    actual_salary = Column(Float, default=0.0, comment="实发工资")
    status = Column(String(20), default="待发放", comment="状态：待发放/已发放")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
