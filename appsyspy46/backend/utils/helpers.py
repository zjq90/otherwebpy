import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from fastapi import UploadFile

from config import settings


def generate_order_no() -> str:
    """
    生成订单编号
    格式: RC + 年月日时分秒 + 6位随机数
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"RC{timestamp}{random_str}"


def calculate_distance(
    lat1: float, lon1: float, 
    lat2: float, lon2: float
) -> float:
    """
    计算两点之间的距离(Haversine公式)
    返回单位: 公里
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    
    return c * r


def optimize_route(
    points: List[dict],
    start_lat: Optional[float] = None,
    start_lon: Optional[float] = None
) -> Tuple[List[int], float, float]:
    """
    简单的路线规划算法(最近邻算法)
    返回: 优化后的订单ID顺序, 总距离(公里), 预计时间(分钟)
    """
    if not points:
        return [], 0.0, 0.0
    
    valid_points = [p for p in points if p.get("latitude") and p.get("longitude")]
    if not valid_points:
        return [p["order_id"] for p in points], 0.0, 0.0
    
    if start_lat is None or start_lon is None:
        current_point = valid_points[0]
        remaining = valid_points[1:]
    else:
        current_point = {"latitude": start_lat, "longitude": start_lon}
        remaining = valid_points.copy()
    
    optimized_order = []
    total_distance = 0.0
    
    while remaining:
        min_dist = float("inf")
        nearest_idx = 0
        
        for i, point in enumerate(remaining):
            dist = calculate_distance(
                current_point["latitude"], current_point["longitude"],
                point["latitude"], point["longitude"]
            )
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        total_distance += min_dist
        nearest_point = remaining.pop(nearest_idx)
        optimized_order.append(nearest_point["order_id"])
        current_point = nearest_point
    
    if start_lat is not None and start_lon is not None and len(optimized_order) > 0:
        first_idx = next((i for i, p in enumerate(points) if p["order_id"] == optimized_order[0]), 0)
        all_order = [p["order_id"] for p in points]
        result = optimized_order
    else:
        result = optimized_order
    
    estimated_duration = total_distance * 3.0
    
    return result, total_distance, estimated_duration


async def save_upload_file(file: UploadFile, sub_dir: str = "images") -> str:
    """
    保存上传的文件
    返回文件URL路径
    """
    upload_dir = os.path.join(settings.UPLOAD_DIR, sub_dir)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    new_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, new_filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return f"/uploads/{sub_dir}/{new_filename}"
