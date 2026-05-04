"""
数据模型模块
定义所有数据库表结构
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    用户表
    存储会员基本信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    bio = Column(Text, nullable=True, comment="个人简介")
    phone = Column(String(20), nullable=True, comment="手机号")
    points = Column(Integer, default=0, comment="积分余额")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    friendships_as_user1 = relationship("Friendship", foreign_keys="Friendship.user_id_1", back_populates="user1")
    friendships_as_user2 = relationship("Friendship", foreign_keys="Friendship.user_id_2", back_populates="user2")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    user_challenges = relationship("UserChallenge", back_populates="user", cascade="all, delete-orphan")
    sent_invitations = relationship("Invitation", foreign_keys="Invitation.inviter_id", back_populates="inviter")
    received_invitations = relationship("Invitation", foreign_keys="Invitation.invitee_id", back_populates="invitee")


class Post(Base):
    """
    动态表
    存储用户发布的训练照片、饮食打卡、成果对比等内容
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, comment="动态ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发布者ID")
    content = Column(Text, nullable=False, comment="动态内容")
    post_type = Column(String(20), nullable=False, default="training", comment="动态类型: training(训练), diet(饮食), achievement(成果)")
    images = Column(Text, nullable=True, comment="图片URL列表(逗号分隔)")
    likes_count = Column(Integer, default=0, comment="点赞数")
    comments_count = Column(Integer, default=0, comment="评论数")
    shares_count = Column(Integer, default=0, comment="分享数")
    is_public = Column(Boolean, default=True, comment="是否公开")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Like(Base):
    """
    点赞表
    存储用户对动态的点赞记录
    """
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True, comment="点赞ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="点赞用户ID")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="被点赞动态ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="点赞时间")

    # 关系定义
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Comment(Base):
    """
    评论表
    存储用户对动态的评论
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, comment="评论ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评论用户ID")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="被评论动态ID")
    content = Column(Text, nullable=False, comment="评论内容")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, comment="父评论ID(用于回复)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="评论时间")

    # 关系定义
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Share(Base):
    """
    分享表
    存储用户对动态的分享记录
    """
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True, comment="分享ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="分享用户ID")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="被分享动态ID")
    share_platform = Column(String(20), nullable=True, comment="分享平台")
    created_at = Column(DateTime, default=datetime.utcnow, comment="分享时间")


class Friendship(Base):
    """
    好友关系表
    存储用户之间的好友关系
    """
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True, comment="好友关系ID")
    user_id_1 = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户1ID")
    user_id_2 = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户2ID")
    status = Column(String(20), default="pending", comment="关系状态: pending(待确认), accepted(已接受), rejected(已拒绝), blocked(已拉黑)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user1 = relationship("User", foreign_keys=[user_id_1], back_populates="friendships_as_user1")
    user2 = relationship("User", foreign_keys=[user_id_2], back_populates="friendships_as_user2")


class Message(Base):
    """
    私信表
    存储用户之间的私信记录
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, comment="私信ID")
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收者ID")
    content = Column(Text, nullable=False, comment="消息内容")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.utcnow, comment="发送时间")

    # 关系定义
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class Challenge(Base):
    """
    挑战活动表
    存储平台发起的挑战活动信息
    """
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True, comment="挑战活动ID")
    title = Column(String(100), nullable=False, comment="活动标题")
    description = Column(Text, nullable=False, comment="活动描述")
    challenge_type = Column(String(50), nullable=False, comment="挑战类型: fat_loss(减脂), steps(步数), strength(力量)等")
    duration_days = Column(Integer, nullable=False, comment="活动持续天数")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    reward_points = Column(Integer, default=0, comment="奖励积分")
    reward_description = Column(Text, nullable=True, comment="奖励描述(实物奖励等)")
    max_participants = Column(Integer, nullable=True, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前参与人数")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user_challenges = relationship("UserChallenge", back_populates="challenge", cascade="all, delete-orphan")


class UserChallenge(Base):
    """
    用户挑战参与表
    存储用户参与挑战活动的记录和进度
    """
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True, comment="用户挑战ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, comment="挑战活动ID")
    progress = Column(Float, default=0.0, comment="完成进度(百分比)")
    daily_data = Column(Text, nullable=True, comment="每日数据(JSON格式)")
    is_completed = Column(Boolean, default=False, comment="是否完成")
    reward_claimed = Column(Boolean, default=False, comment="奖励是否已领取")
    joined_at = Column(DateTime, default=datetime.utcnow, comment="参与时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系定义
    user = relationship("User", back_populates="user_challenges")
    challenge = relationship("Challenge", back_populates="user_challenges")


class Invitation(Base):
    """
    邀请记录表
    存储用户邀请好友的记录
    """
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True, comment="邀请记录ID")
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="邀请者ID")
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="被邀请者ID(注册后填充)")
    invite_code = Column(String(20), unique=True, index=True, nullable=False, comment="邀请码")
    invitee_phone = Column(String(20), nullable=True, comment="被邀请者手机号")
    invitee_email = Column(String(100), nullable=True, comment="被邀请者邮箱")
    status = Column(String(20), default="pending", comment="邀请状态: pending(待接受), registered(已注册), subscribed(已办卡), rewarded(已奖励)")
    reward_points = Column(Integer, default=0, comment="奖励积分")
    reward_description = Column(Text, nullable=True, comment="奖励描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="sent_invitations")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="received_invitations")


class Achievement(Base):
    """
    成就表
    存储用户获得的成就
    """
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True, comment="成就ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(100), nullable=False, comment="成就标题")
    description = Column(Text, nullable=True, comment="成就描述")
    achievement_type = Column(String(50), nullable=False, comment="成就类型")
    icon = Column(String(255), nullable=True, comment="成就图标")
    points_awarded = Column(Integer, default=0, comment="奖励积分")
    created_at = Column(DateTime, default=datetime.utcnow, comment="获得时间")
