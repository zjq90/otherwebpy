"""
动态广场路由模块
处理动态发布、点赞、评论、分享等功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.database import get_db
from app.models import User, Post, Like, Comment, Share
from app.schemas import (
    PostCreate, PostUpdate, PostResponse, 
    CommentCreate, CommentResponse,
    LikeResponse, APIResponse, PaginatedResponse
)
from app.auth import get_current_active_user
from math import ceil

router = APIRouter(prefix="/posts", tags=["动态广场"])


@router.post("", response_model=PostResponse, summary="发布动态")
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发布新动态
    
    - **content**: 动态内容
    - **post_type**: 动态类型 (training, diet, achievement)
    - **images**: 图片URL列表（逗号分隔）
    - **is_public**: 是否公开
    """
    # 创建新动态
    new_post = Post(
        user_id=current_user.id,
        content=post_data.content,
        post_type=post_data.post_type,
        images=post_data.images,
        is_public=post_data.is_public
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # 关联作者信息
    new_post.author = current_user
    
    return PostResponse.from_orm(new_post)


@router.get("", response_model=PaginatedResponse, summary="获取动态列表")
async def get_posts(
    post_type: Optional[str] = Query(None, description="动态类型筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取动态列表（分页）
    
    - **post_type**: 动态类型筛选 (training, diet, achievement)
    - **user_id**: 用户ID筛选（查看特定用户的动态）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 构建查询
    query = db.query(Post).filter(Post.is_public == True)
    
    # 按类型筛选
    if post_type:
        query = query.filter(Post.post_type == post_type)
    
    # 按用户筛选
    if user_id:
        query = query.filter(Post.user_id == user_id)
    
    # 按创建时间倒序排列
    query = query.order_by(desc(Post.created_at))
    
    # 计算总数
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 分页查询
    posts = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 为每个动态添加作者信息和点赞状态
    post_responses = []
    for post in posts:
        post_response = PostResponse.from_orm(post)
        post_response.author = post.author
        # 检查当前用户是否点赞
        is_liked = db.query(Like).filter(
            Like.user_id == current_user.id,
            Like.post_id == post.id
        ).first() is not None
        post_response.is_liked = is_liked
        post_responses.append(post_response)
    
    return PaginatedResponse(
        items=post_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{post_id}", response_model=PostResponse, summary="获取动态详情")
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取单条动态详情
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 检查是否有权限查看
    if not post.is_public and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此动态"
        )
    
    # 检查当前用户是否点赞
    is_liked = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post.id
    ).first() is not None
    
    post_response = PostResponse.from_orm(post)
    post_response.author = post.author
    post_response.is_liked = is_liked
    
    return post_response


@router.put("/{post_id}", response_model=PostResponse, summary="更新动态")
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新动态内容
    只有动态作者可以更新
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 检查是否是作者
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此动态"
        )
    
    # 更新动态信息
    update_data = post_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(post, key, value)
    
    db.commit()
    db.refresh(post)
    
    post_response = PostResponse.from_orm(post)
    post_response.author = post.author
    
    return post_response


@router.delete("/{post_id}", response_model=APIResponse, summary="删除动态")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除动态
    只有动态作者可以删除
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 检查是否是作者
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此动态"
        )
    
    db.delete(post)
    db.commit()
    
    return APIResponse(
        code=200,
        message="删除成功",
        data={"post_id": post_id}
    )


@router.post("/{post_id}/like", response_model=APIResponse, summary="点赞/取消点赞")
async def toggle_like(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    点赞或取消点赞动态
    如果已点赞则取消，未点赞则添加
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 检查是否已点赞
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        post.likes_count -= 1
        is_liked = False
        message = "取消点赞成功"
    else:
        # 添加点赞
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        post.likes_count += 1
        is_liked = True
        message = "点赞成功"
    
    db.commit()
    
    return APIResponse(
        code=200,
        message=message,
        data={"post_id": post_id, "is_liked": is_liked, "likes_count": post.likes_count}
    )


@router.get("/{post_id}/comments", response_model=List[CommentResponse], summary="获取动态评论")
async def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取动态的评论列表
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 查询评论
    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(Comment.created_at).offset((page - 1) * page_size).limit(page_size).all()
    
    # 添加用户信息
    comment_responses = []
    for comment in comments:
        comment_response = CommentResponse.from_orm(comment)
        comment_response.user = comment.user
        comment_responses.append(comment_response)
    
    return comment_responses


@router.post("/comments", response_model=CommentResponse, summary="发表评论")
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发表评论
    
    - **post_id**: 动态ID
    - **content**: 评论内容
    - **parent_id**: 父评论ID（用于回复）
    """
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 创建评论
    new_comment = Comment(
        user_id=current_user.id,
        post_id=comment_data.post_id,
        content=comment_data.content,
        parent_id=comment_data.parent_id
    )
    
    db.add(new_comment)
    post.comments_count += 1
    db.commit()
    db.refresh(new_comment)
    
    comment_response = CommentResponse.from_orm(new_comment)
    comment_response.user = current_user
    
    return comment_response


@router.delete("/comments/{comment_id}", response_model=APIResponse, summary="删除评论")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除评论
    只有评论作者或动态作者可以删除
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限：评论作者或动态作者
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    
    if comment.user_id != current_user.id and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此评论"
        )
    
    db.delete(comment)
    post.comments_count -= 1
    db.commit()
    
    return APIResponse(
        code=200,
        message="删除成功",
        data={"comment_id": comment_id}
    )


@router.post("/{post_id}/share", response_model=APIResponse, summary="分享动态")
async def share_post(
    post_id: int,
    share_platform: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    分享动态
    
    - **share_platform**: 分享平台 (wechat, weibo, qq等)
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    
    # 创建分享记录
    new_share = Share(
        user_id=current_user.id,
        post_id=post_id,
        share_platform=share_platform
    )
    
    db.add(new_share)
    post.shares_count += 1
    db.commit()
    
    return APIResponse(
        code=200,
        message="分享成功",
        data={"post_id": post_id, "shares_count": post.shares_count}
    )
