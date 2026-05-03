from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models import EnvironmentData, Device
from app.schemas import EnvironmentDataCreate


class EnvironmentDataCRUD:
    """
    环境数据CRUD操作类
    封装环境数据相关的数据库操作
    """

    @staticmethod
    def get_by_id(db: Session, data_id: int) -> Optional[EnvironmentData]:
        """
        根据ID获取环境数据
        
        Args:
            db: 数据库会话
            data_id: 数据ID
            
        Returns:
            环境数据对象或None
        """
        return db.query(EnvironmentData).filter(EnvironmentData.id == data_id).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        device_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> tuple:
        """
        获取环境数据列表（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过条数
            limit: 获取条数
            device_id: 设备ID筛选
            start_time: 开始时间筛选
            end_time: 结束时间筛选
            
        Returns:
            tuple: (总数, 数据列表)
        """
        query = db.query(EnvironmentData)
        
        # 添加筛选条件
        if device_id:
            query = query.filter(EnvironmentData.device_id == device_id)
        if start_time:
            query = query.filter(EnvironmentData.recorded_at >= start_time)
        if end_time:
            query = query.filter(EnvironmentData.recorded_at <= end_time)
        
        # 获取总数
        total = query.count()
        
        # 分页查询（按时间倒序）
        data_list = query.order_by(desc(EnvironmentData.recorded_at)).offset(skip).limit(limit).all()
        
        return total, data_list

    @staticmethod
    def get_latest_by_device(db: Session, device_id: int) -> Optional[EnvironmentData]:
        """
        获取指定设备的最新环境数据
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            最新环境数据对象或None
        """
        return db.query(EnvironmentData).filter(
            EnvironmentData.device_id == device_id
        ).order_by(desc(EnvironmentData.recorded_at)).first()

    @staticmethod
    def create(db: Session, data_in: EnvironmentDataCreate) -> EnvironmentData:
        """
        创建环境数据记录
        
        Args:
            db: 数据库会话
            data_in: 环境数据创建数据
            
        Returns:
            创建的环境数据对象
        """
        db_data = EnvironmentData(
            device_id=data_in.device_id,
            temperature=data_in.temperature,
            humidity=data_in.humidity,
            light_intensity=data_in.light_intensity,
            soil_moisture=data_in.soil_moisture,
            co2_concentration=data_in.co2_concentration
        )
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data

    @staticmethod
    def batch_create(db: Session, data_list: List[EnvironmentDataCreate]) -> List[EnvironmentData]:
        """
        批量创建环境数据记录
        
        Args:
            db: 数据库会话
            data_list: 环境数据列表
            
        Returns:
            创建的环境数据对象列表
        """
        db_data_list = []
        for data_in in data_list:
            db_data = EnvironmentData(
                device_id=data_in.device_id,
                temperature=data_in.temperature,
                humidity=data_in.humidity,
                light_intensity=data_in.light_intensity,
                soil_moisture=data_in.soil_moisture,
                co2_concentration=data_in.co2_concentration
            )
            db_data_list.append(db_data)
            db.add(db_data)
        
        db.commit()
        for db_data in db_data_list:
            db.refresh(db_data)
        
        return db_data_list

    @staticmethod
    def get_statistics(
        db: Session,
        device_id: Optional[int] = None,
        hours: int = 24
    ) -> Dict:
        """
        获取环境数据统计信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID（可选，为None时统计所有设备）
            hours: 统计最近多少小时的数据
            
        Returns:
            统计结果字典
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        query = db.query(
            func.min(EnvironmentData.temperature).label('temp_min'),
            func.max(EnvironmentData.temperature).label('temp_max'),
            func.avg(EnvironmentData.temperature).label('temp_avg'),
            func.min(EnvironmentData.humidity).label('humidity_min'),
            func.max(EnvironmentData.humidity).label('humidity_max'),
            func.avg(EnvironmentData.humidity).label('humidity_avg'),
            func.min(EnvironmentData.light_intensity).label('light_min'),
            func.max(EnvironmentData.light_intensity).label('light_max'),
            func.avg(EnvironmentData.light_intensity).label('light_avg'),
            func.min(EnvironmentData.soil_moisture).label('soil_min'),
            func.max(EnvironmentData.soil_moisture).label('soil_max'),
            func.avg(EnvironmentData.soil_moisture).label('soil_avg'),
            func.min(EnvironmentData.co2_concentration).label('co2_min'),
            func.max(EnvironmentData.co2_concentration).label('co2_max'),
            func.avg(EnvironmentData.co2_concentration).label('co2_avg'),
            func.count(EnvironmentData.id).label('count')
        ).filter(EnvironmentData.recorded_at >= start_time)
        
        if device_id:
            query = query.filter(EnvironmentData.device_id == device_id)
        
        result = query.first()
        
        # 获取最新数据
        latest_query = db.query(EnvironmentData).filter(EnvironmentData.recorded_at >= start_time)
        if device_id:
            latest_query = latest_query.filter(EnvironmentData.device_id == device_id)
        latest = latest_query.order_by(desc(EnvironmentData.recorded_at)).first()
        
        return {
            'temperature': {
                'min': float(result.temp_min) if result.temp_min else None,
                'max': float(result.temp_max) if result.temp_max else None,
                'avg': float(result.temp_avg) if result.temp_avg else None,
                'latest': float(latest.temperature) if latest and latest.temperature else None
            },
            'humidity': {
                'min': float(result.humidity_min) if result.humidity_min else None,
                'max': float(result.humidity_max) if result.humidity_max else None,
                'avg': float(result.humidity_avg) if result.humidity_avg else None,
                'latest': float(latest.humidity) if latest and latest.humidity else None
            },
            'light_intensity': {
                'min': float(result.light_min) if result.light_min else None,
                'max': float(result.light_max) if result.light_max else None,
                'avg': float(result.light_avg) if result.light_avg else None,
                'latest': float(latest.light_intensity) if latest and latest.light_intensity else None
            },
            'soil_moisture': {
                'min': float(result.soil_min) if result.soil_min else None,
                'max': float(result.soil_max) if result.soil_max else None,
                'avg': float(result.soil_avg) if result.soil_avg else None,
                'latest': float(latest.soil_moisture) if latest and latest.soil_moisture else None
            },
            'co2_concentration': {
                'min': float(result.co2_min) if result.co2_min else None,
                'max': float(result.co2_max) if result.co2_max else None,
                'avg': float(result.co2_avg) if result.co2_avg else None,
                'latest': float(latest.co2_concentration) if latest and latest.co2_concentration else None
            },
            'count': result.count
        }

    @staticmethod
    def get_trend_data(
        db: Session,
        device_id: int,
        field: str,
        hours: int = 24
    ) -> List[Dict]:
        """
        获取趋势数据（用于图表展示）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            field: 数据字段（temperature, humidity, light_intensity, soil_moisture, co2_concentration）
            hours: 统计最近多少小时的数据
            
        Returns:
            趋势数据点列表
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        valid_fields = ['temperature', 'humidity', 'light_intensity', 'soil_moisture', 'co2_concentration']
        if field not in valid_fields:
            return []
        
        field_column = getattr(EnvironmentData, field)
        
        data = db.query(
            EnvironmentData.recorded_at,
            field_column
        ).filter(
            EnvironmentData.device_id == device_id,
            EnvironmentData.recorded_at >= start_time,
            field_column.isnot(None)
        ).order_by(EnvironmentData.recorded_at).all()
        
        return [
            {'time': d.recorded_at, 'value': float(getattr(d, field))}
            for d in data
        ]

    @staticmethod
    def delete(db: Session, data: EnvironmentData) -> EnvironmentData:
        """
        删除环境数据
        
        Args:
            db: 数据库会话
            data: 环境数据对象
            
        Returns:
            被删除的环境数据对象
        """
        db.delete(data)
        db.commit()
        return data
