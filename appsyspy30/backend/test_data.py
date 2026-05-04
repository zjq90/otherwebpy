"""
测试数据生成脚本
用于生成测试数据辅助功能测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, Post, Like, Comment, Share,
    Friendship, Message, Challenge, UserChallenge,
    Invitation, Achievement
)
from app.auth import get_password_hash
import random
import string


def generate_random_string(length: int = 10) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_random_phone() -> str:
    """生成随机手机号"""
    return '1' + ''.join(random.choices(string.digits, k=10))


def generate_invite_code(length: int = 8) -> str:
    """生成邀请码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_test_users(db: Session, count: int = 10) -> list:
    """创建测试用户"""
    users = []
    
    # 创建默认管理员账户
    admin_user = User(
        username="admin",
        email="admin@fitness.com",
        hashed_password=get_password_hash("admin123"),
        nickname="管理员",
        bio="健身社交系统管理员",
        phone="13800138000",
        points=9999,
        is_active=True
    )
    db.add(admin_user)
    users.append(admin_user)
    
    # 创建测试用户
    for i in range(1, count + 1):
        user = User(
            username=f"user{i}",
            email=f"user{i}@fitness.com",
            hashed_password=get_password_hash("123456"),
            nickname=f"健身达人{i}",
            bio=f"热爱健身，坚持运动{i}年",
            phone=generate_random_phone(),
            points=random.randint(100, 5000),
            is_active=True
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✓ 创建了 {len(users)} 个测试用户")
    print(f"  - 管理员: admin / admin123")
    print(f"  - 普通用户: user1~user{count} / 123456")
    return users


def create_test_posts(db: Session, users: list, count: int = 30) -> list:
    """创建测试动态"""
    posts = []
    post_types = ["training", "diet", "achievement"]
    post_contents = {
        "training": [
            "今天完成了5公里跑步，感觉很棒！",
            "健身房打卡，练了1小时力量训练",
            "晨跑打卡，天气真好",
            "今天练了腿，明天估计要酸爽了",
            "瑜伽练习，放松身心"
        ],
        "diet": [
            "健康午餐打卡，鸡胸肉沙拉",
            "早餐：燕麦粥+鸡蛋",
            "晚餐：清蒸鱼+蔬菜",
            "今日餐食记录，蛋白质充足",
            "健身餐打卡，低卡高蛋白"
        ],
        "achievement": [
            "终于完成了第一个半程马拉松！",
            "体重从80kg降到70kg，3个月的努力",
            "卧推突破100kg，开心！",
            "连续打卡30天，养成好习惯",
            "体脂率从25%降到18%，继续加油！"
        ]
    }
    
    for i in range(count):
        user = random.choice(users)
        post_type = random.choice(post_types)
        content = random.choice(post_contents[post_type])
        
        post = Post(
            user_id=user.id,
            content=content,
            post_type=post_type,
            images="",  # 暂时为空
            likes_count=random.randint(0, 50),
            comments_count=random.randint(0, 20),
            shares_count=random.randint(0, 10),
            is_public=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.add(post)
        posts.append(post)
    
    db.commit()
    print(f"✓ 创建了 {len(posts)} 条测试动态")
    return posts


def create_test_likes(db: Session, users: list, posts: list, count: int = 100) -> list:
    """创建测试点赞"""
    likes = []
    like_set = set()  # 避免重复点赞
    
    for _ in range(count):
        user = random.choice(users)
        post = random.choice(posts)
        
        # 检查是否已点赞
        key = (user.id, post.id)
        if key in like_set:
            continue
        
        like = Like(
            user_id=user.id,
            post_id=post.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.add(like)
        likes.append(like)
        like_set.add(key)
    
    db.commit()
    print(f"✓ 创建了 {len(likes)} 条测试点赞")
    return likes


def create_test_comments(db: Session, users: list, posts: list, count: int = 50) -> list:
    """创建测试评论"""
    comments = []
    comment_contents = [
        "太棒了！继续加油！",
        "向你学习！",
        "这个很有帮助",
        "我也在做这个",
        "效果如何？",
        "坚持就是胜利！",
        "恭喜恭喜！",
        "太厉害了！",
        "求教程",
        "一起加油！"
    ]
    
    for _ in range(count):
        user = random.choice(users)
        post = random.choice(posts)
        
        comment = Comment(
            user_id=user.id,
            post_id=post.id,
            content=random.choice(comment_contents),
            parent_id=None,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.add(comment)
        comments.append(comment)
    
    db.commit()
    print(f"✓ 创建了 {len(comments)} 条测试评论")
    return comments


def create_test_friendships(db: Session, users: list) -> list:
    """创建测试好友关系"""
    friendships = []
    friendship_set = set()
    
    # 为前5个用户创建好友关系
    for i in range(min(5, len(users))):
        for j in range(i + 1, min(8, len(users))):
            user1 = users[i]
            user2 = users[j]
            
            key = tuple(sorted([user1.id, user2.id]))
            if key in friendship_set:
                continue
            
            # 随机决定状态
            status = random.choice(["accepted", "accepted", "accepted", "pending"])
            
            friendship = Friendship(
                user_id_1=user1.id,
                user_id_2=user2.id,
                status=status,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            db.add(friendship)
            friendships.append(friendship)
            friendship_set.add(key)
    
    db.commit()
    print(f"✓ 创建了 {len(friendships)} 条测试好友关系")
    return friendships


def create_test_messages(db: Session, users: list, count: int = 30) -> list:
    """创建测试私信"""
    messages = []
    message_contents = [
        "嗨，最近健身怎么样？",
        "今天去健身房吗？",
        "有什么好的健身计划推荐吗？",
        "你用的什么蛋白粉？",
        "一起打卡吧！",
        "恭喜你完成挑战！",
        "你的训练计划能分享一下吗？",
        "最近体重变化如何？",
        "周末一起跑步吗？",
        "谢谢分享！"
    ]
    
    # 创建一些已接受的好友之间的对话
    accepted_friendships = db.query(Friendship).filter(
        Friendship.status == "accepted"
    ).all()
    
    for _ in range(count):
        if not accepted_friendships:
            break
            
        friendship = random.choice(accepted_friendships)
        
        # 随机决定谁发消息给谁
        if random.choice([True, False]):
            sender_id = friendship.user_id_1
            receiver_id = friendship.user_id_2
        else:
            sender_id = friendship.user_id_2
            receiver_id = friendship.user_id_1
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=random.choice(message_contents),
            is_read=random.choice([True, True, False]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 14))
        )
        db.add(message)
        messages.append(message)
    
    db.commit()
    print(f"✓ 创建了 {len(messages)} 条测试私信")
    return messages


def create_test_challenges(db: Session) -> list:
    """创建测试挑战活动"""
    challenges = []
    
    challenge_data = [
        {
            "title": "3周减脂挑战",
            "description": "连续21天坚持健康饮食和运动，目标体脂率下降3%。每日打卡记录饮食和运动情况。",
            "challenge_type": "fat_loss",
            "duration_days": 21,
            "reward_points": 500,
            "reward_description": "完成挑战可获得500积分及免费私教课一节"
        },
        {
            "title": "月度步数王",
            "description": "一个月内累计步数最多的用户获胜。每日步数自动记录，月底结算。",
            "challenge_type": "steps",
            "duration_days": 30,
            "reward_points": 800,
            "reward_description": "前三名可获得运动手环及积分奖励"
        },
        {
            "title": "力量突破计划",
            "description": "4周力量训练挑战，目标卧推/深蹲/硬拉重量提升10%。",
            "challenge_type": "strength",
            "duration_days": 28,
            "reward_points": 600,
            "reward_description": "完成者可获得专业力量训练指导"
        },
        {
            "title": "连续打卡30天",
            "description": "连续30天每日打卡，养成健身习惯。",
            "challenge_type": "habit",
            "duration_days": 30,
            "reward_points": 300,
            "reward_description": "坚持就是胜利！"
        }
    ]
    
    today = date.today()
    for i, data in enumerate(challenge_data):
        start_date = today - timedelta(days=random.randint(0, 7))
        end_date = start_date + timedelta(days=data["duration_days"])
        
        challenge = Challenge(
            title=data["title"],
            description=data["description"],
            challenge_type=data["challenge_type"],
            duration_days=data["duration_days"],
            start_date=start_date,
            end_date=end_date,
            reward_points=data["reward_points"],
            reward_description=data["reward_description"],
            max_participants=100,
            current_participants=random.randint(10, 50),
            is_active=True
        )
        db.add(challenge)
        challenges.append(challenge)
    
    db.commit()
    print(f"✓ 创建了 {len(challenges)} 个测试挑战活动")
    return challenges


def create_test_user_challenges(db: Session, users: list, challenges: list) -> list:
    """创建测试用户挑战参与记录"""
    user_challenges = []
    
    for user in users[:5]:  # 前5个用户参与挑战
        for challenge in challenges:
            # 随机决定是否参与
            if random.choice([True, False]):
                progress = random.uniform(0, 100)
                is_completed = progress >= 100
                
                user_challenge = UserChallenge(
                    user_id=user.id,
                    challenge_id=challenge.id,
                    progress=round(progress, 2),
                    daily_data='{"days": []}',
                    is_completed=is_completed,
                    reward_claimed=False,
                    joined_at=datetime.utcnow() - timedelta(days=random.randint(1, 14)),
                    completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)) if is_completed else None
                )
                db.add(user_challenge)
                user_challenges.append(user_challenge)
    
    db.commit()
    print(f"✓ 创建了 {len(user_challenges)} 条测试用户挑战参与记录")
    return user_challenges


def create_test_invitations(db: Session, users: list) -> list:
    """创建测试邀请记录"""
    invitations = []
    
    for user in users[:3]:  # 前3个用户发起邀请
        for _ in range(random.randint(2, 5)):
            status = random.choice(["pending", "registered", "subscribed", "rewarded"])
            
            invitee = None
            if status != "pending":
                # 随机选择一个被邀请者
                invitee = random.choice([u for u in users if u.id != user.id])
            
            invitation = Invitation(
                inviter_id=user.id,
                invitee_id=invitee.id if invitee else None,
                invite_code=generate_invite_code(),
                invitee_phone=generate_random_phone() if status == "pending" else None,
                invitee_email=f"{generate_random_string()}@test.com" if status == "pending" else None,
                status=status,
                reward_points=200,
                reward_description="邀请好友注册奖励",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(invitation)
            invitations.append(invitation)
    
    db.commit()
    print(f"✓ 创建了 {len(invitations)} 条测试邀请记录")
    return invitations


def create_test_achievements(db: Session, users: list) -> list:
    """创建测试成就"""
    achievements = []
    
    achievement_titles = [
        ("首次打卡", "完成第一次训练打卡", "milestone"),
        ("连续7天", "连续7天打卡", "streak"),
        ("月度之星", "本月活跃度排名第一", "achievement"),
        ("减脂达人", "成功减脂5kg", "fat_loss"),
        ("社交达人", "好友数达到10人", "social"),
        ("挑战王者", "完成5个挑战活动", "challenge")
    ]
    
    for user in users[:5]:
        for title, desc, atype in achievement_titles:
            if random.choice([True, False]):
                achievement = Achievement(
                    user_id=user.id,
                    title=title,
                    description=desc,
                    achievement_type=atype,
                    points_awarded=random.randint(50, 200),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.add(achievement)
                achievements.append(achievement)
    
    db.commit()
    print(f"✓ 创建了 {len(achievements)} 条测试成就")
    return achievements


def init_test_data():
    """初始化测试数据"""
    print("=" * 50)
    print("开始创建测试数据...")
    print("=" * 50)
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  数据库中已有数据，是否继续？")
            print("   继续会在现有数据基础上添加更多测试数据")
        
        # 创建测试数据
        users = create_test_users(db)
        posts = create_test_posts(db, users)
        create_test_likes(db, users, posts)
        create_test_comments(db, users, posts)
        create_test_friendships(db, users)
        create_test_messages(db, users)
        challenges = create_test_challenges(db)
        create_test_user_challenges(db, users, challenges)
        create_test_invitations(db, users)
        create_test_achievements(db, users)
        
        print("\n" + "=" * 50)
        print("测试数据创建完成！")
        print("=" * 50)
        print("\n测试账号信息：")
        print("  - 管理员账号: admin / admin123")
        print("  - 普通用户账号: user1~user10 / 123456")
        print("\nAPI文档地址: http://localhost:8000/api/v1/docs")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()
