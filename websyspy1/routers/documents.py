"""
文档管理路由模块
提供文档的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Document, User
from schemas import DocumentCreate, DocumentUpdate, DocumentResponse, ApiResponse
from routers.auth import get_current_admin_user
from config import PAGE_SIZE

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def get_documents(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取文档列表接口（公开访问）
    支持分页、分类过滤、关键词搜索
    
    参数:
        page: 页码
        page_size: 每页数量
        category: 文档分类
        keyword: 搜索关键词
        db: 数据库会话
    
    返回:
        ApiResponse: 文档列表数据
    """
    # 构建查询，只查询启用的文档
    query = db.query(Document).filter(Document.is_active == True)
    
    # 分类过滤
    if category:
        query = query.filter(Document.category == category)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Document.title.contains(keyword)) |
            (Document.description.contains(keyword)) |
            (Document.tags.contains(keyword))
        )
    
    # 计算总数
    total = query.count()
    
    # 分页，按排序权重降序，创建时间降序
    offset = (page - 1) * page_size
    documents = query.order_by(
        Document.sort_order.desc(),
        Document.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 转换为响应模型
    doc_responses = [DocumentResponse.from_orm(doc) for doc in documents]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": doc_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{document_id}", response_model=ApiResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文档详情接口（公开访问）
    访问时会增加阅读次数
    
    参数:
        document_id: 文档ID
        db: 数据库会话
    
    返回:
        ApiResponse: 文档详情
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或已禁用"
        )
    
    # 增加阅读次数
    document.view_count += 1
    db.commit()
    db.refresh(document)
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"document": DocumentResponse.from_orm(document)}
    )


@router.post("/", response_model=ApiResponse)
def create_document(
    doc_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    创建文档接口（管理员专用）
    
    参数:
        doc_data: 文档数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 创建结果
    """
    new_doc = Document(
        title=doc_data.title,
        description=doc_data.description,
        content=doc_data.content,
        category=doc_data.category,
        tags=doc_data.tags,
        file_url=doc_data.file_url,
        sort_order=doc_data.sort_order or 0,
        is_active=True,
        view_count=0
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return ApiResponse(
        success=True,
        message="文档创建成功",
        data={"document": DocumentResponse.from_orm(new_doc)}
    )


@router.put("/{document_id}", response_model=ApiResponse)
def update_document(
    document_id: int,
    doc_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    更新文档接口（管理员专用）
    
    参数:
        document_id: 文档ID
        doc_data: 文档更新数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 更新结果
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 更新字段
    update_data = doc_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(document, key, value)
    
    db.commit()
    db.refresh(document)
    
    return ApiResponse(
        success=True,
        message="文档更新成功",
        data={"document": DocumentResponse.from_orm(document)}
    )


@router.delete("/{document_id}", response_model=ApiResponse)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    删除文档接口（管理员专用）
    
    参数:
        document_id: 文档ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 删除结果
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    db.delete(document)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="文档已删除"
    )


@router.put("/{document_id}/toggle-active", response_model=ApiResponse)
def toggle_document_active(
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换文档启用状态接口（管理员专用）
    
    参数:
        document_id: 文档ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    document.is_active = not document.is_active
    db.commit()
    db.refresh(document)
    
    return ApiResponse(
        success=True,
        message=f"文档已{'启用' if document.is_active else '禁用'}",
        data={"document": DocumentResponse.from_orm(document)}
    )
