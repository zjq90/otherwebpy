"""
CD分类管理路由模块
处理CD分类的增删改查操作
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from utils.database import execute_query, execute_insert, execute_update, execute_delete, get_pagination
from routers.auth import get_current_user_required, get_current_admin
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, TEMPLATES_DIR


# 创建路由
router = APIRouter(tags=["分类管理"])

# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/categories", response_class=HTMLResponse)
async def category_list(
    request: Request,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示CD分类列表页面（支持分页和搜索）
    """
    # 验证分页参数
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    
    # 构建查询条件
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE name LIKE ? OR description LIKE ?"
        params = [f"%{search}%", f"%{search}%"]
    
    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM categories {where_clause}"
    count_result = execute_query(count_sql, tuple(params), fetchone=True)
    total = count_result[0]["total"] if count_result else 0
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 查询分类列表（包含每个分类下的CD数量）
    list_sql = f"""
        SELECT c.*, 
               (SELECT COUNT(*) FROM cds WHERE category_id = c.id) as cd_count
        FROM categories c
        {where_clause}
        ORDER BY c.name ASC
        LIMIT ? OFFSET ?
    """
    list_params = params + [page_size, offset]
    categories = execute_query(list_sql, tuple(list_params)) or []
    
    # 生成分页信息
    pagination = get_pagination(total, page, page_size)
    
    return templates.TemplateResponse(
        "categories/list.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "pagination": pagination,
            "search": search or ""
        }
    )


@router.get("/categories/create", response_class=HTMLResponse)
async def create_category_page(
    request: Request,
    current_user: dict = Depends(get_current_admin)
):
    """
    显示创建分类页面（仅管理员可访问）
    """
    return templates.TemplateResponse(
        "categories/form.html",
        {
            "request": request,
            "current_user": current_user,
            "category": None,
            "action": "create"
        }
    )


@router.post("/categories/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    current_user: dict = Depends(get_current_admin)
):
    """
    处理创建分类请求
    """
    # 验证分类名称是否已存在
    existing = execute_query(
        "SELECT id FROM categories WHERE name = ?",
        (name,),
        fetchone=True
    )
    
    if existing:
        return templates.TemplateResponse(
            "categories/form.html",
            {
                "request": request,
                "current_user": current_user,
                "category": {"name": name, "description": description},
                "action": "create",
                "error": "分类名称已存在"
            }
        )
    
    # 插入新分类
    category_id = execute_insert(
        """
        INSERT INTO categories (name, description)
        VALUES (?, ?)
        """,
        (name, description)
    )
    
    if category_id:
        # 创建成功，重定向到分类列表
        return RedirectResponse(url="/categories", status_code=302)
    else:
        return templates.TemplateResponse(
            "categories/form.html",
            {
                "request": request,
                "current_user": current_user,
                "category": {"name": name, "description": description},
                "action": "create",
                "error": "创建失败，请稍后重试"
            }
        )


@router.get("/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_page(
    request: Request,
    category_id: int,
    current_user: dict = Depends(get_current_admin)
):
    """
    显示编辑分类页面（仅管理员可访问）
    """
    # 查询分类信息
    categories = execute_query(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,),
        fetchone=True
    )
    
    if not categories:
        return RedirectResponse(url="/categories", status_code=302)
    
    return templates.TemplateResponse(
        "categories/form.html",
        {
            "request": request,
            "current_user": current_user,
            "category": categories[0],
            "action": "edit"
        }
    )


@router.post("/categories/{category_id}/edit")
async def edit_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    description: str = Form(default=""),
    current_user: dict = Depends(get_current_admin)
):
    """
    处理编辑分类请求
    """
    # 验证分类是否存在
    existing_category = execute_query(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,),
        fetchone=True
    )
    
    if not existing_category:
        return RedirectResponse(url="/categories", status_code=302)
    
    # 验证分类名称是否已被其他分类使用
    existing = execute_query(
        "SELECT id FROM categories WHERE name = ? AND id != ?",
        (name, category_id),
        fetchone=True
    )
    
    if existing:
        return templates.TemplateResponse(
            "categories/form.html",
            {
                "request": request,
                "current_user": current_user,
                "category": {"id": category_id, "name": name, "description": description},
                "action": "edit",
                "error": "分类名称已存在"
            }
        )
    
    # 更新分类信息
    rows_affected = execute_update(
        """
        UPDATE categories 
        SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (name, description, category_id)
    )
    
    if rows_affected > 0:
        # 更新成功，重定向到分类列表
        return RedirectResponse(url="/categories", status_code=302)
    else:
        return templates.TemplateResponse(
            "categories/form.html",
            {
                "request": request,
                "current_user": current_user,
                "category": {"id": category_id, "name": name, "description": description},
                "action": "edit",
                "error": "更新失败，请稍后重试"
            }
        )


@router.post("/categories/{category_id}/delete")
async def delete_category(
    request: Request,
    category_id: int,
    current_user: dict = Depends(get_current_admin)
):
    """
    处理删除分类请求（仅管理员可访问）
    """
    # 检查分类下是否有CD
    cd_count = execute_query(
        "SELECT COUNT(*) as count FROM cds WHERE category_id = ?",
        (category_id,),
        fetchone=True
    )
    
    if cd_count and cd_count[0]["count"] > 0:
        # 分类下有CD，不允许删除
        # 这里返回错误信息，实际项目中可以通过闪存消息或页面显示
        return RedirectResponse(
            url="/categories?error=分类下有CD，无法删除",
            status_code=302
        )
    
    # 删除分类
    rows_affected = execute_delete(
        "DELETE FROM categories WHERE id = ?",
        (category_id,)
    )
    
    if rows_affected > 0:
        return RedirectResponse(url="/categories", status_code=302)
    else:
        return RedirectResponse(
            url="/categories?error=删除失败，请稍后重试",
            status_code=302
        )


@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_detail(
    request: Request,
    category_id: int,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示分类详情页面（包含该分类下的CD列表）
    """
    # 查询分类信息
    categories = execute_query(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,),
        fetchone=True
    )
    
    if not categories:
        return RedirectResponse(url="/categories", status_code=302)
    
    category = categories[0]
    
    # 验证分页参数
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    
    # 查询该分类下的CD总数
    count_sql = "SELECT COUNT(*) as total FROM cds WHERE category_id = ?"
    count_result = execute_query(count_sql, (category_id,), fetchone=True)
    total = count_result[0]["total"] if count_result else 0
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 查询该分类下的CD列表
    list_sql = """
        SELECT c.*, cat.name as category_name
        FROM cds c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.category_id = ?
        ORDER BY c.title ASC
        LIMIT ? OFFSET ?
    """
    cds = execute_query(list_sql, (category_id, page_size, offset)) or []
    
    # 生成分页信息
    pagination = get_pagination(total, page, page_size)
    
    return templates.TemplateResponse(
        "categories/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "category": category,
            "cds": cds,
            "pagination": pagination
        }
    )
