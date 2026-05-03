"""
工作人员管理API路由
提供工作人员的增删改查功能
"""
import os
import re
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from database import get_db
from models.staff import Staff
from config import FACE_PHOTO_DIR, ALLOWED_IMAGE_TYPES

router = APIRouter(prefix="/api/staff", tags=["工作人员管理"])

# 数据校验函数
def validate_phone(phone: Optional[str]) -> Optional[str]:
    """校验手机号格式"""
    if not phone:
        return None
    phone = phone.strip()
    if not phone:
        return None
    # 11位手机号，以1开头
    phone_regex = r'^1[3-9]\d{9}$'
    if not re.match(phone_regex, phone):
        raise HTTPException(status_code=400, detail="请输入正确的11位手机号")
    return phone


def validate_email(email: Optional[str]) -> Optional[str]:
    """校验邮箱格式"""
    if not email:
        return None
    email = email.strip()
    if not email:
        return None
    # 简单邮箱格式校验
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="请输入正确的邮箱格式")
    if len(email) > 100:
        raise HTTPException(status_code=400, detail="邮箱不能超过100个字符")
    return email


def validate_id_card(id_card: Optional[str]) -> Optional[str]:
    """校验身份证号格式"""
    if not id_card:
        return None
    id_card = id_card.strip().upper()
    if not id_card:
        return None
    # 15位或18位身份证号
    id_card_regex = r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X)$)'
    if not re.match(id_card_regex, id_card):
        raise HTTPException(status_code=400, detail="请输入正确的15位或18位身份证号")
    return id_card


def validate_staff_data(
    staff_no: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    id_card: Optional[str] = None,
    is_create: bool = False
) -> dict:
    """
    校验工作人员数据
    返回处理后的数据字典
    """
    validated_data = {}
    
    # 工号校验（创建时必填）
    if staff_no is not None:
        staff_no = staff_no.strip()
        if is_create and not staff_no:
            raise HTTPException(status_code=400, detail="请输入工号")
        if staff_no:
            if len(staff_no) > 50:
                raise HTTPException(status_code=400, detail="工号不能超过50个字符")
            validated_data['staff_no'] = staff_no
    
    # 姓名校验（创建时必填）
    if name is not None:
        name = name.strip()
        if is_create and not name:
            raise HTTPException(status_code=400, detail="请输入姓名")
        if name:
            if len(name) > 100:
                raise HTTPException(status_code=400, detail="姓名不能超过100个字符")
            validated_data['name'] = name
    
    # 手机号校验
    validated_data['phone'] = validate_phone(phone)
    
    # 邮箱校验
    validated_data['email'] = validate_email(email)
    
    # 身份证号校验
    validated_data['id_card'] = validate_id_card(id_card)
    
    return validated_data


class StaffCreate(BaseModel):
    """工作人员创建请求模型"""
    staff_no: str
    name: str
    gender: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None


class StaffUpdate(BaseModel):
    """工作人员更新请求模型"""
    name: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


@router.get("/list")
def get_staff_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取工作人员列表
    支持分页、关键字搜索、部门筛选、状态筛选
    """
    query = db.query(Staff)
    
    # 关键字搜索（工号、姓名、电话）
    if keyword:
        query = query.filter(
            or_(
                Staff.staff_no.contains(keyword),
                Staff.name.contains(keyword),
                Staff.phone.contains(keyword)
            )
        )
    
    # 部门筛选
    if department:
        query = query.filter(Staff.department == department)
    
    # 状态筛选
    if status is not None:
        query = query.filter(Staff.status == status)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    staff_list = query.order_by(Staff.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": [staff.to_dict() for staff in staff_list],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/{staff_id}")
def get_staff_detail(staff_id: int, db: Session = Depends(get_db)):
    """
    获取工作人员详情
    """
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="工作人员不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": staff.to_dict()
    }


@router.post("/create")
def create_staff(
    staff_no: str = Form(...),
    name: str = Form(...),
    gender: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    id_card: Optional[str] = Form(None),
    status: int = Form(1),
    remark: Optional[str] = Form(None),
    face_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    创建工作人员
    支持上传人脸照片
    """
    # 数据校验
    validated = validate_staff_data(
        staff_no=staff_no,
        name=name,
        phone=phone,
        email=email,
        id_card=id_card,
        is_create=True
    )
    
    # 检查工号是否已存在
    existing = db.query(Staff).filter(Staff.staff_no == validated['staff_no']).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")
    
    # 处理人脸照片
    face_photo_path = None
    if face_photo:
        # 检查文件类型
        if face_photo.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="不支持的图片类型")
        
        # 生成唯一文件名
        file_ext = os.path.splitext(face_photo.filename)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(FACE_PHOTO_DIR, file_name)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(face_photo.file.read())
        
        face_photo_path = file_name
    
    # 创建工作人员（使用校验后的数据）
    staff = Staff(
        staff_no=validated['staff_no'],
        name=validated['name'],
        gender=gender.strip() if gender and gender.strip() else None,
        department=department.strip() if department and department.strip() else None,
        position=position.strip() if position and position.strip() else None,
        phone=validated['phone'],
        email=validated['email'],
        id_card=validated['id_card'],
        status=status,
        remark=remark.strip() if remark and remark.strip() else None,
        face_photo_path=face_photo_path
    )
    
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": staff.to_dict()
    }


@router.put("/{staff_id}")
def update_staff(
    staff_id: int,
    name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    id_card: Optional[str] = Form(None),
    status: Optional[int] = Form(None),
    remark: Optional[str] = Form(None),
    face_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    更新工作人员信息
    支持更新人脸照片
    """
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="工作人员不存在")
    
    # 数据校验
    if phone is not None:
        phone = validate_phone(phone)
    if email is not None:
        email = validate_email(email)
    if id_card is not None:
        id_card = validate_id_card(id_card)
    
    # 姓名长度校验
    if name is not None:
        name = name.strip()
        if name and len(name) > 100:
            raise HTTPException(status_code=400, detail="姓名不能超过100个字符")
    
    # 更新基本信息
    if name is not None and name:
        staff.name = name
    if gender is not None and gender.strip():
        staff.gender = gender.strip()
    if department is not None:
        staff.department = department.strip() if department.strip() else None
    if position is not None:
        staff.position = position.strip() if position.strip() else None
    if phone is not None:
        staff.phone = phone
    if email is not None:
        staff.email = email
    if id_card is not None:
        staff.id_card = id_card
    if status is not None:
        staff.status = status
    if remark is not None:
        staff.remark = remark.strip() if remark.strip() else None
    
    # 处理人脸照片
    if face_photo:
        # 检查文件类型
        if face_photo.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="不支持的图片类型")
        
        # 删除旧照片
        if staff.face_photo_path:
            old_path = os.path.join(FACE_PHOTO_DIR, staff.face_photo_path)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(face_photo.filename)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(FACE_PHOTO_DIR, file_name)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(face_photo.file.read())
        
        staff.face_photo_path = file_name
    
    db.commit()
    db.refresh(staff)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": staff.to_dict()
    }


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    """
    删除工作人员
    """
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="工作人员不存在")
    
    # 删除人脸照片
    if staff.face_photo_path:
        photo_path = os.path.join(FACE_PHOTO_DIR, staff.face_photo_path)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.delete(staff)
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.get("/photo/{file_name}")
def get_face_photo(file_name: str):
    """
    获取人脸照片
    """
    file_path = os.path.join(FACE_PHOTO_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="照片不存在")
    
    return FileResponse(file_path)


@router.get("/departments/all")
def get_all_departments(db: Session = Depends(get_db)):
    """
    获取所有部门列表
    """
    departments = db.query(Staff.department).filter(
        Staff.department.isnot(None),
        Staff.department != ""
    ).distinct().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [d[0] for d in departments]
    }
