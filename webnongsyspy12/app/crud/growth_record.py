from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models import GrowthRecord
from app.schemas import GrowthRecordCreate, GrowthRecordUpdate


class GrowthRecordCRUD:
    """
    生长记录CRUD操作类
    封装生长记录相关的数据库操作
    """

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[GrowthRecord]:
        """
        根据ID获取生长记录
        
        Args:
            db: 数据库会话
            record_id: 记录ID
            
        Returns:
            生长记录对象或None
        """
        return db.query(GrowthRecord).filter(GrowthRecord.id == record_id).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        crop_id: Optional[int] = None,
        record_type: Optional[str] = None,
        growth_stage: Optional[str] = None
    ) -> tuple:
        """
        获取生长记录列表（分页）
        
        Args:
            db: 数据库会话
            skip: 跳过条数
            limit: 获取条数
            crop_id: 作物ID筛选
            record_type: 记录类型筛选
            growth_stage: 生育期筛选
            
        Returns:
            tuple: (总数, 记录列表)
        """
        query = db.query(GrowthRecord)
        
        # 添加筛选条件
        if crop_id:
            query = query.filter(GrowthRecord.crop_id == crop_id)
        if record_type:
            query = query.filter(GrowthRecord.record_type == record_type)
        if growth_stage:
            query = query.filter(GrowthRecord.growth_stage == growth_stage)
        
        # 获取总数
        total = query.count()
        
        # 分页查询（按记录时间倒序）
        records = query.order_by(desc(GrowthRecord.recorded_at)).offset(skip).limit(limit).all()
        
        return total, records

    @staticmethod
    def create(db: Session, record_in: GrowthRecordCreate) -> GrowthRecord:
        """
        创建生长记录
        
        Args:
            db: 数据库会话
            record_in: 生长记录创建数据
            
        Returns:
            创建的生长记录对象
        """
        db_record = GrowthRecord(
            crop_id=record_in.crop_id,
            record_type=record_in.record_type,
            title=record_in.title,
            description=record_in.description,
            growth_stage=record_in.growth_stage,
            recorded_at=record_in.recorded_at or datetime.now()
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

    @staticmethod
    def update(db: Session, record: GrowthRecord, record_in: GrowthRecordUpdate) -> GrowthRecord:
        """
        更新生长记录
        
        Args:
            db: 数据库会话
            record: 原生长记录对象
            record_in: 更新数据
            
        Returns:
            更新后的生长记录对象
        """
        update_data = record_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(record, key, value)
        
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_with_file(
        db: Session,
        record: GrowthRecord,
        file_path: str,
        file_type: str
    ) -> GrowthRecord:
        """
        更新生长记录的文件信息
        
        Args:
            db: 数据库会话
            record: 生长记录对象
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            更新后的生长记录对象
        """
        record.file_path = file_path
        record.file_type = file_type
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_ai_diagnosis(
        db: Session,
        record: GrowthRecord,
        ai_diagnosis: str,
        disease_detected: Optional[str] = None,
        nutrition_status: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> GrowthRecord:
        """
        更新AI诊断结果
        
        Args:
            db: 数据库会话
            record: 生长记录对象
            ai_diagnosis: AI诊断结果文本
            disease_detected: 检测到的病害
            nutrition_status: 营养状况评估
            confidence: 诊断置信度
            
        Returns:
            更新后的生长记录对象
        """
        record.ai_diagnosis = ai_diagnosis
        record.disease_detected = disease_detected
        record.nutrition_status = nutrition_status
        record.diagnosis_confidence = confidence
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete(db: Session, record: GrowthRecord) -> GrowthRecord:
        """
        删除生长记录
        
        Args:
            db: 数据库会话
            record: 生长记录对象
            
        Returns:
            被删除的生长记录对象
        """
        db.delete(record)
        db.commit()
        return record

    @staticmethod
    def get_by_crop_and_stage(
        db: Session,
        crop_id: int,
        growth_stage: str
    ) -> List[GrowthRecord]:
        """
        获取指定作物在指定生育期的所有记录
        
        Args:
            db: 数据库会话
            crop_id: 作物ID
            growth_stage: 生育期
            
        Returns:
            生长记录列表
        """
        return db.query(GrowthRecord).filter(
            GrowthRecord.crop_id == crop_id,
            GrowthRecord.growth_stage == growth_stage
        ).order_by(GrowthRecord.recorded_at).all()

    @staticmethod
    def get_latest_by_crop(db: Session, crop_id: int, limit: int = 5) -> List[GrowthRecord]:
        """
        获取指定作物的最新生长记录
        
        Args:
            db: 数据库会话
            crop_id: 作物ID
            limit: 获取条数
            
        Returns:
            生长记录列表
        """
        return db.query(GrowthRecord).filter(
            GrowthRecord.crop_id == crop_id
        ).order_by(desc(GrowthRecord.recorded_at)).limit(limit).all()

    @staticmethod
    def get_statistics(db: Session, crop_id: Optional[int] = None) -> dict:
        """
        获取生长记录统计信息
        
        Args:
            db: 数据库会话
            crop_id: 可选的作物ID筛选
            
        Returns:
            统计结果字典
        """
        query = db.query(GrowthRecord)
        if crop_id:
            query = query.filter(GrowthRecord.crop_id == crop_id)
        
        # 统计各类型的记录数量
        type_stats = db.query(
            GrowthRecord.record_type,
            func.count(GrowthRecord.id).label('count')
        )
        if crop_id:
            type_stats = type_stats.filter(GrowthRecord.crop_id == crop_id)
        type_stats = type_stats.group_by(GrowthRecord.record_type).all()
        
        # 统计各生育期的记录数量
        stage_stats = db.query(
            GrowthRecord.growth_stage,
            func.count(GrowthRecord.id).label('count')
        )
        if crop_id:
            stage_stats = stage_stats.filter(GrowthRecord.crop_id == crop_id)
        stage_stats = stage_stats.filter(
            GrowthRecord.growth_stage.isnot(None)
        ).group_by(GrowthRecord.growth_stage).all()
        
        # 统计有病害检测的记录
        disease_count = db.query(GrowthRecord).filter(
            GrowthRecord.disease_detected.isnot(None)
        )
        if crop_id:
            disease_count = disease_count.filter(GrowthRecord.crop_id == crop_id)
        disease_count = disease_count.count()
        
        return {
            'total': query.count(),
            'by_type': {s.record_type: s.count for s in type_stats},
            'by_stage': {s.growth_stage: s.count for s in stage_stats},
            'disease_detected_count': disease_count
        }
