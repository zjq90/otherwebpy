"""
用户认证路由模块
处理用户注册、登录、登出等认证相关操作
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from utils.database import execute_query, execute_insert, execute_update
from utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token
)
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ROLE_ADMIN,
    ROLE_USER,
    TEMPLATES_DIR
)


# 创建路由
router = APIRouter(tags=["认证"])

# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# OAuth2密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserCreate(BaseModel):
    """
    用户注册数据模型
    """
    username: str
    email: EmailStr
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    """
    用户登录数据模型
    """
    username: str
    password: str


def get_current_user(request: Request) -> Optional[dict]:
    """
    从Cookie中获取当前登录用户信息
    
    参数:
        request: FastAPI请求对象
    
    返回:
        用户信息字典，如果未登录则返回None
    """
    # 从Cookie中获取token
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # 验证token
    token = token.replace("Bearer ", "")
    user_info = verify_token(token)
    if user_info is None:
        return None
    
    # 从数据库获取完整用户信息
    users = execute_query(
        "SELECT id, username, email, role, created_at FROM users WHERE id = ?",
        (user_info["user_id"],),
        fetchone=True
    )
    
    if not users:
        return None
    
    return users[0]


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    可选的用户认证依赖（用于不需要登录但可以显示用户信息的页面）
    
    参数:
        request: FastAPI请求对象
    
    返回:
        用户信息字典或None
    """
    return get_current_user(request)


async def get_current_user_required(request: Request) -> dict:
    """
    必需的用户认证依赖（用于需要登录才能访问的页面）
    
    参数:
        request: FastAPI请求对象
    
    返回:
        用户信息字典
    
    异常:
        HTTPException: 如果用户未登录
    """
    user = get_current_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/auth/login"}
        )
    return user


async def get_current_admin(request: Request) -> dict:
    """
    必需的管理员认证依赖（用于只有管理员才能访问的页面）
    
    参数:
        request: FastAPI请求对象
    
    返回:
        用户信息字典（必须是管理员）
    
    异常:
        HTTPException: 如果用户未登录或不是管理员
    """
    user = get_current_user_required(request)
    if user["role"] != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return user


@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    显示用户注册页面
    """
    # 如果已登录，重定向到首页
    current_user = get_current_user(request)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "current_user": None}
    )


@router.post("/auth/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """
    处理用户注册请求
    """
    # 验证两次密码是否一致
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "两次输入的密码不一致"
            }
        )
    
    # 检查用户名是否已存在
    existing_users = execute_query(
        "SELECT id FROM users WHERE username = ?",
        (username,),
        fetchone=True
    )
    if existing_users:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "用户名已存在"
            }
        )
    
    # 检查邮箱是否已存在
    existing_emails = execute_query(
        "SELECT id FROM users WHERE email = ?",
        (email,),
        fetchone=True
    )
    if existing_emails:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "邮箱已被注册"
            }
        )
    
    # 加密密码
    hashed_password = get_password_hash(password)
    
    # 创建新用户（默认角色为普通用户）
    user_id = execute_insert(
        """
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (username, email, hashed_password, ROLE_USER)
    )
    
    if user_id:
        # 注册成功，重定向到登录页面
        return RedirectResponse(
            url="/auth/login?registered=true",
            status_code=302
        )
    else:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "注册失败，请稍后重试"
            }
        )


@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    显示用户登录页面
    """
    # 如果已登录，重定向到首页
    current_user = get_current_user(request)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    
    # 检查是否是刚注册的用户
    registered = request.query_params.get("registered", False)
    
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "current_user": None,
            "registered": registered
        }
    )


@router.post("/auth/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    处理用户登录请求
    """
    # 根据用户名查询用户
    users = execute_query(
        "SELECT id, username, password, role FROM users WHERE username = ?",
        (username,),
        fetchone=True
    )
    
    if not users:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "current_user": None,
                "error": "用户名或密码错误"
            }
        )
    
    user = users[0]
    
    # 验证密码
    if not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "current_user": None,
                "error": "用户名或密码错误"
            }
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    # 设置Cookie并重定向到首页
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return response


@router.get("/auth/logout")
async def logout(request: Request):
    """
    处理用户登出请求
    """
    # 清除Cookie并重定向到登录页面
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    
    return response


@router.get("/auth/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示用户个人资料页面
    """
    # 查询用户的借还记录
    borrow_records = execute_query(
        """
        SELECT br.*, c.title as cd_title, c.artist as cd_artist
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        WHERE br.user_id = ?
        ORDER BY br.borrow_date DESC
        LIMIT 20
        """,
        (current_user["id"],)
    )
    
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "borrow_records": borrow_records or []
        }
    )
