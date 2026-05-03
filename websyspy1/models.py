"""
数据模型定义模块
定义所有数据库表结构和ORM映射关系
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """
    用户表
    存储系统用户信息，支持注册和登录功能
    """
    __tablename__ = "users"

    # 用户主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 用户名，唯一
    username = Column(String(50), unique=True, index=True, nullable=False)
    # 邮箱，唯一
    email = Column(String(100), unique=True, index=True, nullable=False)
    # 密码（哈希存储）
    hashed_password = Column(String(255), nullable=False)
    # 真实姓名
    full_name = Column(String(100), nullable=True)
    # 手机号
    phone = Column(String(20), nullable=True)
    # 是否激活
    is_active = Column(Boolean, default=True)
    # 是否管理员
    is_admin = Column(Boolean, default=False)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系定义：一个用户可以有多个秘钥申请
    key_applications = relationship("KeyApplication", back_populates="user")


class Product(Base):
    """
    产品表
    存储产品展示信息
    """
    __tablename__ = "products"

    # 产品主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 产品名称
    name = Column(String(100), nullable=False)
    # 产品简短描述
    short_desc = Column(String(500), nullable=True)
    # 产品详细描述
    description = Column(Text, nullable=True)
    # 产品图片URL
    image_url = Column(String(255), nullable=True)
    # 产品价格
    price = Column(String(50), nullable=True)
    # 产品分类
    category = Column(String(50), nullable=True)
    # 是否上架
    is_active = Column(Boolean, default=True)
    # 排序权重
    sort_order = Column(Integer, default=0)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Service(Base):
    """
    服务表
    存储服务介绍信息
    """
    __tablename__ = "services"

    # 服务主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 服务名称
    name = Column(String(100), nullable=False)
    # 服务简短描述
    short_desc = Column(String(500), nullable=True)
    # 服务详细描述
    description = Column(Text, nullable=True)
    # 服务图标
    icon = Column(String(100), nullable=True)
    # 服务图片URL
    image_url = Column(String(255), nullable=True)
    # 是否启用
    is_active = Column(Boolean, default=True)
    # 排序权重
    sort_order = Column(Integer, default=0)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Case(Base):
    """
    案例表
    存储案例展示信息
    """
    __tablename__ = "cases"

    # 案例主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 案例标题
    title = Column(String(200), nullable=False)
    # 案例简短描述
    short_desc = Column(String(500), nullable=True)
    # 案例详细描述
    description = Column(Text, nullable=True)
    # 案例详细内容
    content = Column(Text, nullable=True)
    # 案例封面图片
    image_url = Column(String(255), nullable=True)
    # 客户名称
    client = Column(String(100), nullable=True)
    # 案例分类
    category = Column(String(50), nullable=True)
    # 是否推荐
    is_featured = Column(Boolean, default=False)
    # 是否启用
    is_active = Column(Boolean, default=True)
    # 排序权重
    sort_order = Column(Integer, default=0)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Document(Base):
    """
    文档表
    存储文档中心的文档信息
    """
    __tablename__ = "documents"

    # 文档主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 文档标题
    title = Column(String(200), nullable=False)
    # 文档简短描述
    short_desc = Column(String(500), nullable=True)
    # 文档简介
    description = Column(Text, nullable=True)
    # 文档内容
    content = Column(Text, nullable=True)
    # 文档分类
    category = Column(String(50), nullable=True)
    # 文档标签（逗号分隔）
    tags = Column(String(500), nullable=True)
    # 文档附件URL
    file_url = Column(String(255), nullable=True)
    # 阅读次数
    view_count = Column(Integer, default=0)
    # 是否启用
    is_active = Column(Boolean, default=True)
    # 排序权重
    sort_order = Column(Integer, default=0)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class KeyApplication(Base):
    """
    秘钥申请表
    存储用户的秘钥申请信息
    """
    __tablename__ = "key_applications"

    # 申请主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 申请人用户ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 申请类型：trial(试用版), basic(基础版), pro(专业版), enterprise(企业版)
    application_type = Column(String(20), default="trial")
    # 公司名称
    company_name = Column(String(200), nullable=True)
    # 公司网站
    website = Column(String(255), nullable=True)
    # 使用场景说明
    use_case = Column(Text, nullable=False)
    # 预计API调用量
    expected_calls = Column(String(50), nullable=True)
    # 申请状态：pending(待审核), approved(已通过), rejected(已拒绝)
    status = Column(String(20), default="pending")
    # 生成的秘钥
    api_key = Column(String(64), nullable=True)
    # 秘钥有效期
    valid_until = Column(DateTime, nullable=True)
    # 审核备注
    review_notes = Column(Text, nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系定义：关联用户
    user = relationship("User", back_populates="key_applications")
