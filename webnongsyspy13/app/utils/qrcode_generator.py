"""
二维码生成工具模块
提供为农产品批次生成唯一二维码的功能
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import qrcode
from qrcode.image.pil import PilImage
from app.config import settings
from app import models, crud


def generate_qrcode_content(batch_number: str) -> str:
    """
    生成二维码内容（溯源URL）
    
    Args:
        batch_number: 批次编号
        
    Returns:
        二维码内容（URL格式）
    """
    # 构建溯源查询URL
    # 消费者扫码后将访问此URL查看溯源信息
    traceability_url = f"{settings.BASE_URL}/traceability/batch/{batch_number}"
    
    return traceability_url


def generate_qrcode_image(
    content: str,
    output_path: str,
    version: int = 1,
    error_correction: int = qrcode.constants.ERROR_CORRECT_M,
    box_size: int = 10,
    border: int = 4
) -> str:
    """
    生成二维码图片
    
    Args:
        content: 二维码内容
        output_path: 输出文件路径
        version: QR码版本（1-40）
        error_correction: 纠错级别
        box_size: 每个方块的像素大小
        border: 边框大小
        
    Returns:
        生成的图片路径
    """
    # 创建QR码生成器
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    
    # 添加数据
    qr.add_data(content)
    qr.make(fit=True)
    
    # 生成图片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存图片
    img.save(output_path)
    
    return output_path


def generate_qrcode_for_batch(
    db: Session,
    batch_id: int
) -> Optional[models.Batch]:
    """
    为指定批次生成二维码
    
    Args:
        db: 数据库会话
        batch_id: 批次ID
        
    Returns:
        更新后的批次对象，如果失败返回None
    """
    # 获取批次信息
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        return None
    
    # 生成二维码内容
    qrcode_content = generate_qrcode_content(batch.batch_number)
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"qrcode_{batch.batch_number}_{timestamp}_{unique_id}.png"
    
    # 构建输出路径
    output_path = os.path.join(settings.QRCODE_DIR, filename)
    
    # 生成二维码图片
    generate_qrcode_image(qrcode_content, output_path)
    
    # 更新批次的二维码信息
    update_data = {
        "qrcode_content": qrcode_content,
        "qrcode_path": f"/static/qrcodes/{filename}"
    }
    
    batch = crud.batch.update(db, db_obj=batch, obj_in=update_data)
    
    return batch


def regenerate_qrcode_for_batch(
    db: Session,
    batch_id: int
) -> Optional[models.Batch]:
    """
    为指定批次重新生成二维码
    用于URL变更或二维码损坏的情况
    
    Args:
        db: 数据库会话
        batch_id: 批次ID
        
    Returns:
        更新后的批次对象，如果失败返回None
    """
    # 获取批次信息
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        return None
    
    # 删除旧的二维码图片（如果存在）
    if batch.qrcode_path:
        # 转换URL路径为文件系统路径
        old_file_path = batch.qrcode_path.replace("/static/", "./static/")
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception:
                # 忽略删除错误
                pass
    
    # 生成新的二维码
    return generate_qrcode_for_batch(db, batch_id)


def get_qrcode_url(batch: models.Batch) -> Optional[str]:
    """
    获取批次的二维码图片访问URL
    
    Args:
        batch: 批次对象
        
    Returns:
        二维码图片URL，如果不存在返回None
    """
    if batch.qrcode_path:
        return f"{settings.BASE_URL}{batch.qrcode_path}"
    return None
