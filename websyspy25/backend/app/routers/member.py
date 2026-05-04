from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date, timedelta
import uuid

from ..database import get_db
from ..models.member import Member, CoursePackage
from ..schemas.member import (
    MemberCreate, MemberUpdate, MemberResponse, MemberListResponse,
    CoursePackageCreate, CoursePackageUpdate, CoursePackageResponse, CoursePackageListResponse
)

"""
会员和课程包管理API路由
实现会员增删改查、课程包购买管理等功能
"""

router = APIRouter(
    prefix="/api/members",
    tags=["会员管理"]
)


def generate_package_no() -> str:
    """
    生成课程包编号
    格式: CP + 年月日 + 6位随机字符
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"CP{date_str}{random_str}"


# ========== 会员相关API ==========

@router.post("/", response_model=MemberResponse, summary="创建会员")
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """
    创建新会员记录
    - 检查手机号是否已存在
    """
    # 检查手机号是否已存在
    existing = db.query(Member).filter(Member.phone == member.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号码已存在")
    
    db_member = Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("/", response_model=MemberListResponse, summary="获取会员列表")
def get_members(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    name: Optional[str] = Query(None, description="会员姓名（模糊搜索）"),
    phone: Optional[str] = Query(None, description="手机号码（模糊搜索）"),
    status: Optional[str] = Query(None, description="状态：正常/冻结/过期"),
    level: Optional[str] = Query(None, description="会员等级"),
    db: Session = Depends(get_db)
):
    """
    分页获取会员列表
    支持按姓名、手机号、状态、等级筛选
    """
    query = db.query(Member)
    
    # 应用筛选条件
    if name:
        query = query.filter(Member.name.contains(name))
    if phone:
        query = query.filter(Member.phone.contains(phone))
    if status:
        query = query.filter(Member.status == status)
    if level:
        query = query.filter(Member.level == level)
    
    # 获取总记录数
    total = query.count()
    
    # 分页查询
    members = query.order_by(Member.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return MemberListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=members
    )


@router.get("/{member_id}", response_model=MemberResponse, summary="获取单个会员详情")
def get_member(member_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个会员详情
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    return member


@router.put("/{member_id}", response_model=MemberResponse, summary="更新会员信息")
def update_member(member_id: int, member_update: MemberUpdate, db: Session = Depends(get_db)):
    """
    更新会员信息
    """
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查手机号是否冲突
    if member_update.phone and member_update.phone != db_member.phone:
        existing = db.query(Member).filter(Member.phone == member_update.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="该手机号码已被其他会员使用")
    
    # 只更新非空字段
    update_data = member_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/{member_id}", summary="删除会员")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """
    删除会员
    """
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查是否有关联的课程包
    packages = db.query(CoursePackage).filter(CoursePackage.member_id == member_id).first()
    if packages:
        raise HTTPException(status_code=400, detail="该会员有关联的课程包，无法删除")
    
    db.delete(db_member)
    db.commit()
    return {"message": "删除成功", "member_id": member_id}


# ========== 课程包相关API ==========

@router.post("/packages/", response_model=CoursePackageResponse, summary="购买课程包")
def create_package(package: CoursePackageCreate, db: Session = Depends(get_db)):
    """
    为会员购买课程包
    - 自动生成课程包编号
    - 计算总金额和剩余课时
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == package.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 创建课程包数据
    package_data = package.model_dump()
    package_data["package_no"] = generate_package_no()
    package_data["remaining_lessons"] = package.total_lessons + package.bonus_lessons
    package_data["total_amount"] = package.unit_price * package.total_lessons
    
    db_package = CoursePackage(**package_data)
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package


@router.get("/packages/", response_model=CoursePackageListResponse, summary="获取课程包列表")
def get_packages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    status: Optional[str] = Query(None, description="状态：有效/已用完/已过期/已冻结"),
    db: Session = Depends(get_db)
):
    """
    分页获取课程包列表
    支持按会员、教练、状态筛选
    """
    query = db.query(CoursePackage)
    
    # 应用筛选条件
    if member_id:
        query = query.filter(CoursePackage.member_id == member_id)
    if coach_id:
        query = query.filter(CoursePackage.coach_id == coach_id)
    if status:
        query = query.filter(CoursePackage.status == status)
    
    # 获取总记录数
    total = query.count()
    
    # 分页查询
    packages = query.order_by(CoursePackage.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return CoursePackageListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=packages
    )


@router.get("/packages/{package_id}", response_model=CoursePackageResponse, summary="获取单个课程包详情")
def get_package(package_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个课程包详情
    """
    package = db.query(CoursePackage).filter(CoursePackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    return package


@router.put("/packages/{package_id}", response_model=CoursePackageResponse, summary="更新课程包信息")
def update_package(package_id: int, package_update: CoursePackageUpdate, db: Session = Depends(get_db)):
    """
    更新课程包信息
    """
    db_package = db.query(CoursePackage).filter(CoursePackage.id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    # 只更新非空字段
    update_data = package_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_package, key, value)
    
    db.commit()
    db.refresh(db_package)
    return db_package


@router.get("/{member_id}/packages/", response_model=List[CoursePackageResponse], summary="获取会员的课程包列表")
def get_member_packages(
    member_id: int,
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取指定会员的所有课程包
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    query = db.query(CoursePackage).filter(CoursePackage.member_id == member_id)
    
    if status:
        query = query.filter(CoursePackage.status == status)
    
    packages = query.order_by(CoursePackage.created_at.desc()).all()
    return packages
