"""
课程管理路由模块
处理课程信息的增删改查、分类筛选等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import User, UserRole, Course, CourseCategory, CourseType
from schemas import (
    CourseCreate, CourseUpdate, CourseResponse, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取课程列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[CourseCategory] = Query(None, description="课程分类筛选"),
    course_type: Optional[CourseType] = Query(None, description="课程类型筛选"),
    difficulty_level: Optional[int] = Query(None, ge=1, le=5, description="难度等级筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取课程列表
    
    支持分页、分类筛选、类型筛选、难度筛选、关键词搜索
    所有用户都可以查看课程列表
    
    Args:
        page: 页码
        page_size: 每页数量
        category: 课程分类筛选
        course_type: 课程类型筛选
        difficulty_level: 难度等级筛选
        keyword: 搜索关键词
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的课程列表
    """
    # 构建查询
    query = db.query(Course).filter(Course.is_active == True)
    
    # 分类筛选
    if category:
        query = query.filter(Course.category == category)
    
    # 类型筛选
    if course_type:
        query = query.filter(Course.course_type == course_type)
    
    # 难度筛选
    if difficulty_level:
        query = query.filter(Course.difficulty_level == difficulty_level)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Course.name.contains(keyword)) |
            (Course.description.contains(keyword))
        )
    
    # 按难度等级、创建时间排序
    query = query.order_by(Course.difficulty_level.asc(), Course.created_at.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    courses_response = [CourseResponse.model_validate(course) for course in paginated.items]
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"courses": [c.model_dump() for c in courses_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取课程详情
# ========================================

@router.get("/{course_id}", response_model=ResponseModel)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    获取课程详情
    
    所有用户都可以查看课程详情
    
    Args:
        course_id: 课程ID
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含课程信息的响应
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在或已下架"
        )
    
    course_response = CourseResponse.model_validate(course)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"course": course_response.model_dump()}
    )

# ========================================
# 创建课程（管理员/工作人员权限）
# ========================================

@router.post("", response_model=ResponseModel)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    创建新课程
    
    需要管理员或工作人员权限
    
    Args:
        course_data: 课程数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新课程信息的响应
    """
    # 检查课程名称是否已存在
    existing_course = db.query(Course).filter(Course.name == course_data.name).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="课程名称已存在"
        )
    
    # 创建新课程
    new_course = Course(
        name=course_data.name,
        description=course_data.description,
        category=course_data.category,
        course_type=course_data.course_type,
        duration=course_data.duration,
        difficulty_level=course_data.difficulty_level,
        calories_burned=course_data.calories_burned,
        image_url=course_data.image_url,
        is_active=True
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    course_response = CourseResponse.model_validate(new_course)
    
    return ResponseModel(
        code=200,
        message="课程创建成功",
        data={"course": course_response.model_dump()}
    )

# ========================================
# 更新课程（管理员/工作人员权限）
# ========================================

@router.put("/{course_id}", response_model=ResponseModel)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    更新课程信息
    
    需要管理员或工作人员权限
    
    Args:
        course_id: 课程ID
        course_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后课程信息的响应
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 检查课程名称是否已被其他课程使用
    if course_data.name and course_data.name != course.name:
        existing_course = db.query(Course).filter(
            Course.name == course_data.name,
            Course.id != course_id
        ).first()
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="课程名称已存在"
            )
    
    # 更新课程信息
    update_data = course_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
    
    db.commit()
    db.refresh(course)
    
    course_response = CourseResponse.model_validate(course)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={"course": course_response.model_dump()}
    )

# ========================================
# 上架/下架课程（管理员/工作人员权限）
# ========================================

@router.put("/{course_id}/toggle-status", response_model=ResponseModel)
async def toggle_course_status(
    course_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    切换课程状态（上架/下架）
    
    需要管理员或工作人员权限
    
    Args:
        course_id: 课程ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 切换状态
    course.is_active = not course.is_active
    db.commit()
    db.refresh(course)
    
    status_text = "上架" if course.is_active else "下架"
    course_response = CourseResponse.model_validate(course)
    
    return ResponseModel(
        code=200,
        message=f"课程已{status_text}",
        data={"course": course_response.model_dump()}
    )

# ========================================
# 删除课程（管理员权限）
# ========================================

@router.delete("/{course_id}", response_model=ResponseModel)
async def delete_course(
    course_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    删除课程
    
    需要管理员权限
    注意：删除课程会级联删除相关的预约记录，请谨慎操作
    
    Args:
        course_id: 课程ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    db.delete(course)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="课程已删除",
        data=None
    )

# ========================================
# 获取课程分类列表
# ========================================

@router.get("/categories/list", response_model=ResponseModel)
async def get_course_categories():
    """
    获取所有课程分类
    
    Returns:
        ResponseModel: 包含课程分类列表的响应
    """
    categories = [
        {"value": category.value, "label": category.value}
        for category in CourseCategory
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"categories": categories}
    )

# ========================================
# 获取热门课程
# ========================================

@router.get("/list/popular", response_model=ResponseModel)
async def get_popular_courses(
    limit: int = Query(6, ge=1, le=20, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取热门课程列表
    
    用于首页推荐展示
    
    Args:
        limit: 返回数量
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含热门课程列表的响应
    """
    courses = db.query(Course).filter(
        Course.is_active == True
    ).order_by(
        Course.difficulty_level.asc()
    ).limit(limit).all()
    
    courses_response = [CourseResponse.model_validate(course).model_dump() for course in courses]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"courses": courses_response}
    )

# ========================================
# 获取新课程
# ========================================

@router.get("/list/new", response_model=ResponseModel)
async def get_new_courses(
    limit: int = Query(6, ge=1, le=20, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取新课程列表
    
    按创建时间倒序排列，返回最新的课程
    
    Args:
        limit: 返回数量
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新课程列表的响应
    """
    courses = db.query(Course).filter(
        Course.is_active == True
    ).order_by(
        Course.created_at.desc()
    ).limit(limit).all()
    
    courses_response = [CourseResponse.model_validate(course).model_dump() for course in courses]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"courses": courses_response}
    )
