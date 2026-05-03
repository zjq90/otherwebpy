"""
页面路由模块
提供前端页面的渲染接口
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Product, Service, Case, Document, User, KeyApplication
from routers.auth import get_current_user, get_current_active_user, get_current_admin_user
from config import TEMPLATES_DIR

router = APIRouter()

# 初始化模板引擎
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_user_info(request: Request, db: Session = Depends(get_db)):
    """
    从请求中获取当前用户信息
    用于页面渲染时传递用户信息
    """
    user_info = None
    try:
        # 尝试从Authorization头获取令牌
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            from security import decode_access_token
            payload = decode_access_token(token)
            if payload:
                username = payload.get("sub")
                if username:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        user_info = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "full_name": user.full_name,
                            "is_admin": user.is_admin
                        }
    except Exception:
        pass
    return user_info


@router.get("/home")
def home_page(request: Request, db: Session = Depends(get_db)):
    """
    首页
    展示网站概览、精选产品、推荐案例等
    """
    # 获取用户信息
    user_info = get_user_info(request, db)
    
    # 获取部分产品
    products = db.query(Product).filter(
        Product.is_active == True
    ).order_by(Product.sort_order.desc()).limit(6).all()
    
    # 获取部分服务
    services = db.query(Service).filter(
        Service.is_active == True
    ).order_by(Service.sort_order.desc()).limit(4).all()
    
    # 获取推荐案例
    featured_cases = db.query(Case).filter(
        Case.is_active == True,
        Case.is_featured == True
    ).order_by(Case.sort_order.desc()).limit(3).all()
    
    # 获取最新文档
    latest_docs = db.query(Document).filter(
        Document.is_active == True
    ).order_by(Document.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user_info,
            "products": products,
            "services": services,
            "featured_cases": featured_cases,
            "latest_docs": latest_docs
        }
    )


@router.get("/products")
def products_page(request: Request, db: Session = Depends(get_db)):
    """
    产品展示页
    展示所有产品列表
    """
    user_info = get_user_info(request, db)
    
    # 获取所有产品分类
    categories = db.query(Product.category).filter(
        Product.is_active == True,
        Product.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # 获取产品列表
    products = db.query(Product).filter(
        Product.is_active == True
    ).order_by(Product.sort_order.desc()).all()
    
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "user": user_info,
            "categories": categories,
            "products": products
        }
    )


@router.get("/products/{product_id}")
def product_detail_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    产品详情页
    展示单个产品的详细信息
    """
    user_info = get_user_info(request, db)
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    return templates.TemplateResponse(
        "product_detail.html",
        {
            "request": request,
            "user": user_info,
            "product": product
        }
    )


@router.get("/services")
def services_page(request: Request, db: Session = Depends(get_db)):
    """
    服务介绍页
    展示所有服务列表
    """
    user_info = get_user_info(request, db)
    
    services = db.query(Service).filter(
        Service.is_active == True
    ).order_by(Service.sort_order.desc()).all()
    
    return templates.TemplateResponse(
        "services.html",
        {
            "request": request,
            "user": user_info,
            "services": services
        }
    )


@router.get("/cases")
def cases_page(request: Request, db: Session = Depends(get_db)):
    """
    案例展示页
    展示所有案例列表
    """
    user_info = get_user_info(request, db)
    
    # 获取所有案例分类
    categories = db.query(Case.category).filter(
        Case.is_active == True,
        Case.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # 获取案例列表
    cases = db.query(Case).filter(
        Case.is_active == True
    ).order_by(Case.sort_order.desc()).all()
    
    return templates.TemplateResponse(
        "cases.html",
        {
            "request": request,
            "user": user_info,
            "categories": categories,
            "cases": cases
        }
    )


@router.get("/cases/{case_id}")
def case_detail_page(
    request: Request,
    case_id: int,
    db: Session = Depends(get_db)
):
    """
    案例详情页
    展示单个案例的详细信息
    """
    user_info = get_user_info(request, db)
    
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_active == True
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    return templates.TemplateResponse(
        "case_detail.html",
        {
            "request": request,
            "user": user_info,
            "case": case
        }
    )


@router.get("/documents")
def documents_page(request: Request, db: Session = Depends(get_db)):
    """
    文档中心页
    展示所有文档列表
    """
    user_info = get_user_info(request, db)
    
    # 获取所有文档分类
    categories = db.query(Document.category).filter(
        Document.is_active == True,
        Document.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # 获取文档列表
    documents = db.query(Document).filter(
        Document.is_active == True
    ).order_by(Document.sort_order.desc()).all()
    
    return templates.TemplateResponse(
        "documents.html",
        {
            "request": request,
            "user": user_info,
            "categories": categories,
            "documents": documents
        }
    )


@router.get("/documents/{doc_id}")
def document_detail_page(
    request: Request,
    doc_id: int,
    db: Session = Depends(get_db)
):
    """
    文档详情页
    展示单个文档的详细信息
    """
    user_info = get_user_info(request, db)
    
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 增加阅读次数
    document.view_count += 1
    db.commit()
    db.refresh(document)
    
    return templates.TemplateResponse(
        "document_detail.html",
        {
            "request": request,
            "user": user_info,
            "document": document
        }
    )


@router.get("/about")
def about_page(request: Request, db: Session = Depends(get_db)):
    """
    关于我们页
    展示公司介绍、团队信息等
    """
    user_info = get_user_info(request, db)
    
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": user_info
        }
    )


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    """
    登录页
    """
    user_info = get_user_info(request, db)
    
    # 如果已登录，跳转到首页
    if user_info:
        return templates.TemplateResponse(
            "redirect.html",
            {"request": request, "url": "/home"}
        )
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "user": None
        }
    )


@router.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    """
    注册页
    """
    user_info = get_user_info(request, db)
    
    # 如果已登录，跳转到首页
    if user_info:
        return templates.TemplateResponse(
            "redirect.html",
            {"request": request, "url": "/home"}
        )
    
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None
        }
    )


@router.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):
    """
    用户个人中心页
    需要登录才能访问
    """
    user_info = get_user_info(request, db)
    
    # 如果未登录，跳转到登录页
    if not user_info:
        return templates.TemplateResponse(
            "redirect.html",
            {"request": request, "url": "/login"}
        )
    
    # 获取用户的秘钥申请记录
    applications = db.query(KeyApplication).filter(
        KeyApplication.user_id == user_info["id"]
    ).order_by(KeyApplication.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user_info,
            "applications": applications
        }
    )


@router.get("/key-application")
def key_application_page(request: Request, db: Session = Depends(get_db)):
    """
    秘钥申请页
    需要登录才能访问
    """
    user_info = get_user_info(request, db)
    
    # 如果未登录，跳转到登录页
    if not user_info:
        return templates.TemplateResponse(
            "redirect.html",
            {"request": request, "url": "/login"}
        )
    
    # 检查是否有待审核的申请
    pending_app = db.query(KeyApplication).filter(
        KeyApplication.user_id == user_info["id"],
        KeyApplication.status == "pending"
    ).first()
    
    return templates.TemplateResponse(
        "key_application.html",
        {
            "request": request,
            "user": user_info,
            "has_pending": pending_app is not None
        }
    )


@router.get("/admin")
def admin_page(request: Request, db: Session = Depends(get_db)):
    """
    管理后台页
    需要管理员权限才能访问
    """
    user_info = get_user_info(request, db)
    
    # 如果未登录或不是管理员，跳转到首页
    if not user_info or not user_info.get("is_admin"):
        return templates.TemplateResponse(
            "redirect.html",
            {"request": request, "url": "/home"}
        )
    
    # 获取统计数据
    user_count = db.query(User).count()
    product_count = db.query(Product).filter(Product.is_active == True).count()
    case_count = db.query(Case).filter(Case.is_active == True).count()
    pending_app_count = db.query(KeyApplication).filter(KeyApplication.status == "pending").count()
    
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user_info,
            "stats": {
                "user_count": user_count,
                "product_count": product_count,
                "case_count": case_count,
                "pending_app_count": pending_app_count
            }
        }
    )
