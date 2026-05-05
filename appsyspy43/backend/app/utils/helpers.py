"""
辅助函数模块
包含各种实用辅助函数，如任务编号生成、距离计算等
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal
from pathlib import Path
from fastapi import UploadFile

from app.config import settings


def generate_task_no() -> str:
    """
    生成运输任务编号
    格式：TASK + 年月日时分 + 4位随机数
    :return: 任务编号字符串
    """
    now = datetime.now()
    date_part = now.strftime("%Y%m%d%H%M")
    random_part = str(uuid.uuid4().int)[:4].zfill(4)
    return f"TASK{date_part}{random_part}"


def calculate_distance(
    lat1: Decimal,
    lon1: Decimal,
    lat2: Decimal,
    lon2: Decimal
) -> float:
    """
    使用Haversine公式计算两点之间的距离（单位：公里）
    :param lat1: 点1纬度
    :param lon1: 点1经度
    :param lat2: 点2纬度
    :param lon2: 点2经度
    :return: 距离（公里）
    """
    import math
    
    # 转换为弧度
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # 地球半径（公里）
    R = 6371.0
    
    # 计算差异
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Haversine公式
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_estimated_arrival(
    current_lat: Decimal,
    current_lon: Decimal,
    dest_lat: Decimal,
    dest_lon: Decimal,
    average_speed: float = 50.0  # 平均速度（公里/小时）
) -> Optional[datetime]:
    """
    计算预计到达时间
    :param current_lat: 当前纬度
    :param current_lon: 当前经度
    :param dest_lat: 目的地纬度
    :param dest_lon: 目的地经度
    :param average_speed: 平均速度（公里/小时），默认50公里/小时
    :return: 预计到达时间
    """
    if None in [current_lat, current_lon, dest_lat, dest_lon]:
        return None
    
    # 计算距离
    distance = calculate_distance(current_lat, current_lon, dest_lat, dest_lon)
    
    # 计算预计时间（小时）
    if average_speed <= 0:
        average_speed = 50.0
    hours_needed = distance / average_speed
    
    # 计算预计到达时间
    estimated_arrival = datetime.utcnow() + timedelta(hours=hours_needed)
    return estimated_arrival


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    格式化日期时间为字符串
    :param dt: 日期时间对象
    :return: 格式化后的字符串
    """
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def save_upload_file(
    file: UploadFile,
    subdirectory: str = "general"
) -> dict:
    """
    保存上传的文件
    :param file: 上传的文件对象
    :param subdirectory: 子目录名称
    :return: 包含文件信息的字典
    """
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_DIR) / subdirectory
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else uuid.uuid4().hex
    file_path = upload_dir / unique_filename
    
    # 读取并保存文件
    file_content = await file.read()
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 获取文件大小
    file_size = len(file_content)
    
    # 构建相对路径（用于URL访问）
    relative_path = f"/{settings.UPLOAD_DIR}/{subdirectory}/{unique_filename}"
    relative_path = relative_path.replace("\\", "/")
    
    return {
        "file_name": unique_filename,
        "original_name": file.filename,
        "file_path": str(file_path),
        "relative_path": relative_path,
        "file_size": file_size,
        "content_type": file.content_type,
    }


def get_file_url(relative_path: str, base_url: str = "") -> str:
    """
    获取文件的完整访问URL
    :param relative_path: 文件相对路径
    :param base_url: 基础URL
    :return: 完整的访问URL
    """
    if base_url:
        return f"{base_url.rstrip('/')}{relative_path}"
    return relative_path


def decimal_to_float(value: Optional[Decimal]) -> Optional[float]:
    """
    将Decimal转换为float
    :param value: Decimal值
    :return: float值
    """
    if value is None:
        return None
    return float(value)


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    解析字符串为日期时间
    :param value: 日期时间字符串
    :return: 日期时间对象
    """
    if value is None:
        return None
    
    # 尝试多种格式
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    
    return None
