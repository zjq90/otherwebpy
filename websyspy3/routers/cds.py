"""
CD信息管理路由模块
处理CD信息的增删改查操作
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from utils.database import execute_query, execute_insert, execute_update, execute_delete, get_pagination
from routers.auth import get_current_user_required, get_current_admin
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, TEMPLATES_DIR, ROLE_ADMIN


# 创建路由
router = APIRouter(tags=["CD管理"])

# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_all_categories():
    """
    获取所有分类列表（用于表单下拉选择）
    """
    return execute_query(
        "SELECT id, name FROM categories ORDER BY name ASC"
    ) or []


@router.get("/cds", response_class=HTMLResponse)
async def cd_list(
    request: Request,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示CD列表页面（支持分页、搜索和分类筛选）
    """
    # 验证分页参数
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    
    # 构建查询条件
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("(c.title LIKE ? OR c.artist LIKE ? OR c.description LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    if category_id:
        where_clauses.append("c.category_id = ?")
        params.append(category_id)
    
    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM cds c {where_clause}"
    count_result = execute_query(count_sql, tuple(params), fetchone=True)
    total = count_result[0]["total"] if count_result else 0
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 查询CD列表（包含分类名称）
    list_sql = f"""
        SELECT c.*, cat.name as category_name
        FROM cds c
        LEFT JOIN categories cat ON c.category_id = cat.id
        {where_clause}
        ORDER BY c.created_at DESC
        LIMIT ? OFFSET ?
    """
    list_params = params + [page_size, offset]
    cds = execute_query(list_sql, tuple(list_params)) or []
    
    # 查询所有分类（用于筛选下拉框）
    categories = get_all_categories()
    
    # 生成分页信息
    pagination = get_pagination(total, page, page_size)
    
    return templates.TemplateResponse(
        "cds/list.html",
        {
            "request": request,
            "current_user": current_user,
            "cds": cds,
            "categories": categories,
            "pagination": pagination,
            "search": search or "",
            "selected_category": category_id,
            "is_admin": current_user["role"] == ROLE_ADMIN
        }
    )


@router.get("/cds/create", response_class=HTMLResponse)
async def create_cd_page(
    request: Request,
    current_user: dict = Depends(get_current_admin)
):
    """
    显示创建CD页面（仅管理员可访问）
    """
    categories = get_all_categories()
    
    return templates.TemplateResponse(
        "cds/form.html",
        {
            "request": request,
            "current_user": current_user,
            "cd": None,
            "categories": categories,
            "action": "create"
        }
    )


@router.post("/cds/create")
async def create_cd(
    request: Request,
    title: str = Form(...),
    artist: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(default=""),
    total_quantity: int = Form(default=1),
    current_user: dict = Depends(get_current_admin)
):
    """
    处理创建CD请求
    """
    # 验证分类是否存在
    category = execute_query(
        "SELECT id FROM categories WHERE id = ?",
        (category_id,),
        fetchone=True
    )
    
    if not category:
        categories = get_all_categories()
        return templates.TemplateResponse(
            "cds/form.html",
            {
                "request": request,
                "current_user": current_user,
                "cd": {
                    "title": title,
                    "artist": artist,
                    "category_id": category_id,
                    "description": description,
                    "total_quantity": total_quantity
                },
                "categories": categories,
                "action": "create",
                "error": "所选分类不存在"
            }
        )
    
    # 验证数量
    if total_quantity < 1:
        total_quantity = 1
    
    # 插入新CD
    cd_id = execute_insert(
        """
        INSERT INTO cds (title, artist, category_id, description, total_quantity, available_quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, artist, category_id, description, total_quantity, total_quantity)
    )
    
    if cd_id:
        # 创建成功，重定向到CD列表
        return RedirectResponse(url="/cds", status_code=302)
    else:
        categories = get_all_categories()
        return templates.TemplateResponse(
            "cds/form.html",
            {
                "request": request,
                "current_user": current_user,
                "cd": {
                    "title": title,
                    "artist": artist,
                    "category_id": category_id,
                    "description": description,
                    "total_quantity": total_quantity
                },
                "categories": categories,
                "action": "create",
                "error": "创建失败，请稍后重试"
            }
        )


@router.get("/cds/{cd_id}/edit", response_class=HTMLResponse)
async def edit_cd_page(
    request: Request,
    cd_id: int,
    current_user: dict = Depends(get_current_admin)
):
    """
    显示编辑CD页面（仅管理员可访问）
    """
    # 查询CD信息
    cds = execute_query(
        "SELECT * FROM cds WHERE id = ?",
        (cd_id,),
        fetchone=True
    )
    
    if not cds:
        return RedirectResponse(url="/cds", status_code=302)
    
    categories = get_all_categories()
    
    return templates.TemplateResponse(
        "cds/form.html",
        {
            "request": request,
            "current_user": current_user,
            "cd": cds[0],
            "categories": categories,
            "action": "edit"
        }
    )


@router.post("/cds/{cd_id}/edit")
async def edit_cd(
    request: Request,
    cd_id: int,
    title: str = Form(...),
    artist: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(default=""),
    total_quantity: int = Form(default=1),
    current_user: dict = Depends(get_current_admin)
):
    """
    处理编辑CD请求
    """
    # 验证CD是否存在
    existing_cd = execute_query(
        "SELECT * FROM cds WHERE id = ?",
        (cd_id,),
        fetchone=True
    )
    
    if not existing_cd:
        return RedirectResponse(url="/cds", status_code=302)
    
    # 验证分类是否存在
    category = execute_query(
        "SELECT id FROM categories WHERE id = ?",
        (category_id,),
        fetchone=True
    )
    
    if not category:
        categories = get_all_categories()
        return templates.TemplateResponse(
            "cds/form.html",
            {
                "request": request,
                "current_user": current_user,
                "cd": {
                    "id": cd_id,
                    "title": title,
                    "artist": artist,
                    "category_id": category_id,
                    "description": description,
                    "total_quantity": total_quantity
                },
                "categories": categories,
                "action": "edit",
                "error": "所选分类不存在"
            }
        )
    
    # 验证数量
    if total_quantity < 1:
        total_quantity = 1
    
    # 计算可用数量（不能小于已借出的数量）
    borrowed_count = execute_query(
        """
        SELECT COUNT(*) as count 
        FROM borrow_records 
        WHERE cd_id = ? AND status = 'borrowed'
        """,
        (cd_id,),
        fetchone=True
    )
    
    borrowed = borrowed_count[0]["count"] if borrowed_count else 0
    available_quantity = max(total_quantity - borrowed, 0)
    
    # 更新CD信息
    rows_affected = execute_update(
        """
        UPDATE cds 
        SET title = ?, artist = ?, category_id = ?, description = ?, 
            total_quantity = ?, available_quantity = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (title, artist, category_id, description, total_quantity, available_quantity, cd_id)
    )
    
    if rows_affected > 0:
        # 更新成功，重定向到CD列表
        return RedirectResponse(url="/cds", status_code=302)
    else:
        categories = get_all_categories()
        return templates.TemplateResponse(
            "cds/form.html",
            {
                "request": request,
                "current_user": current_user,
                "cd": {
                    "id": cd_id,
                    "title": title,
                    "artist": artist,
                    "category_id": category_id,
                    "description": description,
                    "total_quantity": total_quantity
                },
                "categories": categories,
                "action": "edit",
                "error": "更新失败，请稍后重试"
            }
        )


@router.post("/cds/{cd_id}/delete")
async def delete_cd(
    request: Request,
    cd_id: int,
    current_user: dict = Depends(get_current_admin)
):
    """
    处理删除CD请求（仅管理员可访问）
    """
    # 检查CD是否有未归还的借还记录
    borrowed_count = execute_query(
        """
        SELECT COUNT(*) as count 
        FROM borrow_records 
        WHERE cd_id = ? AND status = 'borrowed'
        """,
        (cd_id,),
        fetchone=True
    )
    
    if borrowed_count and borrowed_count[0]["count"] > 0:
        # 有未归还的CD，不允许删除
        return RedirectResponse(
            url="/cds?error=该CD有未归还的记录，无法删除",
            status_code=302
        )
    
    # 删除CD
    rows_affected = execute_delete(
        "DELETE FROM cds WHERE id = ?",
        (cd_id,)
    )
    
    if rows_affected > 0:
        return RedirectResponse(url="/cds", status_code=302)
    else:
        return RedirectResponse(
            url="/cds?error=删除失败，请稍后重试",
            status_code=302
        )


@router.get("/cds/{cd_id}", response_class=HTMLResponse)
async def cd_detail(
    request: Request,
    cd_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示CD详情页面
    """
    # 查询CD信息
    cds = execute_query(
        """
        SELECT c.*, cat.name as category_name
        FROM cds c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.id = ?
        """,
        (cd_id,),
        fetchone=True
    )
    
    if not cds:
        return RedirectResponse(url="/cds", status_code=302)
    
    cd = cds[0]
    
    # 查询该CD的借还记录
    borrow_records = execute_query(
        """
        SELECT br.*, u.username as user_name
        FROM borrow_records br
        JOIN users u ON br.user_id = u.id
        WHERE br.cd_id = ?
        ORDER BY br.borrow_date DESC
        LIMIT 20
        """,
        (cd_id,)
    )
    
    # 查询是否可以借阅
    can_borrow = cd["available_quantity"] > 0
    
    return templates.TemplateResponse(
        "cds/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "cd": cd,
            "borrow_records": borrow_records or [],
            "can_borrow": can_borrow,
            "is_admin": current_user["role"] == ROLE_ADMIN
        }
    )
