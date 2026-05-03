"""
CRUD操作模块
包含所有数据库的增删改查操作
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from passlib.context import CryptContext
import models
import schemas
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== 工具函数 ====================

def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密
    bcrypt有72字节限制，需要截断长密码
    """
    # bcrypt只支持最多72字节，UTF-8编码后截断
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    bcrypt有72字节限制，需要截断长密码
    """
    # bcrypt只支持最多72字节，UTF-8编码后截断
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)


def get_pagination_params(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> tuple:
    """
    处理分页参数
    """
    page = max(1, page)
    page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    return page, page_size


# ==================== 用户CRUD ====================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    根据ID获取用户
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    根据用户名获取用户
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE, 
              keyword: str = None) -> tuple:
    """
    获取用户列表（分页）
    """
    page, page_size = get_pagination_params(page, page_size)
    query = db.query(models.User)
    
    if keyword:
        query = query.filter(
            models.User.username.contains(keyword) |
            models.User.real_name.contains(keyword)
        )
    
    total = query.count()
    users = query.order_by(models.User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return users, total


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    创建用户
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate) -> Optional[models.User]:
    """
    更新用户信息
    """
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
    """
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# ==================== 分类CRUD ====================

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """
    根据ID获取分类
    """
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_categories(db: Session, parent_id: int = None, is_active: bool = None) -> List[models.Category]:
    """
    获取分类列表
    """
    query = db.query(models.Category)
    
    if parent_id is not None:
        query = query.filter(models.Category.parent_id == parent_id)
    if is_active is not None:
        query = query.filter(models.Category.is_active == is_active)
    
    return query.order_by(models.Category.sort_order, models.Category.id).all()


def get_all_categories(db: Session) -> List[models.Category]:
    """
    获取所有分类
    """
    return db.query(models.Category).order_by(
        models.Category.sort_order, 
        models.Category.id
    ).all()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """
    创建分类
    """
    db_category = models.Category(
        name=category.name,
        parent_id=category.parent_id,
        description=category.description,
        sort_order=category.sort_order
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, 
                    category_data: schemas.CategoryUpdate) -> Optional[models.Category]:
    """
    更新分类
    """
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """
    删除分类
    """
    db_category = get_category(db, category_id)
    if db_category:
        # 检查是否有子分类
        child_count = db.query(models.Category).filter(
            models.Category.parent_id == category_id
        ).count()
        if child_count > 0:
            return False
        # 检查是否有产品关联
        product_count = db.query(models.Product).filter(
            models.Product.category_id == category_id
        ).count()
        if product_count > 0:
            return False
        db.delete(db_category)
        db.commit()
        return True
    return False


# ==================== 产品CRUD ====================

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    根据ID获取产品
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_code(db: Session, code: str) -> Optional[models.Product]:
    """
    根据产品编码获取产品
    """
    return db.query(models.Product).filter(models.Product.code == code).first()


def get_products(db: Session, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                 keyword: str = None, category_id: int = None, 
                 status: int = None) -> tuple:
    """
    获取产品列表（分页）
    """
    page, page_size = get_pagination_params(page, page_size)
    query = db.query(models.Product)
    
    if keyword:
        query = query.filter(
            models.Product.name.contains(keyword) |
            models.Product.code.contains(keyword)
        )
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if status is not None:
        query = query.filter(models.Product.status == status)
    
    total = query.count()
    products = query.order_by(models.Product.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return products, total


def get_products_for_export(db: Session, keyword: str = None, 
                             category_id: int = None) -> List[models.Product]:
    """
    获取产品列表（用于导出Excel）
    """
    query = db.query(models.Product)
    
    if keyword:
        query = query.filter(
            models.Product.name.contains(keyword) |
            models.Product.code.contains(keyword)
        )
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    return query.order_by(models.Product.created_at.desc()).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """
    创建产品
    """
    db_product = models.Product(
        name=product.name,
        code=product.code,
        category_id=product.category_id,
        description=product.description,
        specification=product.specification,
        unit=product.unit,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        stock_quantity=product.stock_quantity,
        min_stock=product.min_stock,
        max_stock=product.max_stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, 
                   product_data: schemas.ProductUpdate) -> Optional[models.Product]:
    """
    更新产品
    """
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def update_product_image(db: Session, product_id: int, image_path: str) -> Optional[models.Product]:
    """
    更新产品图片
    """
    db_product = get_product(db, product_id)
    if db_product:
        db_product.image = image_path
        db.commit()
        db.refresh(db_product)
    return db_product


def toggle_product_status(db: Session, product_id: int) -> Optional[models.Product]:
    """
    切换产品上下架状态
    """
    db_product = get_product(db, product_id)
    if db_product:
        db_product.status = 0 if db_product.status == 1 else 1
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """
    删除产品
    """
    db_product = get_product(db, product_id)
    if db_product:
        # 检查是否有进销存记录
        record_count = db.query(models.InventoryRecord).filter(
            models.InventoryRecord.product_id == product_id
        ).count()
        if record_count > 0:
            return False
        db.delete(db_product)
        db.commit()
        return True
    return False


# ==================== 进销存记录CRUD ====================

def get_inventory_record(db: Session, record_id: int) -> Optional[models.InventoryRecord]:
    """
    根据ID获取进销存记录
    """
    return db.query(models.InventoryRecord).filter(
        models.InventoryRecord.id == record_id
    ).first()


def get_inventory_records(db: Session, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                           product_id: int = None, record_type: str = None,
                           start_date: date = None, end_date: date = None) -> tuple:
    """
    获取进销存记录列表（分页）
    """
    page, page_size = get_pagination_params(page, page_size)
    query = db.query(models.InventoryRecord)
    
    if product_id:
        query = query.filter(models.InventoryRecord.product_id == product_id)
    if record_type:
        query = query.filter(models.InventoryRecord.record_type == record_type)
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(models.InventoryRecord.created_at >= start_datetime)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(models.InventoryRecord.created_at <= end_datetime)
    
    total = query.count()
    records = query.order_by(models.InventoryRecord.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return records, total


def create_inventory_record(db: Session, record: schemas.InventoryRecordCreate) -> Optional[models.InventoryRecord]:
    """
    创建进销存记录（同时更新库存）
    """
    # 检查产品是否存在
    db_product = get_product(db, record.product_id)
    if not db_product:
        return None
    
    # 计算总金额
    total_amount = record.quantity * record.unit_price
    
    # 创建记录
    db_record = models.InventoryRecord(
        product_id=record.product_id,
        record_type=record.record_type,
        quantity=record.quantity,
        unit_price=record.unit_price,
        total_amount=total_amount,
        operator_id=record.operator_id,
        remark=record.remark,
        reference_no=record.reference_no
    )
    
    # 更新库存
    if record.record_type == "in":
        # 入库：增加库存
        db_product.stock_quantity += record.quantity
    elif record.record_type == "out":
        # 出库：减少库存
        if db_product.stock_quantity < record.quantity:
            return None  # 库存不足
        db_product.stock_quantity -= record.quantity
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# ==================== 数据看板统计 ====================

def get_dashboard_stats(db: Session) -> dict:
    """
    获取数据看板统计数据
    """
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # 产品总数
    total_products = db.query(models.Product).count()
    
    # 分类总数
    total_categories = db.query(models.Category).count()
    
    # 用户总数
    total_users = db.query(models.User).count()
    
    # 库存总价值
    total_stock_value = db.query(
        func.sum(models.Product.stock_quantity * models.Product.cost_price)
    ).scalar() or 0
    
    # 低库存产品数
    low_stock_count = db.query(models.Product).filter(
        models.Product.stock_quantity <= models.Product.min_stock
    ).count()
    
    # 今日入库统计
    today_in_records = db.query(models.InventoryRecord).filter(
        models.InventoryRecord.record_type == "in",
        models.InventoryRecord.created_at >= today_start,
        models.InventoryRecord.created_at <= today_end
    ).all()
    
    today_in_count = sum(r.quantity for r in today_in_records)
    today_in_amount = sum(r.total_amount for r in today_in_records)
    
    # 今日出库统计
    today_out_records = db.query(models.InventoryRecord).filter(
        models.InventoryRecord.record_type == "out",
        models.InventoryRecord.created_at >= today_start,
        models.InventoryRecord.created_at <= today_end
    ).all()
    
    today_out_count = sum(r.quantity for r in today_out_records)
    today_out_amount = sum(r.total_amount for r in today_out_records)
    
    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_users": total_users,
        "total_stock_value": float(total_stock_value),
        "low_stock_count": low_stock_count,
        "today_in_count": today_in_count,
        "today_out_count": today_out_count,
        "today_in_amount": float(today_in_amount),
        "today_out_amount": float(today_out_amount)
    }
