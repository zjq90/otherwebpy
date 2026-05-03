"""
门禁设备管理API路由
提供设备的增删改查功能
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models.device import Device

router = APIRouter(prefix="/api/device", tags=["门禁设备管理"])


class DeviceCreateRequest(BaseModel):
    """
    设备创建请求模型
    """
    device_no: str
    device_name: str
    device_model: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None


class DeviceUpdateRequest(BaseModel):
    """
    设备更新请求模型
    """
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


@router.get("/list")
def get_device_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备列表
    支持分页、关键字搜索、位置筛选、状态筛选
    """
    query = db.query(Device)
    
    # 关键字搜索（设备编号、设备名称、IP地址）
    if keyword:
        query = query.filter(
            or_(
                Device.device_no.contains(keyword),
                Device.device_name.contains(keyword),
                Device.ip_address.contains(keyword)
            )
        )
    
    # 位置筛选
    if location:
        query = query.filter(Device.location.contains(location))
    
    # 状态筛选
    if status is not None:
        query = query.filter(Device.status == status)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    device_list = query.order_by(Device.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": [device.to_dict() for device in device_list],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/all")
def get_all_devices(db: Session = Depends(get_db)):
    """
    获取所有设备（下拉选择用）
    """
    devices = db.query(Device).filter(Device.status == 1).all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{"id": d.id, "device_no": d.device_no, "device_name": d.device_name, "location": d.location} for d in devices]
    }


@router.get("/{device_id}")
def get_device_detail(device_id: int, db: Session = Depends(get_db)):
    """
    获取设备详情
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": device.to_dict()
    }


@router.post("/create")
def create_device(
    request: DeviceCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建设备
    """
    # 检查设备编号是否已存在
    existing = db.query(Device).filter(Device.device_no == request.device_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备编号已存在")
    
    # 创建设备
    device = Device(
        device_no=request.device_no,
        device_name=request.device_name,
        device_model=request.device_model,
        location=request.location,
        ip_address=request.ip_address,
        mac_address=request.mac_address,
        status=request.status,
        last_online_time=datetime.now() if request.status == 1 else None,
        remark=request.remark
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": device.to_dict()
    }


@router.put("/{device_id}")
def update_device(
    device_id: int,
    request: DeviceUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(device, key, value)
    
    # 如果状态变为在线，更新最后在线时间
    if request.status == 1:
        device.last_online_time = datetime.now()
    
    db.commit()
    db.refresh(device)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": device.to_dict()
    }


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """
    删除设备
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db.delete(device)
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.post("/heartbeat/{device_no}")
def device_heartbeat(device_no: str, db: Session = Depends(get_db)):
    """
    设备心跳接口
    设备定期调用此接口更新在线状态
    """
    device = db.query(Device).filter(Device.device_no == device_no).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新状态为在线，并更新最后在线时间
    device.status = 1
    device.last_online_time = datetime.now()
    db.commit()
    
    return {
        "code": 200,
        "message": "心跳更新成功"
    }


@router.get("/locations/all")
def get_all_locations(db: Session = Depends(get_db)):
    """
    获取所有设备位置列表
    """
    locations = db.query(Device.location).filter(
        Device.location.isnot(None),
        Device.location != ""
    ).distinct().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [l[0] for l in locations]
    }
