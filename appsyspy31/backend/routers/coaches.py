"""
教练管理路由模块
处理教练信息的增删改查、评分统计等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import User, UserRole, Coach, Review
from schemas import (
    CoachCreate, CoachUpdate, CoachResponse, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取教练列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_coaches(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    specialization: Optional[str] = Query(None, description="专长领域筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名、专长）"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="最低评分筛选"),
    is_available: Optional[bool] = Query(None, description="是否可预约筛选"),
    db: Session = Depends(get_db)
):
    """
    获取教练列表
    
    支持分页、专长筛选、关键词搜索、评分筛选
    所有用户都可以查看教练列表
    
    Args:
        page: 页码
        page_size: 每页数量
        specialization: 专长领域筛选
        keyword: 搜索关键词
        min_rating: 最低评分筛选
        is_available: 是否可预约筛选
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的教练列表
    """
    # 构建查询（关联用户表获取基本信息）
    query = db.query(Coach).join(User)
    
    # 专长筛选
    if specialization:
        query = query.filter(Coach.specialization.contains(specialization))
    
    # 关键词搜索（搜索教练姓名、专长）
    if keyword:
        query = query.filter(
            (User.real_name.contains(keyword)) |
            (Coach.specialization.contains(keyword)) |
            (Coach.bio.contains(keyword))
        )
    
    # 最低评分筛选
    if min_rating is not None:
        query = query.filter(Coach.rating >= min_rating)
    
    # 可预约筛选
    if is_available is not None:
        query = query.filter(Coach.is_available == is_available)
    
    # 按评分倒序、从业年限倒序排列
    query = query.order_by(Coach.rating.desc(), Coach.experience_years.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型（包含用户信息）
    coaches_response = []
    for coach in paginated.items:
        coach_response = CoachResponse.model_validate(coach)
        if coach.user:
            coach_response.user = coach_response.user.model_validate(coach.user)
        coaches_response.append(coach_response)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"coaches": [c.model_dump() for c in coaches_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取教练详情
# ========================================

@router.get("/{coach_id}", response_model=ResponseModel)
async def get_coach(
    coach_id: int,
    db: Session = Depends(get_db)
):
    """
    获取教练详情
    
    所有用户都可以查看教练详情
    包含教练的基本信息、评分统计等
    
    Args:
        coach_id: 教练ID
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含教练信息的响应
    """
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    coach_response = CoachResponse.model_validate(coach)
    if coach.user:
        coach_response.user = coach_response.user.model_validate(coach.user)
    
    # 获取教练的评价统计
    review_count = db.query(Review).filter(Review.coach_id == coach_id).count()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "coach": coach_response.model_dump(),
            "review_count": review_count
        }
    )

# ========================================
# 创建教练资料（管理员权限）
# ========================================

@router.post("", response_model=ResponseModel)
async def create_coach(
    coach_data: CoachCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    创建教练资料
    
    需要管理员或工作人员权限
    将现有用户设置为教练角色
    
    Args:
        coach_data: 教练数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新教练信息的响应
    """
    # 检查用户是否存在
    user = db.query(User).filter(User.id == coach_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否已经是教练
    existing_coach = db.query(Coach).filter(Coach.user_id == coach_data.user_id).first()
    
    if existing_coach:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已经是教练"
        )
    
    # 更新用户角色为教练
    user.role = UserRole.COACH
    
    # 创建教练资料
    new_coach = Coach(
        user_id=coach_data.user_id,
        specialization=coach_data.specialization,
        experience_years=coach_data.experience_years,
        certifications=coach_data.certifications,
        bio=coach_data.bio,
        hourly_rate=coach_data.hourly_rate,
        is_available=coach_data.is_available
    )
    
    db.add(new_coach)
    db.commit()
    db.refresh(new_coach)
    
    coach_response = CoachResponse.model_validate(new_coach)
    
    return ResponseModel(
        code=200,
        message="教练资料创建成功",
        data={"coach": coach_response.model_dump()}
    )

# ========================================
# 更新教练资料
# ========================================

@router.put("/{coach_id}", response_model=ResponseModel)
async def update_coach(
    coach_id: int,
    coach_data: CoachUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新教练资料
    
    教练可以更新自己的资料
    管理员和工作人员可以更新所有教练的资料
    
    Args:
        coach_id: 教练ID
        coach_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后教练信息的响应
    """
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # 权限检查：教练只能更新自己的资料，管理员/工作人员可以更新所有
    if (current_user.id != coach.user_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.STAFF]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该教练资料"
        )
    
    # 更新教练资料
    update_data = coach_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(coach, key, value)
    
    db.commit()
    db.refresh(coach)
    
    coach_response = CoachResponse.model_validate(coach)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={"coach": coach_response.model_dump()}
    )

# ========================================
# 删除教练资料（管理员权限）
# ========================================

@router.delete("/{coach_id}", response_model=ResponseModel)
async def delete_coach(
    coach_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    删除教练资料
    
    需要管理员权限
    同时将用户角色改回会员
    
    Args:
        coach_id: 教练ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # 获取关联的用户并更新角色
    user = db.query(User).filter(User.id == coach.user_id).first()
    if user:
        user.role = UserRole.MEMBER
    
    # 删除教练资料
    db.delete(coach)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="教练资料已删除",
        data=None
    )

# ========================================
# 获取教练的评价列表
# ========================================

@router.get("/{coach_id}/reviews", response_model=PaginatedResponse)
async def get_coach_reviews(
    coach_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="最低评分筛选"),
    db: Session = Depends(get_db)
):
    """
    获取教练的评价列表
    
    所有用户都可以查看教练的评价
    
    Args:
        coach_id: 教练ID
        page: 页码
        page_size: 每页数量
        min_rating: 最低评分筛选
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的评价列表
    """
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # 构建查询
    query = db.query(Review).filter(Review.coach_id == coach_id, Review.is_visible == True)
    
    # 最低评分筛选
    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)
    
    # 按创建时间倒序排列
    query = query.order_by(Review.created_at.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    from schemas import ReviewResponse
    reviews_response = [ReviewResponse.model_validate(review) for review in paginated.items]
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"reviews": [r.model_dump() for r in reviews_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取热门教练（评分最高的前N个）
# ========================================

@router.get("/list/popular", response_model=ResponseModel)
async def get_popular_coaches(
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取热门教练列表
    
    按评分排序，返回评分最高的教练
    用于首页推荐展示
    
    Args:
        limit: 返回数量
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含热门教练列表的响应
    """
    coaches = db.query(Coach).filter(
        Coach.is_available == True
    ).order_by(
        Coach.rating.desc(),
        Coach.review_count.desc()
    ).limit(limit).all()
    
    coaches_response = []
    for coach in coaches:
        coach_response = CoachResponse.model_validate(coach)
        if coach.user:
            coach_response.user = coach_response.user.model_validate(coach.user)
        coaches_response.append(coach_response.model_dump())
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"coaches": coaches_response}
    )
