"""
客服咨询路由模块
包含在线客服聊天功能
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime
from typing import Optional, List
import uuid
import logging

from app.database import get_db
from app.models import User, ChatSession, ChatMessage
from app.schemas.common import success, success_page, error
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["客服咨询"])


def generate_session_id() -> str:
    """
    生成会话ID
    """
    return f"CHAT_{uuid.uuid4().hex[:16]}"


@router.get("/sessions")
async def get_chat_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的会话列表
    """
    # 统计总数
    count_result = await db.execute(
        select(func.count(ChatSession.id)).where(
            ChatSession.user_id == current_user.id
        )
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.last_message_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    sessions = result.scalars().all()
    
    return success_page(
        items=[s.to_dict() for s in sessions],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/session/start")
async def start_chat_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    开始新的客服会话
    或恢复未结束的会话
    """
    # 检查是否有未结束的会话
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.user_id == current_user.id,
            ChatSession.status == 1  # 进行中
        ).order_by(ChatSession.create_time.desc())
    )
    existing_session = result.scalar_one_or_none()
    
    if existing_session:
        return success(data={
            "session_id": existing_session.session_id,
            "is_new": False,
            "unread_count": existing_session.unread_count
        })
    
    # 创建新会话
    session_id = generate_session_id()
    new_session = ChatSession(
        session_id=session_id,
        user_id=current_user.id,
        status=1,
        last_message="欢迎使用旧衣回收客服！请问有什么可以帮助您的？"
    )
    
    db.add(new_session)
    
    # 添加欢迎消息
    welcome_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        message_type="text",
        content="欢迎使用旧衣回收客服！请问有什么可以帮助您的？\n\n您可以咨询以下问题：\n1. 旧衣回收流程\n2. 积分规则\n3. 商品兑换\n4. 订单问题\n5. 其他问题",
        sender_type="system",
        is_read=1
    )
    db.add(welcome_message)
    
    await db.commit()
    await db.refresh(new_session)
    
    return success(data={
        "session_id": new_session.session_id,
        "is_new": True,
        "unread_count": 0
    })


@router.get("/messages")
async def get_chat_messages(
    session_id: str = Query(..., description="会话ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话的消息列表
    """
    # 验证会话归属
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return error(code=404, message="会话不存在")
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id
        )
    )
    total = count_result.scalar() or 0
    
    # 查询消息（倒序，最新的在后面）
    offset = (page - 1) * page_size
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.create_time)
        .offset(offset)
        .limit(page_size)
    )
    messages = result.scalars().all()
    
    # 标记消息为已读
    await db.execute(
        update(ChatMessage).where(
            ChatMessage.session_id == session_id,
            ChatMessage.sender_type != "user",
            ChatMessage.is_read == 0
        ).values(is_read=1, read_time=datetime.now())
    )
    
    # 重置未读计数
    session.unread_count = 0
    await db.commit()
    
    return success_page(
        items=[m.to_dict() for m in messages],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/message/send")
async def send_chat_message(
    session_id: str,
    content: str,
    message_type: str = "text",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    发送消息
    支持文本、图片等消息类型
    """
    # 验证会话归属
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return error(code=404, message="会话不存在")
    
    # 创建用户消息
    user_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        message_type=message_type,
        content=content,
        sender_type="user",
        sender_id=current_user.id,
        is_read=1
    )
    db.add(user_message)
    
    # 更新会话最后消息
    session.last_message = content[:50] if len(content) > 50 else content
    session.last_message_time = datetime.now()
    
    # 模拟客服自动回复（实际项目应该是客服人员回复）
    auto_reply = generate_auto_reply(content)
    if auto_reply:
        reply_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            message_type="text",
            content=auto_reply,
            sender_type="customer_service",
            sender_id=1,  # 客服ID
            is_read=0
        )
        db.add(reply_message)
        
        # 更新会话最后消息为回复
        session.last_message = auto_reply[:50] if len(auto_reply) > 50 else auto_reply
        session.unread_count += 1
    
    await db.commit()
    await db.refresh(user_message)
    
    return success(data={
        "message_id": user_message.id,
        "create_time": user_message.create_time.isoformat() if user_message.create_time else None
    }, message="发送成功")


def generate_auto_reply(user_message: str) -> Optional[str]:
    """
    模拟客服自动回复
    实际项目中可以接入AI客服或由人工回复
    """
    msg = user_message.lower()
    
    # 回收流程相关
    if any(keyword in msg for keyword in ["回收流程", "怎么回收", "回收步骤", "预约"]):
        return "旧衣回收流程如下：\n\n1. 在App中选择衣物类型，填写地址和预约时间\n2. 系统自动匹配回收人员\n3. 回收人员按约定时间上门验收\n4. 验收合格后，积分自动到账\n5. 衣物将进行消毒、分类处理\n\n请问您还有其他问题吗？"
    
    # 积分相关
    elif any(keyword in msg for keyword in ["积分", "积分规则", "怎么获得积分"]):
        return "关于积分规则：\n\n1. 回收旧衣：根据衣物类型、数量和品质获得积分\n   - T恤：10积分/件\n   - 毛衣：20积分/件\n   - 羽绒服：35积分/件\n   - 优质品质可获得1.5倍积分\n\n2. 邀请好友：邀请人获得100积分，被邀请人获得50积分\n\n3. 新用户注册：赠送100积分\n\n积分可以用来兑换商品、优惠券等。请问还有什么问题吗？"
    
    # 兑换相关
    elif any(keyword in msg for keyword in ["兑换", "商品", "优惠券"]):
        return "关于商品兑换：\n\n1. 纯积分兑换：使用积分直接兑换\n2. 积分+现金：积分抵扣部分金额\n3. 旧衣兑换：用旧衣直接兑换指定商品\n\n兑换商品支持包邮到家。\n\n您可以在积分商城查看可兑换的商品列表。请问还有什么问题吗？"
    
    # 订单相关
    elif any(keyword in msg for keyword in ["订单", "取消订单", "修改时间"]):
        return "关于订单问题：\n\n1. 取消订单：待接单、待上门状态可取消\n2. 调整时间：待接单、待上门状态可调整预约时间\n3. 订单状态：\n   - 待接单：等待系统派单\n   - 待上门：回收人员已接单\n   - 回收中：回收人员上门中\n   - 已完成：回收完成\n   - 已取消：订单已取消\n\n如需人工协助，请拨打客服热线：400-123-4567"
    
    # 客服热线
    elif any(keyword in msg for keyword in ["人工", "客服热线", "电话"]):
        return "如需人工客服协助，您可以：\n\n1. 拨打客服热线：400-123-4567\n   工作时间：9:00 - 21:00\n\n2. 发送邮件：support@recycle.com\n\n3. 关注公众号：旧衣回收助手\n\n感谢您的咨询！"
    
    # 默认回复
    else:
        return "感谢您的咨询！\n\n我是智能客服助手，您可以咨询以下问题：\n\n1. 旧衣回收流程\n2. 积分规则\n3. 商品兑换\n4. 订单问题\n5. 联系人工客服\n\n请输入相关关键词，我会为您解答。"


@router.get("/unread")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取未读消息总数
    """
    result = await db.execute(
        select(func.sum(ChatSession.unread_count)).where(
            ChatSession.user_id == current_user.id
        )
    )
    total = result.scalar() or 0
    
    return success(data={"unread_count": int(total)})


@router.post("/session/{session_id}/close")
async def close_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    结束会话
    """
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return error(code=404, message="会话不存在")
    
    session.status = 0  # 已结束
    await db.commit()
    
    return success(message="会话已结束")


@router.get("/faq")
async def get_faq():
    """
    获取常见问题列表
    """
    faq_list = [
        {
            "id": 1,
            "question": "旧衣回收需要收费吗？",
            "answer": "不需要，旧衣回收是完全免费的。您还可以通过回收旧衣获得积分奖励。"
        },
        {
            "id": 2,
            "question": "回收的旧衣会怎么处理？",
            "answer": "回收的旧衣会经过专业消毒处理，品质较好的会捐赠给需要的人，其他的会进行环保再生处理，制成保温材料、环保袋等。"
        },
        {
            "id": 3,
            "question": "积分有什么用？",
            "answer": "积分可以用来兑换商城商品、优惠券，也可以选择将积分捐赠给公益项目。"
        },
        {
            "id": 4,
            "question": "预约后可以取消吗？",
            "answer": "可以的。在订单状态为'待接单'或'待上门'时，您可以随时取消订单或调整预约时间。"
        },
        {
            "id": 5,
            "question": "回收人员什么时候上门？",
            "answer": "回收人员会在您预约的时间段内上门。预约成功后，系统会显示预计上门时段。如果需要调整时间，您可以在订单详情中修改。"
        }
    ]
    
    return success(data=faq_list)
