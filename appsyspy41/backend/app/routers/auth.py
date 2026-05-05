"""
用户认证路由
提供用户登录、注册、权限验证等功能
"""

import hashlib
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database.connection import db
from app.models.schemas import (
    UserCreate, UserUpdate, UserLogin, UserResponse,
    ApiResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


def hash_password(password: str) -> str:
    """
    密码哈希函数
    
    Args:
        password: 明文密码
        
    Returns:
        str: MD5哈希后的密码
    """
    return hashlib.md5(password.encode()).hexdigest()


@router.post("/login", response_model=ApiResponse)
async def login(user_login: UserLogin):
    """
    用户登录
    
    验证用户名和密码，返回用户信息
    """
    # 查询用户
    sql = """
    SELECT * FROM users 
    WHERE username = ? AND password = ?
    """
    hashed_password = hash_password(user_login.password)
    user = db.query_one(sql, (user_login.username, hashed_password))
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户状态
    if user['status'] != 'active':
        raise HTTPException(status_code=403, detail="用户已被禁用")
    
    # 返回用户信息（不包含密码）
    user_dict = dict(user)
    user_dict.pop('password', None)
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data={"user": user_dict}
    )


@router.post("/register", response_model=ApiResponse)
async def register(user_create: UserCreate):
    """
    用户注册
    
    注意：生产环境中应该有权限控制，只有管理员可以注册用户
    """
    # 检查用户名是否已存在
    check_sql = "SELECT id FROM users WHERE username = ?"
    existing = db.query_one(check_sql, (user_create.username,))
    
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 插入用户
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hashed_password = hash_password(user_create.password)
    
    sql = """
    INSERT INTO users (
        username, password, real_name, role, phone, email, status,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        user_create.username, hashed_password, user_create.real_name,
        user_create.role, user_create.phone, user_create.email,
        user_create.status, now, now
    )
    
    user_id = db.execute_insert(sql, params)
    
    return ApiResponse(
        code=200,
        message="用户注册成功",
        data={"id": user_id}
    )


@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    role: Optional[str] = Query(None, description="用户角色"),
    status: Optional[str] = Query(None, description="用户状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取用户列表（分页）
    
    支持按角色、状态和关键词筛选
    """
    conditions = ["1=1"]
    params = []
    
    if role:
        conditions.append("role = ?")
        params.append(role)
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    if keyword:
        conditions.append("(username LIKE ? OR real_name LIKE ? OR phone LIKE ?)")
        keyword_param = f"%{keyword}%"
        params.extend([keyword_param, keyword_param, keyword_param])
    
    where_clause = " AND ".join(conditions)
    sql = f"SELECT id, username, real_name, role, phone, email, status, created_at, updated_at FROM users WHERE {where_clause} ORDER BY id DESC"
    
    result = db.query_paginated(sql, tuple(params), page, page_size)
    
    return PaginatedResponse(
        code=200,
        message="success",
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages'],
        data={"items": result['items']}
    )


@router.get("/users/{user_id}", response_model=ApiResponse)
async def get_user(user_id: int):
    """
    获取单个用户详情
    """
    sql = "SELECT id, username, real_name, role, phone, email, status, created_at, updated_at FROM users WHERE id = ?"
    user = db.query_one(sql, (user_id,))
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return ApiResponse(
        code=200,
        message="success",
        data=user
    )


@router.put("/users/{user_id}", response_model=ApiResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    """
    更新用户信息
    """
    # 检查用户是否存在
    check_sql = "SELECT id FROM users WHERE id = ?"
    existing = db.query_one(check_sql, (user_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 构建更新字段
    update_fields = []
    params = []
    
    user_dict = user_update.dict(exclude_unset=True)
    for key, value in user_dict.items():
        update_fields.append(f"{key} = ?")
        params.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    # 添加更新时间
    update_fields.append("updated_at = ?")
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(user_id)
    
    sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    db.execute(sql, tuple(params))
    
    return ApiResponse(
        code=200,
        message="用户更新成功"
    )


@router.put("/users/{user_id}/password", response_model=ApiResponse)
async def update_password(user_id: int, old_password: str, new_password: str):
    """
    更新用户密码
    
    需要验证旧密码
    """
    # 检查用户是否存在
    check_sql = "SELECT id, password FROM users WHERE id = ?"
    user = db.query_one(check_sql, (user_id,))
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    old_hashed = hash_password(old_password)
    if user['password'] != old_hashed:
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 更新密码
    new_hashed = hash_password(new_password)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sql = "UPDATE users SET password = ?, updated_at = ? WHERE id = ?"
    db.execute(sql, (new_hashed, now, user_id))
    
    return ApiResponse(
        code=200,
        message="密码更新成功"
    )


@router.delete("/users/{user_id}", response_model=ApiResponse)
async def delete_user(user_id: int):
    """
    删除用户
    
    注意：有外键关联的用户无法直接删除
    """
    # 检查用户是否存在
    check_sql = "SELECT id FROM users WHERE id = ?"
    existing = db.query_one(check_sql, (user_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 删除用户
    try:
        sql = "DELETE FROM users WHERE id = ?"
        db.execute(sql, (user_id,))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")
    
    return ApiResponse(
        code=200,
        message="用户删除成功"
    )


@router.get("/roles", response_model=ApiResponse)
async def get_roles():
    """
    获取所有用户角色列表
    
    用于前端展示角色选项
    """
    roles = [
        {"code": "admin", "name": "系统管理员", "description": "拥有系统全部权限"},
        {"code": "operator", "name": "操作员", "description": "设备操作、提交报修、查看状态"},
        {"code": "repair", "name": "维修人员", "description": "处理报修、维护设备、记录维修"}
    ]
    
    return ApiResponse(
        code=200,
        message="success",
        data={"roles": roles}
    )
