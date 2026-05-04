"""
在线客服聊天路由模块
处理聊天会话的创建、消息发送、消息查询等功能
支持会员与客服/教练之间的实时聊天
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import (
    User, UserRole, ChatSession, ChatMessage, ChatType, Coach
)
from schemas import (
    ChatSessionCreate, ChatSessionResponse, ChatMessageCreate,
    ChatMessageResponse, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取聊天会话列表
# ========================================

@router.get("/sessions", response_model=PaginatedResponse)
async def get_chat_sessions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="会话状态筛选"),
    chat_type: Optional[ChatType] = Query(None, description="聊天类型筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的聊天会话列表
    
    会员看到的是自己发起的会话
    客服/教练看到的是分配给自己的会话
    
    Args:
        page: 页码
        page_size: 每页数量
        is_active: 会话状态筛选
        chat_type: 聊天类型筛选
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的会话列表
    """
    # 构建查询
    query = db.query(ChatSession)
    
    # 根据角色过滤会话
    if current_user.role == UserRole.MEMBER:
        # 会员只能看到自己的会话
        query = query.filter(ChatSession.user_id == current_user.id)
    else:
        # 客服/教练可以看到分配给自己的会话
        query = query.filter(ChatSession.staff_id == current_user.id)
    
    # 状态筛选
    if is_active is not None:
        query = query.filter(ChatSession.is_active == is_active)
    
    # 类型筛选
    if chat_type:
        query = query.filter(ChatSession.chat_type == chat_type)
    
    # 按最后消息时间倒序排列
    query = query.order_by(ChatSession.last_message_at.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    sessions_response = []
    for session in paginated.items:
        session_response = ChatSessionResponse.model_validate(session)
        if session.user:
            session_response.user = session_response.user.model_validate(session.user)
        if session.staff:
            session_response.staff = session_response.staff.model_validate(session.staff)
        
        # 获取最后一条消息
        last_message = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.desc()).first()
        
        if last_message:
            setattr(session_response, 'last_message', {
                'content': last_message.content,
                'created_at': last_message.created_at.isoformat() if last_message.created_at else None,
                'sender_id': last_message.sender_id
            })
        
        sessions_response.append(session_response)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"sessions": [s.model_dump() for s in sessions_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 创建聊天会话
# ========================================

@router.post("/sessions", response_model=ResponseModel)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的聊天会话
    
    会员可以创建与客服或教练的会话
    如果是教练咨询类型，必须指定教练ID
    
    Args:
        session_data: 会话数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新会话信息的响应
    """
    # 只有会员可以创建会话
    if current_user.role != UserRole.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有会员可以创建聊天会话"
        )
    
    # 检查是否需要指定工作人员
    staff_id = session_data.staff_id
    
    # 如果是教练咨询类型，需要检查教练是否存在
    if session_data.chat_type == ChatType.COACH_CONSULT:
        if not staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教练咨询必须指定教练"
            )
        
        # 检查教练是否存在且可预约
        coach = db.query(Coach).filter(
            Coach.user_id == staff_id,
            Coach.is_available == True
        ).first()
        
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练不存在或不可预约"
            )
    else:
        # 客服咨询：分配在线客服（这里简化处理，使用管理员作为客服）
        if not staff_id:
            # 查找管理员或工作人员作为客服
            staff = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.STAFF]),
                User.is_active == True
            ).first()
            
            if not staff:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="暂无可用客服"
                )
            
            staff_id = staff.id
    
    # 检查用户是否存在
    staff = db.query(User).filter(User.id == staff_id).first()
    
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作人员不存在"
        )
    
    # 检查是否已有相同类型的活跃会话
    existing_session = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.staff_id == staff_id,
        ChatSession.chat_type == session_data.chat_type,
        ChatSession.is_active == True
    ).first()
    
    if existing_session:
        # 返回现有会话
        session_response = ChatSessionResponse.model_validate(existing_session)
        return ResponseModel(
            code=200,
            message="已有活跃会话",
            data={"session": session_response.model_dump(), "is_new": False}
        )
    
    # 创建新会话
    new_session = ChatSession(
        user_id=current_user.id,
        staff_id=staff_id,
        chat_type=session_data.chat_type,
        subject=session_data.subject,
        is_active=True,
        last_message_at=datetime.utcnow()
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    session_response = ChatSessionResponse.model_validate(new_session)
    
    return ResponseModel(
        code=200,
        message="会话创建成功",
        data={"session": session_response.model_dump(), "is_new": True}
    )

# ========================================
# 获取会话详情
# ========================================

@router.get("/sessions/{session_id}", response_model=ResponseModel)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取聊天会话详情
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含会话详情的响应
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 权限检查：只能查看自己参与的会话
    if (current_user.id != session.user_id and 
        current_user.id != session.staff_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该会话"
        )
    
    session_response = ChatSessionResponse.model_validate(session)
    if session.user:
        session_response.user = session_response.user.model_validate(session.user)
    if session.staff:
        session_response.staff = session_response.staff.model_validate(session.staff)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"session": session_response.model_dump()}
    )

# ========================================
# 关闭聊天会话
# ========================================

@router.post("/sessions/{session_id}/close", response_model=ResponseModel)
async def close_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    关闭聊天会话
    
    会话双方都可以关闭会话
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 权限检查
    if (current_user.id != session.user_id and 
        current_user.id != session.staff_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该会话"
        )
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话已关闭"
        )
    
    # 关闭会话
    session.is_active = False
    session.closed_at = datetime.utcnow()
    db.commit()
    
    return ResponseModel(
        code=200,
        message="会话已关闭",
        data=None
    )

# ========================================
# 获取会话消息列表
# ========================================

@router.get("/sessions/{session_id}/messages", response_model=PaginatedResponse)
async def get_chat_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取聊天会话的消息列表
    
    Args:
        session_id: 会话ID
        page: 页码
        page_size: 每页数量
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的消息列表
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 权限检查
    if (current_user.id != session.user_id and 
        current_user.id != session.staff_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该会话消息"
        )
    
    # 构建查询
    query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
    
    # 按创建时间正序排列（旧消息在前）
    query = query.order_by(ChatMessage.created_at.asc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    messages_response = []
    for message in paginated.items:
        message_response = ChatMessageResponse.model_validate(message)
        if message.sender:
            message_response.sender = message_response.sender.model_validate(message.sender)
        messages_response.append(message_response)
    
    # 标记对方发送的消息为已读
    unread_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.sender_id != current_user.id,
        ChatMessage.is_read == False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
        msg.read_at = datetime.utcnow()
    
    db.commit()
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"messages": [m.model_dump() for m in messages_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 发送消息
# ========================================

@router.post("/messages", response_model=ResponseModel)
async def send_chat_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发送聊天消息
    
    Args:
        message_data: 消息数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含发送的消息信息的响应
    """
    session = db.query(ChatSession).filter(ChatSession.id == message_data.session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 权限检查：只能在自己参与的会话中发送消息
    if (current_user.id != session.user_id and 
        current_user.id != session.staff_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在该会话中发送消息"
        )
    
    # 检查会话是否已关闭
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话已关闭，无法发送消息"
        )
    
    # 创建消息
    new_message = ChatMessage(
        session_id=message_data.session_id,
        sender_id=current_user.id,
        message_type=message_data.message_type,
        content=message_data.content,
        file_url=message_data.file_url,
        is_read=False
    )
    
    db.add(new_message)
    
    # 更新会话的最后消息时间
    session.last_message_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    message_response = ChatMessageResponse.model_validate(new_message)
    
    return ResponseModel(
        code=200,
        message="消息发送成功",
        data={"message": message_response.model_dump()}
    )

# ========================================
# 获取未读消息数量
# ========================================

@router.get("/stats/unread-count", response_model=ResponseModel)
async def get_chat_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的未读聊天消息数量
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含未读数量的响应
    """
    # 查找用户参与的所有会话
    if current_user.role == UserRole.MEMBER:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).all()
    else:
        sessions = db.query(ChatSession).filter(
            ChatSession.staff_id == current_user.id,
            ChatSession.is_active == True
        ).all()
    
    session_ids = [session.id for session in sessions]
    
    # 统计未读消息（对方发送的）
    if session_ids:
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.session_id.in_(session_ids),
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        ).count()
    else:
        unread_count = 0
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"unread_count": unread_count}
    )

# ========================================
# 获取可用客服/教练列表
# ========================================

@router.get("/staff/available", response_model=ResponseModel)
async def get_available_staff(
    chat_type: ChatType = Query(..., description="聊天类型"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取可用的工作人员列表（客服/教练）
    
    Args:
        chat_type: 聊天类型
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含工作人员列表的响应
    """
    if chat_type == ChatType.COACH_CONSULT:
        # 获取可预约的教练列表
        coaches = db.query(Coach).filter(
            Coach.is_available == True
        ).all()
        
        staff_list = []
        for coach in coaches:
            if coach.user:
                staff_list.append({
                    "id": coach.user.id,
                    "name": coach.user.real_name or coach.user.username,
                    "avatar": coach.user.avatar,
                    "specialization": coach.specialization,
                    "rating": coach.rating,
                    "type": "coach"
                })
    else:
        # 获取客服列表（管理员和工作人员）
        staff_users = db.query(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.STAFF]),
            User.is_active == True
        ).all()
        
        staff_list = []
        for staff in staff_users:
            staff_list.append({
                "id": staff.id,
                "name": staff.real_name or staff.username,
                "avatar": staff.avatar,
                "role": staff.role.value,
                "type": "staff"
            })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"staff_list": staff_list}
    )
