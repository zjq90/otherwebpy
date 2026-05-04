"""
好友系统路由模块
处理用户搜索、添加好友、查看好友、私信等功能
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from app.database import get_db
from app.models import User, Friendship, Message
from app.schemas import (
    UserPublic, FriendshipCreate, FriendshipResponse,
    MessageCreate, MessageResponse, MessageConversation,
    APIResponse, PaginatedResponse
)
from app.auth import get_current_active_user
from math import ceil

router = APIRouter(prefix="/friends", tags=["好友系统"])


@router.get("/search", response_model=List[UserPublic], summary="搜索用户")
async def search_users(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    搜索用户（按用户名或昵称）
    
    - **keyword**: 搜索关键词
    """
    users = db.query(User).filter(
        or_(
            User.username.contains(keyword),
            User.nickname.contains(keyword)
        ),
        User.id != current_user.id,
        User.is_active == True
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return [UserPublic.from_orm(user) for user in users]


@router.get("/profile/{user_id}", response_model=UserPublic, summary="查看用户公开资料")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    查看指定用户的公开资料
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserPublic.from_orm(user)


@router.post("/add", response_model=FriendshipResponse, summary="添加好友")
async def add_friend(
    friendship_data: FriendshipCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    添加好友（发送好友请求）
    
    - **user_id_2**: 要添加的用户ID
    """
    # 检查目标用户是否存在
    target_user = db.query(User).filter(
        User.id == friendship_data.user_id_2,
        User.is_active == True
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标用户不存在"
        )
    
    # 不能添加自己为好友
    if friendship_data.user_id_2 == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能添加自己为好友"
        )
    
    # 检查是否已经是好友或有待处理的请求
    existing_friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id_1 == current_user.id, Friendship.user_id_2 == friendship_data.user_id_2),
            and_(Friendship.user_id_1 == friendship_data.user_id_2, Friendship.user_id_2 == current_user.id)
        )
    ).first()
    
    if existing_friendship:
        if existing_friendship.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经是好友了"
            )
        elif existing_friendship.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已有待处理的好友请求"
            )
    
    # 创建好友请求
    new_friendship = Friendship(
        user_id_1=current_user.id,
        user_id_2=friendship_data.user_id_2,
        status="pending"
    )
    
    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)
    
    response = FriendshipResponse.from_orm(new_friendship)
    response.user = UserPublic.from_orm(target_user)
    
    return response


@router.get("/requests", response_model=PaginatedResponse, summary="获取好友请求列表")
async def get_friend_requests(
    status: Optional[str] = Query(None, description="状态筛选: pending, accepted, rejected"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取好友请求列表（收到的请求）
    
    - **status**: 状态筛选 (pending, accepted, rejected)
    """
    query = db.query(Friendship).filter(
        Friendship.user_id_2 == current_user.id
    )
    
    if status:
        query = query.filter(Friendship.status == status)
    else:
        query = query.filter(Friendship.status == "pending")
    
    query = query.order_by(desc(Friendship.created_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    friendships = query.offset((page - 1) * page_size).limit(page_size).all()
    
    responses = []
    for friendship in friendships:
        response = FriendshipResponse.from_orm(friendship)
        response.user = UserPublic.from_orm(friendship.user1)
        responses.append(response)
    
    return PaginatedResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/sent-requests", response_model=PaginatedResponse, summary="获取已发送的好友请求")
async def get_sent_friend_requests(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取已发送的好友请求列表
    """
    query = db.query(Friendship).filter(
        Friendship.user_id_1 == current_user.id
    )
    
    if status:
        query = query.filter(Friendship.status == status)
    
    query = query.order_by(desc(Friendship.created_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    friendships = query.offset((page - 1) * page_size).limit(page_size).all()
    
    responses = []
    for friendship in friendships:
        response = FriendshipResponse.from_orm(friendship)
        response.user = UserPublic.from_orm(friendship.user2)
        responses.append(response)
    
    return PaginatedResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/requests/{friendship_id}/accept", response_model=FriendshipResponse, summary="接受好友请求")
async def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    接受好友请求
    """
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.user_id_2 == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友请求不存在"
        )
    
    friendship.status = "accepted"
    db.commit()
    db.refresh(friendship)
    
    response = FriendshipResponse.from_orm(friendship)
    response.user = UserPublic.from_orm(friendship.user1)
    
    return response


@router.post("/requests/{friendship_id}/reject", response_model=APIResponse, summary="拒绝好友请求")
async def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    拒绝好友请求
    """
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.user_id_2 == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友请求不存在"
        )
    
    friendship.status = "rejected"
    db.commit()
    
    return APIResponse(
        code=200,
        message="已拒绝好友请求",
        data={"friendship_id": friendship_id}
    )


@router.get("", response_model=PaginatedResponse, summary="获取好友列表")
async def get_friends(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取好友列表
    """
    # 查询所有好友关系（双向）
    friendships = db.query(Friendship).filter(
        or_(
            Friendship.user_id_1 == current_user.id,
            Friendship.user_id_2 == current_user.id
        ),
        Friendship.status == "accepted"
    ).all()
    
    # 提取好友ID
    friend_ids = []
    for f in friendships:
        if f.user_id_1 == current_user.id:
            friend_ids.append(f.user_id_2)
        else:
            friend_ids.append(f.user_id_1)
    
    # 查询好友信息
    total = len(friend_ids)
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_friend_ids = friend_ids[start:end]
    
    friends = db.query(User).filter(User.id.in_(paginated_friend_ids)).all()
    
    return PaginatedResponse(
        items=[UserPublic.from_orm(friend) for friend in friends],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.delete("/{friend_id}", response_model=APIResponse, summary="删除好友")
async def delete_friend(
    friend_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除好友
    """
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id_1 == current_user.id, Friendship.user_id_2 == friend_id),
            and_(Friendship.user_id_1 == friend_id, Friendship.user_id_2 == current_user.id)
        ),
        Friendship.status == "accepted"
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="不是好友关系"
        )
    
    db.delete(friendship)
    db.commit()
    
    return APIResponse(
        code=200,
        message="已删除好友",
        data={"friend_id": friend_id}
    )


# ==================== 私信相关 ====================

@router.post("/messages", response_model=MessageResponse, summary="发送私信")
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发送私信
    
    - **receiver_id**: 接收者ID
    - **content**: 消息内容
    """
    # 检查接收者是否存在
    receiver = db.query(User).filter(
        User.id == message_data.receiver_id,
        User.is_active == True
    ).first()
    
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="接收者不存在"
        )
    
    # 不能给自己发消息
    if message_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能给自己发送消息"
        )
    
    # 创建消息
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    response = MessageResponse.from_orm(new_message)
    response.sender = UserPublic.from_orm(current_user)
    response.receiver = UserPublic.from_orm(receiver)
    
    return response


@router.get("/messages/conversations", response_model=List[MessageConversation], summary="获取会话列表")
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取会话列表（与每个用户的最新消息）
    """
    # 获取所有涉及当前用户的消息
    messages = db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).order_by(desc(Message.created_at)).all()
    
    # 按用户分组，获取每个对话的最新消息
    conversations_dict = {}
    for msg in messages:
        other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        
        if other_user_id not in conversations_dict:
            conversations_dict[other_user_id] = {
                "last_message": msg,
                "unread_count": 0
            }
        
        # 统计未读消息
        if msg.receiver_id == current_user.id and not msg.is_read:
            conversations_dict[other_user_id]["unread_count"] += 1
    
    # 转换为响应格式
    conversations = []
    for other_user_id, data in conversations_dict.items():
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if other_user:
            msg_response = MessageResponse.from_orm(data["last_message"])
            msg_response.sender = UserPublic.from_orm(data["last_message"].sender)
            msg_response.receiver = UserPublic.from_orm(data["last_message"].receiver)
            
            conversations.append(MessageConversation(
                user=UserPublic.from_orm(other_user),
                last_message=msg_response,
                unread_count=data["unread_count"]
            ))
    
    return conversations


@router.get("/messages/{user_id}", response_model=List[MessageResponse], summary="获取与指定用户的消息记录")
async def get_messages_with_user(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取与指定用户的消息记录
    
    - **user_id**: 对方用户ID
    """
    # 查询消息（双向）
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).offset((page - 1) * page_size).limit(page_size).all()
    
    # 标记收到的消息为已读
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    
    db.commit()
    
    # 构建响应
    responses = []
    for msg in messages:
        msg_response = MessageResponse.from_orm(msg)
        msg_response.sender = UserPublic.from_orm(msg.sender)
        msg_response.receiver = UserPublic.from_orm(msg.receiver)
        responses.append(msg_response)
    
    return responses


@router.get("/messages/unread/count", response_model=APIResponse, summary="获取未读消息数量")
async def get_unread_message_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取未读消息总数
    """
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return APIResponse(
        code=200,
        message="success",
        data={"unread_count": count}
    )
