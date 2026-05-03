from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import StaffCreate, StaffUpdate, StaffResponse, StaffRoleInfo
from ..crud import staff_crud
from ..models.role import Role
from ..permissions import parse_permissions

# 创建路由对象
router = APIRouter(
    prefix="/api/staff",
    tags=["人员管理"],
    responses={404: {"description": "未找到"}},
)


def staff_to_response(db_staff, db: Session) -> StaffResponse:
    """
    将数据库员工对象转换为响应对象
    包含角色信息和权限信息
    """
    # 构建基本数据
    staff_data = {
        "id": db_staff.id,
        "staff_number": db_staff.staff_number,
        "name": db_staff.name,
        "gender": db_staff.gender,
        "age": db_staff.age,
        "phone": db_staff.phone,
        "email": db_staff.email,
        "id_card": db_staff.id_card,
        "role_id": db_staff.role_id,
        "position": db_staff.position,
        "department": db_staff.department,
        "permissions": db_staff.permissions,
        "join_date": db_staff.join_date,
        "status": db_staff.status,
        "remarks": db_staff.remarks,
        "created_at": db_staff.created_at,
        "updated_at": db_staff.updated_at,
    }
    
    # 添加角色信息
    role_info = None
    if db_staff.role_id:
        role = db.query(Role).filter(Role.id == db_staff.role_id).first()
        if role:
            role_info = StaffRoleInfo(
                role_id=role.id,
                role_name=role.name,
                role_code=role.code,
                role_permissions=parse_permissions(role.permissions)
            )
    
    staff_data["role_info"] = role_info
    
    # 添加自定义权限列表
    staff_data["permission_list"] = parse_permissions(db_staff.permissions)
    
    # 添加实际生效权限
    effective_permissions = staff_crud.get_effective_permissions(db, db_staff.id)
    staff_data["effective_permissions"] = effective_permissions
    
    return StaffResponse(**staff_data)


@router.get("/", response_model=List[StaffResponse])
def read_staffs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取员工列表
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数（用于分页）
    """
    staffs = staff_crud.get_all(db, skip=skip, limit=limit)
    return [staff_to_response(staff, db) for staff in staffs]


@router.get("/count", response_model=int)
def count_staffs(db: Session = Depends(get_db)):
    """
    统计员工总数
    """
    return staff_crud.count(db)


@router.get("/position/{position}", response_model=List[StaffResponse])
def read_staffs_by_position(
    position: str, 
    db: Session = Depends(get_db)
):
    """
    根据岗位获取员工列表
    - **position**: 岗位名称
    """
    staffs = staff_crud.get_by_position(db, position=position)
    return [staff_to_response(staff, db) for staff in staffs]


@router.get("/role/{role_id}", response_model=List[StaffResponse])
def read_staffs_by_role(
    role_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据角色获取员工列表
    - **role_id**: 角色ID
    """
    staffs = staff_crud.get_by_role(db, role_id=role_id)
    return [staff_to_response(staff, db) for staff in staffs]


@router.get("/{staff_id}", response_model=StaffResponse)
def read_staff(
    staff_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个员工信息
    - **staff_id**: 员工ID
    """
    staff = staff_crud.get_by_id(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    return staff_to_response(staff, db)


@router.get("/{staff_id}/permissions", response_model=List[str])
def get_staff_permissions(
    staff_id: int, 
    db: Session = Depends(get_db)
):
    """
    获取员工实际生效的权限列表
    - **staff_id**: 员工ID
    """
    staff = staff_crud.get_by_id(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    return staff_crud.get_effective_permissions(db, staff_id)


@router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff: StaffCreate, 
    db: Session = Depends(get_db)
):
    """
    创建新员工
    - **staff**: 员工信息
    """
    # 检查员工工号是否已存在
    existing_staff = staff_crud.get_by_staff_number(db, staff_number=staff.staff_number)
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"员工工号 '{staff.staff_number}' 已存在"
        )
    
    # 验证角色ID（如果提供）
    if staff.role_id:
        role = db.query(Role).filter(Role.id == staff.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色ID {staff.role_id} 不存在"
            )
    
    new_staff = staff_crud.create(db=db, staff=staff)
    return staff_to_response(new_staff, db)


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int, 
    staff: StaffUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新员工信息
    - **staff_id**: 员工ID
    - **staff**: 更新的员工信息
    """
    db_staff = staff_crud.get_by_id(db, staff_id=staff_id)
    if db_staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    
    # 验证角色ID（如果提供）
    update_data = staff.model_dump(exclude_unset=True)
    if "role_id" in update_data and update_data["role_id"] is not None:
        role = db.query(Role).filter(Role.id == update_data["role_id"]).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色ID {update_data['role_id']} 不存在"
            )
    
    updated_staff = staff_crud.update(db=db, staff_id=staff_id, staff=staff)
    return staff_to_response(updated_staff, db)


@router.put("/{staff_id}/assign-role/{role_id}", response_model=StaffResponse)
def assign_role_to_staff(
    staff_id: int, 
    role_id: int, 
    db: Session = Depends(get_db)
):
    """
    为员工分配角色
    - **staff_id**: 员工ID
    - **role_id**: 角色ID
    """
    # 验证员工是否存在
    staff = staff_crud.get_by_id(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    
    # 验证角色是否存在
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色ID {role_id} 不存在"
        )
    
    updated_staff = staff_crud.assign_role(db, staff_id, role_id)
    return staff_to_response(updated_staff, db)


@router.put("/{staff_id}/remove-role", response_model=StaffResponse)
def remove_role_from_staff(
    staff_id: int, 
    db: Session = Depends(get_db)
):
    """
    移除员工的角色
    - **staff_id**: 员工ID
    """
    staff = staff_crud.get_by_id(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    
    updated_staff = staff_crud.remove_role(db, staff_id)
    return staff_to_response(updated_staff, db)


@router.delete("/{staff_id}", response_model=dict)
def delete_staff(
    staff_id: int, 
    db: Session = Depends(get_db)
):
    """
    删除员工
    - **staff_id**: 员工ID
    """
    success = staff_crud.delete(db=db, staff_id=staff_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"员工ID {staff_id} 不存在"
        )
    return {"message": "删除成功", "staff_id": staff_id}
