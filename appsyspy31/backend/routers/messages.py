"""
消息中心路由模块
处理消息的查询、已读标记、分类筛选等功能
支持课程提醒、续费通知、活动推送、系统公告等消息类型
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import User, UserRole, Message, MessageType
from schemas import (
    MessageCreate, MessageUpdate, MessageResponse, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取消息列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_messages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    message_type: Optional[MessageType] = Query(None, description="消息类型筛选"),
    is_read: Optional[bool] = Query(None, description="已读状态筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的消息列表
    
    支持分页、消息类型筛选、已读状态筛选
    
    Args:
        page: 页码
        page_size: 每页数量
        message_type: 消息类型筛选
        is_read: 已读状态筛选
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的消息列表
    """
    # 构建查询：只查询当前用户的消息
    query = db.query(Message).filter(Message.user_id == current_user.id)
    
    # 消息类型筛选
    if message_type:
        query = query.filter(Message.message_type == message_type)
    
    # 已读状态筛选
    if is_read is not None:
        query = query.filter(Message.is_read == is_read)
    
    # 按创建时间倒序排列
    query = query.order_by(Message.created_at.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    messages_response = [MessageResponse.model_validate(msg) for msg in paginated.items]
    
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
# 获取消息详情
# ========================================

@router.get("/{message_id}", response_model=ResponseModel)
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取消息详情
    
    同时会将消息标记为已读
    
    Args:
        message_id: 消息ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含消息详情的响应
    """
    # 查找消息（只能查看自己的消息）
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 标记为已读
    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
    
    message_response = MessageResponse.model_validate(message)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"message": message_response.model_dump()}
    )

# ========================================
# 标记消息为已读
# ========================================

@router.put("/{message_id}/mark-read", response_model=ResponseModel)
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    将单个消息标记为已读
    
    Args:
        message_id: 消息ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
    
    return ResponseModel(
        code=200,
        message="已标记为已读",
        data=None
    )

# ========================================
# 批量标记消息为已读
# ========================================

@router.post("/mark-all-read", response_model=ResponseModel)
async def mark_all_messages_read(
    message_type: Optional[MessageType] = Query(None, description="指定消息类型（可选）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    将当前用户的所有未读消息标记为已读
    
    可以指定消息类型，也可以标记所有类型
    
    Args:
        message_type: 消息类型（可选）
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    # 构建查询
    query = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == False
    )
    
    # 如果指定了消息类型
    if message_type:
        query = query.filter(Message.message_type == message_type)
    
    # 统计未读数量
    unread_count = query.count()
    
    # 标记为已读
    query.update({
        Message.is_read: True,
        Message.read_at: datetime.utcnow()
    }, synchronize_session=False)
    
    db.commit()
    
    return ResponseModel(
        code=200,
        message=f"已标记 {unread_count} 条消息为已读",
        data={"marked_count": unread_count}
    )

# ========================================
# 获取未读消息数量
# ========================================

@router.get("/stats/unread-count", response_model=ResponseModel)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的未读消息数量
    
    按消息类型分类统计
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含未读数量统计的响应
    """
    # 总未读数量
    total_unread = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == False
    ).count()
    
    # 按类型统计
    type_counts = {}
    for msg_type in MessageType:
        count = db.query(Message).filter(
            Message.user_id == current_user.id,
            Message.message_type == msg_type,
            Message.is_read == False
        ).count()
        type_counts[msg_type.value] = count
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "total_unread": total_unread,
            "type_counts": type_counts
        }
    )

# ========================================
# 删除消息
# ========================================

@router.delete("/{message_id}", response_model=ResponseModel)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除消息
    
    用户只能删除自己的消息
    
    Args:
        message_id: 消息ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    db.delete(message)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="消息已删除",
        data=None
    )

# ========================================
# 发送消息（管理员/工作人员权限）
# ========================================

@router.post("/send", response_model=ResponseModel)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    发送消息给用户
    
    需要管理员或工作人员权限
    用于发送系统公告、活动推送、续费通知等
    
    Args:
        message_data: 消息数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含发送的消息信息的响应
    """
    # 检查接收用户是否存在
    user = db.query(User).filter(User.id == message_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="接收用户不存在"
        )
    
    # 创建消息
    new_message = Message(
        user_id=message_data.user_id,
        message_type=message_data.message_type,
        title=message_data.title,
        content=message_data.content,
        image_url=message_data.image_url,
        link_url=message_data.link_url,
        related_id=message_data.related_id,
        related_type=message_data.related_type,
        is_read=False
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    message_response = MessageResponse.model_validate(new_message)
    
    return ResponseModel(
        code=200,
        message="消息发送成功",
        data={"message": message_response.model_dump()}
    )

# ========================================
# 批量发送消息（管理员权限）
# ========================================

@router.post("/send-batch", response_model=ResponseModel)
async def send_batch_messages(
    user_ids: List[int],
    message_type: MessageType,
    title: str,
    content: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    批量发送消息给多个用户
    
    需要管理员权限
    
    Args:
        user_ids: 接收用户ID列表
        message_type: 消息类型
        title: 消息标题
        content: 消息内容
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户ID列表不能为空"
        )
    
    # 检查用户是否存在
    valid_users = db.query(User).filter(User.id.in_(user_ids)).all()
    valid_user_ids = [user.id for user in valid_users]
    
    if len(valid_user_ids) != len(user_ids):
        invalid_count = len(user_ids) - len(valid_user_ids)
        # 继续处理有效用户，但提示有无效用户
    
    # 批量创建消息
    messages_to_create = []
    for user_id in valid_user_ids:
        messages_to_create.append(Message(
            user_id=user_id,
            message_type=message_type,
            title=title,
            content=content,
            is_read=False
        ))
    
    db.bulk_save_objects(messages_to_create)
    db.commit()
    
    return ResponseModel(
        code=200,
        message=f"成功发送 {len(messages_to_create)} 条消息",
        data={"sent_count": len(messages_to_create)}
    )

# ========================================
# 获取消息类型列表
# ========================================

@router.get("/types/list", response_model=ResponseModel)
async def get_message_types():
    """
    获取所有消息类型
    
    Returns:
        ResponseModel: 包含消息类型列表的响应
    """
    type_names = {
        MessageType.COURSE_REMINDER: "课程提醒",
        MessageType.RENEWAL_NOTICE: "续费通知",
        MessageType.ACTIVITY_PUSH: "活动推送",
        MessageType.SYSTEM_ANNOUNCEMENT: "系统公告"
    }
    
    types = [
        {
            "value": msg_type.value,
            "label": type_names.get(msg_type, msg_type.value)
        }
        for msg_type in MessageType
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"types": types}
    )
