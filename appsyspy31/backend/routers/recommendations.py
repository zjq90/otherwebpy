"""
智能推荐路由模块
根据会员的课程偏好、训练频率与目标，推荐适合的新课程、教练或营养产品
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

from database import get_db
from models import (
    User, UserRole, Recommendation, RecommendationType, RecommendationReason,
    MemberPreference, Course, CourseCategory, CourseType,
    Coach, NutritionProduct, NutritionProductCategory,
    Booking, BookingStatus
)
from schemas import (
    RecommendationCreate, RecommendationResponse,
    ResponseModel, PaginatedResponse, CourseResponse,
    CoachResponse, NutritionProductResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 推荐算法核心函数
# ========================================

def calculate_recommendation_score(
    item: Any,
    item_type: str,
    user_preferences: Optional[MemberPreference],
    user_bookings: List[Booking],
    db: Session
) -> float:
    """
    计算推荐分数
    
    基于用户偏好、历史行为、热门程度等多维度计算推荐分数
    
    Args:
        item: 推荐项（课程/教练/产品）
        item_type: 类型 ('course', 'coach', 'product')
        user_preferences: 用户偏好设置
        user_bookings: 用户预约历史
        db: 数据库会话
        
    Returns:
        float: 推荐分数（0-100）
    """
    score = 50.0  # 基础分
    
    if user_preferences:
        if item_type == 'course':
            preferred_categories = user_preferences.preferred_categories.split(',') if user_preferences.preferred_categories else []
            if item.category.value in preferred_categories:
                score += 20
            
            preferred_types = user_preferences.preferred_course_types.split(',') if user_preferences.preferred_course_types else []
            if item.course_type.value in preferred_types:
                score += 15
            
            if item.difficulty_level <= user_preferences.preferred_difficulty + 1:
                score += 10
        
        elif item_type == 'coach':
            if user_preferences.preferred_coach_gender and item.user:
                if item.user.gender == user_preferences.preferred_coach_gender:
                    score += 20
            
            if item.rating >= 4.5:
                score += 15
            elif item.rating >= 4.0:
                score += 10
        
        elif item_type == 'product':
            goals = user_preferences.fitness_goals.split(',') if user_preferences.fitness_goals else []
            product_category = item.category.value
            
            if '增肌' in goals and product_category in ['protein', 'supplement']:
                score += 20
            if '减脂' in goals and product_category in ['meal_replacement', 'vitamin']:
                score += 20
    
    if item_type == 'course':
        past_course_ids = [b.course_id for b in user_bookings]
        if item.id not in past_course_ids:
            score += 10
        
        if item.is_active:
            score += 5
    
    elif item_type == 'coach':
        past_coach_ids = [b.coach_id for b in user_bookings if b.coach_id]
        if item.id in past_coach_ids:
            score += 15
        if item.is_available:
            score += 10
    
    elif item_type == 'product':
        if item.is_recommended:
            score += 15
        if item.is_active:
            score += 5
        if item.sales_count > 100:
            score += 10
        elif item.sales_count > 50:
            score += 5
    
    score += random.uniform(-5, 5)
    
    return max(0, min(100, score))

def generate_recommendations_for_user(
    user_id: int,
    recommendation_type: RecommendationType,
    db: Session,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    为用户生成推荐列表
    
    Args:
        user_id: 用户ID
        recommendation_type: 推荐类型
        db: 数据库会话
        limit: 返回数量
        
    Returns:
        List[Dict]: 推荐列表
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    user_preferences = db.query(MemberPreference).filter(
        MemberPreference.user_id == user_id
    ).first()
    
    user_bookings = db.query(Booking).filter(
        Booking.user_id == user_id
    ).all()
    
    recommendations = []
    
    if recommendation_type == RecommendationType.COURSE:
        courses = db.query(Course).filter(Course.is_active == True).all()
        
        scored_courses = []
        for course in courses:
            score = calculate_recommendation_score(
                course, 'course', user_preferences, user_bookings, db
            )
            scored_courses.append((course, score))
        
        scored_courses.sort(key=lambda x: x[1], reverse=True)
        
        for course, score in scored_courses[:limit]:
            reason = RecommendationReason.PERSONAL
            explanation = "根据您的健身偏好和训练目标为您推荐"
            
            if user_preferences and course.category.value in (user_preferences.preferred_categories or ''):
                reason = RecommendationReason.PREFERENCE
                explanation = "您可能喜欢这个类型的课程"
            elif score > 80:
                reason = RecommendationReason.POPULAR
                explanation = "这是一门热门课程"
            
            recommendations.append({
                'course': course,
                'score': score,
                'reason': reason,
                'explanation': explanation
            })
    
    elif recommendation_type == RecommendationType.COACH:
        coaches = db.query(Coach).filter(Coach.is_available == True).all()
        
        scored_coaches = []
        for coach in coaches:
            score = calculate_recommendation_score(
                coach, 'coach', user_preferences, user_bookings, db
            )
            scored_coaches.append((coach, score))
        
        scored_coaches.sort(key=lambda x: x[1], reverse=True)
        
        for coach, score in scored_coaches[:limit]:
            reason = RecommendationReason.PERSONAL
            explanation = "根据您的偏好为您推荐这位教练"
            
            if coach.rating >= 4.5:
                reason = RecommendationReason.POPULAR
                explanation = f"这位教练评分{coach.rating}分，深受会员喜爱"
            
            recommendations.append({
                'coach': coach,
                'score': score,
                'reason': reason,
                'explanation': explanation
            })
    
    elif recommendation_type == RecommendationType.PRODUCT:
        products = db.query(NutritionProduct).filter(
            NutritionProduct.is_active == True
        ).all()
        
        scored_products = []
        for product in products:
            score = calculate_recommendation_score(
                product, 'product', user_preferences, user_bookings, db
            )
            scored_products.append((product, score))
        
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        for product, score in scored_products[:limit]:
            reason = RecommendationReason.PERSONAL
            explanation = "根据您的健身目标为您推荐"
            
            if product.is_recommended:
                reason = RecommendationReason.POPULAR
                explanation = "这是我们的推荐产品"
            
            recommendations.append({
                'product': product,
                'score': score,
                'reason': reason,
                'explanation': explanation
            })
    
    return recommendations

# ========================================
# 获取推荐列表
# ========================================

@router.get("", response_model=ResponseModel)
async def get_recommendations(
    recommendation_type: RecommendationType = Query(..., description="推荐类型"),
    limit: int = Query(10, ge=1, le=20, description="返回数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取智能推荐列表
    
    根据会员的课程偏好、训练频率与目标，推荐适合的新课程、教练或营养产品
    
    Args:
        recommendation_type: 推荐类型（课程/教练/产品）
        limit: 返回数量
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含推荐列表的响应
    """
    recommendations = generate_recommendations_for_user(
        current_user.id, recommendation_type, db, limit
    )
    
    result = []
    for rec in recommendations:
        rec_dict = {
            'score': rec['score'],
            'reason': rec['reason'].value if rec['reason'] else None,
            'explanation': rec['explanation']
        }
        
        if 'course' in rec:
            course = rec['course']
            rec_dict['type'] = 'course'
            rec_dict['item'] = {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'category': course.category.value,
                'course_type': course.course_type.value,
                'duration': course.duration,
                'difficulty_level': course.difficulty_level,
                'calories_burned': course.calories_burned,
                'image_url': course.image_url
            }
        
        elif 'coach' in rec:
            coach = rec['coach']
            rec_dict['type'] = 'coach'
            rec_dict['item'] = {
                'id': coach.id,
                'user_id': coach.user_id,
                'specialization': coach.specialization,
                'experience_years': coach.experience_years,
                'bio': coach.bio,
                'rating': coach.rating,
                'review_count': coach.review_count,
                'hourly_rate': coach.hourly_rate,
                'real_name': coach.user.real_name if coach.user else None,
                'avatar': coach.user.avatar if coach.user else None
            }
        
        elif 'product' in rec:
            product = rec['product']
            rec_dict['type'] = 'product'
            rec_dict['item'] = {
                'id': product.id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category.value,
                'description': product.description,
                'price': product.price,
                'original_price': product.original_price,
                'stock': product.stock,
                'unit': product.unit,
                'suitable_for': product.suitable_for,
                'benefits': product.benefits,
                'image_url': product.image_url,
                'is_recommended': product.is_recommended,
                'rating': product.rating,
                'review_count': product.review_count,
                'sales_count': product.sales_count
            }
        
        result.append(rec_dict)
    
    save_recommendations_to_db(current_user.id, recommendation_type, recommendations, db)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            'recommendation_type': recommendation_type.value,
            'recommendations': result
        }
    )

def save_recommendations_to_db(
    user_id: int,
    recommendation_type: RecommendationType,
    recommendations: List[Dict],
    db: Session
):
    """
    保存推荐记录到数据库
    
    Args:
        user_id: 用户ID
        recommendation_type: 推荐类型
        recommendations: 推荐列表
        db: 数据库会话
    """
    for rec in recommendations:
        new_rec = Recommendation(
            user_id=user_id,
            recommendation_type=recommendation_type,
            reason=rec.get('reason'),
            score=rec.get('score', 0.0),
            explanation=rec.get('explanation')
        )
        
        if 'course' in rec:
            new_rec.course_id = rec['course'].id
        elif 'coach' in rec:
            new_rec.coach_id = rec['coach'].id
        elif 'product' in rec:
            new_rec.product_id = rec['product'].id
        
        db.add(new_rec)
    
    db.commit()

# ========================================
# 获取推荐历史
# ========================================

@router.get("/history", response_model=PaginatedResponse)
async def get_recommendation_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    recommendation_type: Optional[RecommendationType] = Query(None, description="推荐类型筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐历史记录
    
    Args:
        page: 页码
        page_size: 每页数量
        recommendation_type: 推荐类型筛选
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的推荐历史列表
    """
    query = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    )
    
    if recommendation_type:
        query = query.filter(Recommendation.recommendation_type == recommendation_type)
    
    query = query.order_by(Recommendation.created_at.desc())
    
    paginated = paginate_query(query, page, page_size)
    
    recs_response = []
    for rec in paginated.items:
        rec_dict = {
            'id': rec.id,
            'recommendation_type': rec.recommendation_type.value,
            'reason': rec.reason.value if rec.reason else None,
            'score': rec.score,
            'explanation': rec.explanation,
            'is_viewed': rec.is_viewed,
            'is_clicked': rec.is_clicked,
            'is_purchased': rec.is_purchased,
            'created_at': rec.created_at.isoformat() if rec.created_at else None
        }
        
        if rec.course:
            rec_dict['item'] = {
                'type': 'course',
                'id': rec.course.id,
                'name': rec.course.name
            }
        elif rec.coach:
            rec_dict['item'] = {
                'type': 'coach',
                'id': rec.coach.id,
                'real_name': rec.coach.user.real_name if rec.coach.user else None
            }
        elif rec.product:
            rec_dict['item'] = {
                'type': 'product',
                'id': rec.product.id,
                'name': rec.product.name
            }
        
        recs_response.append(rec_dict)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"recommendations": recs_response},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 标记推荐已查看
# ========================================

@router.put("/{recommendation_id}/view", response_model=ResponseModel)
async def mark_recommendation_viewed(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记推荐为已查看
    
    Args:
        recommendation_id: 推荐ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推荐记录不存在"
        )
    
    rec.is_viewed = True
    db.commit()
    
    return ResponseModel(
        code=200,
        message="已标记为已查看",
        data=None
    )

# ========================================
# 标记推荐已点击
# ========================================

@router.put("/{recommendation_id}/click", response_model=ResponseModel)
async def mark_recommendation_clicked(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记推荐为已点击
    
    Args:
        recommendation_id: 推荐ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推荐记录不存在"
        )
    
    rec.is_clicked = True
    rec.is_viewed = True
    db.commit()
    
    return ResponseModel(
        code=200,
        message="已标记为已点击",
        data=None
    )

# ========================================
# 获取个性化推荐（综合推荐）
# ========================================

@router.get("/personalized/all", response_model=ResponseModel)
async def get_personalized_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取综合个性化推荐
    
    返回课程、教练、营养产品三种类型的推荐，用于首页展示
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含综合推荐的响应
    """
    course_recommendations = generate_recommendations_for_user(
        current_user.id, RecommendationType.COURSE, db, 5
    )
    
    coach_recommendations = generate_recommendations_for_user(
        current_user.id, RecommendationType.COACH, db, 3
    )
    
    product_recommendations = generate_recommendations_for_user(
        current_user.id, RecommendationType.PRODUCT, db, 4
    )
    
    result = {
        'courses': [],
        'coaches': [],
        'products': []
    }
    
    for rec in course_recommendations:
        course = rec['course']
        result['courses'].append({
            'id': course.id,
            'name': course.name,
            'category': course.category.value,
            'course_type': course.course_type.value,
            'duration': course.duration,
            'difficulty_level': course.difficulty_level,
            'image_url': course.image_url,
            'recommendation_reason': rec['explanation'],
            'score': rec['score']
        })
    
    for rec in coach_recommendations:
        coach = rec['coach']
        result['coaches'].append({
            'id': coach.id,
            'specialization': coach.specialization,
            'experience_years': coach.experience_years,
            'rating': coach.rating,
            'review_count': coach.review_count,
            'hourly_rate': coach.hourly_rate,
            'real_name': coach.user.real_name if coach.user else None,
            'avatar': coach.user.avatar if coach.user else None,
            'recommendation_reason': rec['explanation'],
            'score': rec['score']
        })
    
    for rec in product_recommendations:
        product = rec['product']
        result['products'].append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category.value,
            'price': product.price,
            'original_price': product.original_price,
            'image_url': product.image_url,
            'is_recommended': product.is_recommended,
            'rating': product.rating,
            'sales_count': product.sales_count,
            'recommendation_reason': rec['explanation'],
            'score': rec['score']
        })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=result
    )
