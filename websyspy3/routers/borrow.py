"""
CD借还管理路由模块
处理CD的借阅、归还和借还记录查询操作
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from utils.database import execute_query, execute_transaction, get_pagination
from routers.auth import get_current_user_required, get_current_admin
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, TEMPLATES_DIR, STATUS_BORROWED, STATUS_RETURNED, ROLE_ADMIN


# 创建路由
router = APIRouter(tags=["借还管理"])

# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/borrow", response_class=HTMLResponse)
async def borrow_list(
    request: Request,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示借还记录列表页面（支持分页、状态筛选和搜索）
    """
    # 验证分页参数
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    
    # 构建查询条件
    where_clauses = []
    params = []
    
    # 普通用户只能看自己的记录
    if current_user["role"] != ROLE_ADMIN:
        where_clauses.append("br.user_id = ?")
        params.append(current_user["id"])
    
    # 状态筛选
    if status:
        where_clauses.append("br.status = ?")
        params.append(status)
    
    # 搜索条件
    if search:
        where_clauses.append("(c.title LIKE ? OR c.artist LIKE ? OR u.username LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # 查询总数
    count_sql = f"""
        SELECT COUNT(*) as total 
        FROM borrow_records br
        {where_clause}
    """
    count_result = execute_query(count_sql, tuple(params), fetchone=True)
    total = count_result[0]["total"] if count_result else 0
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 查询借还记录列表
    list_sql = f"""
        SELECT br.*, 
               c.title as cd_title, 
               c.artist as cd_artist,
               u.username as user_name
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        JOIN users u ON br.user_id = u.id
        {where_clause}
        ORDER BY br.borrow_date DESC
        LIMIT ? OFFSET ?
    """
    list_params = params + [page_size, offset]
    records = execute_query(list_sql, tuple(list_params)) or []
    
    # 生成分页信息
    pagination = get_pagination(total, page, page_size)
    
    return templates.TemplateResponse(
        "borrow/list.html",
        {
            "request": request,
            "current_user": current_user,
            "records": records,
            "pagination": pagination,
            "status": status,
            "search": search or "",
            "is_admin": current_user["role"] == ROLE_ADMIN
        }
    )


@router.post("/borrow/borrow/{cd_id}")
async def borrow_cd(
    request: Request,
    cd_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    """
    处理借阅CD请求
    """
    # 查询CD信息
    cds = execute_query(
        "SELECT * FROM cds WHERE id = ?",
        (cd_id,),
        fetchone=True
    )
    
    if not cds:
        return RedirectResponse(url="/cds", status_code=302)
    
    cd = cds[0]
    
    # 检查是否有库存
    if cd["available_quantity"] <= 0:
        return RedirectResponse(
            url=f"/cds/{cd_id}?error=该CD已被借完，无可用库存",
            status_code=302
        )
    
    # 检查用户是否已经借阅过该CD且未归还
    existing_borrow = execute_query(
        """
        SELECT id FROM borrow_records 
        WHERE user_id = ? AND cd_id = ? AND status = ?
        """,
        (current_user["id"], cd_id, STATUS_BORROWED),
        fetchone=True
    )
    
    if existing_borrow:
        return RedirectResponse(
            url=f"/cds/{cd_id}?error=您已借阅过该CD且未归还",
            status_code=302
        )
    
    # 使用事务处理借阅操作
    sqls = [
        # 1. 创建借还记录
        (
            """
            INSERT INTO borrow_records (user_id, cd_id, status)
            VALUES (?, ?, ?)
            """,
            (current_user["id"], cd_id, STATUS_BORROWED)
        ),
        # 2. 减少可用库存
        (
            """
            UPDATE cds 
            SET available_quantity = available_quantity - 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cd_id,)
        )
    ]
    
    success = execute_transaction(sqls)
    
    if success:
        return RedirectResponse(url="/borrow", status_code=302)
    else:
        return RedirectResponse(
            url=f"/cds/{cd_id}?error=借阅失败，请稍后重试",
            status_code=302
        )


@router.post("/borrow/return/{record_id}")
async def return_cd(
    request: Request,
    record_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    """
    处理归还CD请求
    """
    # 查询借还记录
    records = execute_query(
        """
        SELECT br.*, c.title as cd_title
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        WHERE br.id = ?
        """,
        (record_id,),
        fetchone=True
    )
    
    if not records:
        return RedirectResponse(url="/borrow", status_code=302)
    
    record = records[0]
    
    # 检查权限：管理员可以归还所有记录，普通用户只能归还自己的
    if current_user["role"] != ROLE_ADMIN and record["user_id"] != current_user["id"]:
        return RedirectResponse(
            url="/borrow?error=权限不足，无法归还该记录",
            status_code=302
        )
    
    # 检查是否已经归还
    if record["status"] == STATUS_RETURNED:
        return RedirectResponse(
            url="/borrow?error=该CD已经归还",
            status_code=302
        )
    
    # 使用事务处理归还操作
    sqls = [
        # 1. 更新借还记录状态
        (
            """
            UPDATE borrow_records 
            SET status = ?, return_date = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (STATUS_RETURNED, record_id)
        ),
        # 2. 增加可用库存
        (
            """
            UPDATE cds 
            SET available_quantity = available_quantity + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (record["cd_id"],)
        )
    ]
    
    success = execute_transaction(sqls)
    
    if success:
        return RedirectResponse(url="/borrow", status_code=302)
    else:
        return RedirectResponse(
            url="/borrow?error=归还失败，请稍后重试",
            status_code=302
        )


@router.get("/borrow/{record_id}", response_class=HTMLResponse)
async def borrow_detail(
    request: Request,
    record_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示借还记录详情页面
    """
    # 查询借还记录详情
    records = execute_query(
        """
        SELECT br.*, 
               c.title as cd_title, 
               c.artist as cd_artist,
               c.category_id,
               u.username as user_name,
               u.email as user_email,
               cat.name as category_name
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        JOIN users u ON br.user_id = u.id
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE br.id = ?
        """,
        (record_id,),
        fetchone=True
    )
    
    if not records:
        return RedirectResponse(url="/borrow", status_code=302)
    
    record = records[0]
    
    # 检查权限：管理员可以查看所有记录，普通用户只能查看自己的
    if current_user["role"] != ROLE_ADMIN and record["user_id"] != current_user["id"]:
        return RedirectResponse(
            url="/borrow?error=权限不足",
            status_code=302
        )
    
    return templates.TemplateResponse(
        "borrow/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "record": record,
            "is_admin": current_user["role"] == ROLE_ADMIN
        }
    )


@router.get("/borrow/my-borrows", response_class=HTMLResponse)
async def my_borrows(
    request: Request,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    current_user: dict = Depends(get_current_user_required)
):
    """
    显示当前用户的借还记录（快捷入口）
    """
    # 验证分页参数
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    
    # 查询总数
    count_sql = """
        SELECT COUNT(*) as total 
        FROM borrow_records 
        WHERE user_id = ?
    """
    count_result = execute_query(count_sql, (current_user["id"],), fetchone=True)
    total = count_result[0]["total"] if count_result else 0
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 查询借还记录列表
    list_sql = """
        SELECT br.*, 
               c.title as cd_title, 
               c.artist as cd_artist
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        WHERE br.user_id = ?
        ORDER BY br.borrow_date DESC
        LIMIT ? OFFSET ?
    """
    records = execute_query(list_sql, (current_user["id"], page_size, offset)) or []
    
    # 生成分页信息
    pagination = get_pagination(total, page, page_size)
    
    return templates.TemplateResponse(
        "borrow/my_borrows.html",
        {
            "request": request,
            "current_user": current_user,
            "records": records,
            "pagination": pagination
        }
    )
