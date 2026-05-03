"""
角色管理API路由
提供角色的增删改查接口和权限分配功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas.role import RoleCreate, RoleUpdate, RoleResponse
from ..crud.role import role_crud
from ..permissions import (
    get_all_permissions, 
    get_permission_modules, 
    parse_permissions
)

router = APIRouter(
    prefix="/api/roles",
    tags=["角色管理"]
)


def role_to_response(db_role):
    """
    将数据库角色对象转换为响应对象
    解析权限列表为数组格式
    """
    role_data = {
        "id": db_role.id,
        "name": db_role.name,
        "code": db_role.code,
        "description": db_role.description,
        "permissions": db_role.permissions,
        "is_system": db_role.is_system,
        "is_default": db_role.is_default,
        "sort_order": db_role.sort_order,
        "created_at": db_role.created_at,
        "updated_at": db_role.updated_at,
        "permission_list": parse_permissions(db_role.permissions)
    }
    return RoleResponse(**role_data)


@router.get("/", response_model=List[RoleResponse], summary="获取角色列表")
def get_roles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取所有角色列表，支持分页
    """
    roles = role_crud.get_all(db, skip=skip, limit=limit)
    return [role_to_response(role) for role in roles]


@router.get("/count", response_model=int, summary="统计角色数量")
def count_roles(db: Session = Depends(get_db)):
    """
    统计系统中角色的总数
    """
    return role_crud.count(db)


@router.get("/default", response_model=RoleResponse, summary="获取默认角色")
def get_default_role(db: Session = Depends(get_db)):
    """
    获取系统默认角色
    """
    role = role_crud.get_default(db)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到默认角色"
        )
    return role_to_response(role)


@router.get("/permissions", response_model=dict, summary="获取所有权限定义")
def get_permissions_definition():
    """
    获取系统中定义的所有权限（包括模块信息）
    """
    return {
        "modules": get_permission_modules(),
        "all_permissions": get_all_permissions()
    }


@router.get("/{role_id}", response_model=RoleResponse, summary="获取角色详情")
def get_role(
    role_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID获取角色详情
    """
    role = role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"角色ID {role_id} 不存在"
        )
    return role_to_response(role)


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, summary="创建角色")
def create_role(
    role_data: RoleCreate, 
    db: Session = Depends(get_db)
):
    """
    创建新角色
    """
    # 检查角色代码是否已存在
    existing_role = role_crud.get_by_code(db, role_data.code)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色代码 {role_data.code} 已存在"
        )
    
    try:
        new_role = role_crud.create(db, role_data)
        return role_to_response(new_role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建角色失败: {str(e)}"
        )


@router.put("/{role_id}", response_model=RoleResponse, summary="更新角色")
def update_role(
    role_id: int, 
    role_data: RoleUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新角色信息
    """
    existing_role = role_crud.get_by_id(db, role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"角色ID {role_id} 不存在"
        )
    
    try:
        updated_role = role_crud.update(db, existing_role, role_data)
        return role_to_response(updated_role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色失败: {str(e)}"
        )


@router.delete("/{role_id}", summary="删除角色")
def delete_role(
    role_id: int, 
    db: Session = Depends(get_db)
):
    """
    删除角色
    注意：系统预设角色不可删除
    """
    existing_role = role_crud.get_by_id(db, role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"角色ID {role_id} 不存在"
        )
    
    if existing_role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统预设角色不可删除"
        )
    
    success = role_crud.delete(db, role_id)
    if success:
        return {"message": f"角色ID {role_id} 删除成功", "success": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.post("/init-defaults", response_model=List[RoleResponse], summary="初始化默认角色")
def init_default_roles(db: Session = Depends(get_db)):
    """
    初始化系统预设角色
    此接口会创建或更新预设的角色（超级管理员、农场经理等）
    """
    try:
        roles = role_crud.init_default_roles(db)
        return [role_to_response(role) for role in roles]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化默认角色失败: {str(e)}"
        )
