"""
体测记录相关CRUD操作模块
负责体测数据的增删改查和统计
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models import BodyMeasurement
from ..schemas import BodyMeasurementCreate, BodyMeasurementUpdate, BodyMeasurementStats


def get_measurement_by_id(db: Session, measurement_id: int) -> Optional[BodyMeasurement]:
    """
    根据ID获取体测记录
    """
    return db.query(BodyMeasurement).filter(BodyMeasurement.id == measurement_id).first()


def get_user_measurements(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[BodyMeasurement]:
    """
    获取用户的体测记录列表
    按测量日期倒序排列
    """
    return db.query(BodyMeasurement)\
        .filter(BodyMeasurement.user_id == user_id)\
        .order_by(BodyMeasurement.measurement_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def calculate_bmi(weight: float, height: float = 1.70) -> float:
    """
    计算BMI指数
    BMI = 体重(kg) / 身高(m)^2
    默认身高1.70m，实际项目中应该从用户信息获取
    """
    if height <= 0:
        return 0.0
    return round(weight / (height ** 2), 1)


def create_measurement(db: Session, user_id: int, measurement: BodyMeasurementCreate) -> BodyMeasurement:
    """
    创建新的体测记录
    自动计算BMI指数
    """
    # 计算BMI
    bmi = measurement.bmi
    if bmi is None:
        bmi = calculate_bmi(measurement.weight)
    
    db_measurement = BodyMeasurement(
        user_id=user_id,
        weight=measurement.weight,
        body_fat_rate=measurement.body_fat_rate,
        muscle_mass=measurement.muscle_mass,
        bmi=bmi,
        waist_circumference=measurement.waist_circumference,
        hip_circumference=measurement.hip_circumference,
        chest_circumference=measurement.chest_circumference,
        measurement_date=measurement.measurement_date or datetime.now(),
        source=measurement.source
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


def update_measurement(
    db: Session, 
    measurement_id: int, 
    measurement: BodyMeasurementUpdate
) -> Optional[BodyMeasurement]:
    """
    更新体测记录
    """
    db_measurement = get_measurement_by_id(db, measurement_id)
    if not db_measurement:
        return None
    
    # 更新非空字段
    update_data = measurement.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_measurement, key, value)
    
    db_measurement.updated_at = datetime.now()
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


def delete_measurement(db: Session, measurement_id: int) -> bool:
    """
    删除体测记录
    """
    db_measurement = get_measurement_by_id(db, measurement_id)
    if not db_measurement:
        return False
    
    db.delete(db_measurement)
    db.commit()
    return True


def get_measurement_stats(
    db: Session, 
    user_id: int, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 30
) -> BodyMeasurementStats:
    """
    获取用户体测数据统计
    用于折线图展示
    """
    query = db.query(BodyMeasurement)\
        .filter(BodyMeasurement.user_id == user_id)
    
    # 日期范围过滤
    if start_date:
        query = query.filter(BodyMeasurement.measurement_date >= start_date)
    if end_date:
        query = query.filter(BodyMeasurement.measurement_date <= end_date)
    
    # 按日期排序，限制数量
    measurements = query.order_by(BodyMeasurement.measurement_date.asc()).limit(limit).all()
    
    # 构建统计数据
    stats = BodyMeasurementStats()
    for m in measurements:
        stats.dates.append(m.measurement_date.strftime("%m-%d"))
        stats.weights.append(m.weight)
        stats.body_fat_rates.append(m.body_fat_rate)
        stats.muscle_masses.append(m.muscle_mass)
        stats.bmis.append(m.bmi if m.bmi else 0)
    
    return stats


def get_latest_measurement(db: Session, user_id: int) -> Optional[BodyMeasurement]:
    """
    获取用户最新的体测记录
    """
    return db.query(BodyMeasurement)\
        .filter(BodyMeasurement.user_id == user_id)\
        .order_by(BodyMeasurement.measurement_date.desc())\
        .first()
