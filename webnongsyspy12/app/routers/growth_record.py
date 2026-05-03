import os
import uuid
import shutil
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import (
    GrowthRecordCreate, GrowthRecordUpdate, GrowthRecordResponse,
    ApiResponse, ApiListResponse
)
from app.crud import GrowthRecordCRUD, CropCRUD

router = APIRouter(prefix="/growth-records", tags=["生长记录"])


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov'}

# 最大文件大小：50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


def save_upload_file(upload_file: UploadFile, record_type: str) -> tuple:
    """
    保存上传的文件
    
    Args:
        upload_file: 上传的文件对象
        record_type: 记录类型（image/video）
    
    Returns:
        tuple: (文件相对路径, 文件类型)
    """
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名为空"
        )
    
    # 获取文件扩展名
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    if not file_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法确定文件扩展名"
        )
    
    # 验证文件类型
    if record_type == "image" and file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式，支持的格式: {ALLOWED_IMAGE_EXTENSIONS}"
        )
    elif record_type == "video" and file_ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的视频格式，支持的格式: {ALLOWED_VIDEO_EXTENSIONS}"
        )
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # 确定保存目录
    if record_type == "image":
        save_dir = os.path.join(settings.UPLOAD_DIR, "images")
        relative_path = f"/uploads/images/{unique_filename}"
    else:
        save_dir = os.path.join(settings.UPLOAD_DIR, "videos")
        relative_path = f"/uploads/videos/{unique_filename}"
    
    # 确保目录存在
    try:
        os.makedirs(save_dir, exist_ok=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法创建保存目录: {str(e)}"
        )
    
    # 保存文件
    file_path = os.path.join(save_dir, unique_filename)
    total_size = 0
    
    try:
        # 使用分块读取的方式保存文件，避免大文件问题
        with open(file_path, "wb") as buffer:
            while True:
                chunk = upload_file.file.read(8192)  # 每次读取 8KB
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）"
                    )
                buffer.write(chunk)
        
        if total_size == 0:
            # 删除空文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件内容为空"
            )
    
    except HTTPException:
        # 删除已创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise
    except Exception as e:
        # 删除已创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 处理 content_type 可能为 None 的情况
    content_type = upload_file.content_type
    if not content_type:
        # 根据扩展名推断 content_type
        ext_to_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime'
        }
        content_type = ext_to_type.get(file_ext, 'application/octet-stream')
    
    return relative_path, content_type


def simulate_ai_diagnosis() -> dict:
    """
    模拟AI图像识别诊断
    实际项目中应该调用真实的AI服务
    
    Returns:
        模拟的诊断结果
    """
    import random
    
    # 模拟的病害类型
    diseases = [
        None, None, None,  # 大部分情况是健康的
        "白粉病",
        "叶斑病",
        "霜霉病",
        "炭疽病",
        "病毒病"
    ]
    
    # 营养状况
    nutrition_statuses = [
        "营养充足",
        "营养充足",
        "氮肥稍缺",
        "磷肥稍缺",
        "钾肥稍缺"
    ]
    
    disease = random.choice(diseases)
    nutrition = random.choice(nutrition_statuses)
    confidence = round(random.uniform(0.75, 0.98), 2)
    
    # 生成诊断描述
    if disease:
        diagnosis = f"AI图像识别检测到作物叶片存在{disease}症状，建议及时采取防治措施。"
    else:
        diagnosis = "AI图像识别未检测到明显病害症状，作物生长状态良好。"
    
    diagnosis += f" 营养状况评估：{nutrition}。"
    
    return {
        "ai_diagnosis": diagnosis,
        "disease_detected": disease,
        "nutrition_status": nutrition,
        "diagnosis_confidence": confidence
    }


@router.get("", response_model=ApiListResponse)
def get_growth_records(
    skip: int = 0,
    limit: int = 100,
    crop_id: Optional[int] = None,
    record_type: Optional[str] = None,
    growth_stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取生长记录列表（支持分页和筛选）
    
    Args:
        skip: 跳过条数
        limit: 获取条数
        crop_id: 作物ID筛选
        record_type: 记录类型筛选
        growth_stage: 生育期筛选
        db: 数据库会话
    
    Returns:
        生长记录列表
    """
    total, records = GrowthRecordCRUD.get_list(
        db, skip=skip, limit=limit,
        crop_id=crop_id,
        record_type=record_type,
        growth_stage=growth_stage
    )
    
    return ApiListResponse(
        success=True,
        message="获取生长记录列表成功",
        total=total,
        data=[GrowthRecordResponse.model_validate(record) for record in records]
    )


@router.get("/statistics", response_model=ApiResponse)
def get_growth_record_statistics(
    crop_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取生长记录统计信息
    
    Args:
        crop_id: 可选的作物ID筛选
        db: 数据库会话
    
    Returns:
        统计信息
    """
    # 如果指定了crop_id，检查作物是否存在
    if crop_id:
        crop = CropCRUD.get_by_id(db, crop_id)
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"作物ID {crop_id} 不存在"
            )
    
    statistics = GrowthRecordCRUD.get_statistics(db, crop_id=crop_id)
    
    return ApiResponse(
        success=True,
        message="获取统计信息成功",
        data=statistics
    )


@router.get("/latest/{crop_id}", response_model=ApiListResponse)
def get_latest_records(
    crop_id: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    获取指定作物的最新生长记录
    
    Args:
        crop_id: 作物ID
        limit: 获取条数
        db: 数据库会话
    
    Returns:
        生长记录列表
    """
    # 检查作物是否存在
    crop = CropCRUD.get_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"作物ID {crop_id} 不存在"
        )
    
    records = GrowthRecordCRUD.get_latest_by_crop(db, crop_id=crop_id, limit=limit)
    
    return ApiListResponse(
        success=True,
        message="获取最新记录成功",
        total=len(records),
        data=[GrowthRecordResponse.model_validate(record) for record in records]
    )


@router.get("/{record_id}", response_model=ApiResponse)
def get_growth_record(record_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生长记录详情
    
    Args:
        record_id: 记录ID
        db: 数据库会话
    
    Returns:
        生长记录详情
    """
    record = GrowthRecordCRUD.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"生长记录ID {record_id} 不存在"
        )
    
    return ApiResponse(
        success=True,
        message="获取生长记录详情成功",
        data=GrowthRecordResponse.model_validate(record).model_dump()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_growth_record(
    crop_id: int = Form(...),
    record_type: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    growth_stage: Optional[str] = Form(None),
    recorded_at: Optional[datetime] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    创建生长记录（支持上传图片/视频文件）
    
    Args:
        crop_id: 作物ID
        record_type: 记录类型（image/video/text）
        title: 记录标题
        description: 详细描述
        growth_stage: 生育期
        recorded_at: 记录时间（可选，默认为当前时间）
        file: 上传的文件（图片或视频）
        db: 数据库会话
    
    Returns:
        创建的生长记录
    """
    try:
        # 检查作物是否存在
        crop = CropCRUD.get_by_id(db, crop_id)
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"作物ID {crop_id} 不存在"
            )
        
        # 验证记录类型
        valid_types = ["image", "video", "text"]
        if record_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的记录类型，有效类型: {valid_types}"
            )
        
        # 如果是图片或视频类型但没有文件，给出警告
        if record_type in ["image", "video"] and not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"选择了{record_type}类型，但未上传文件"
            )
        
        # 创建记录数据
        record_in = GrowthRecordCreate(
            crop_id=crop_id,
            record_type=record_type,
            title=title,
            description=description,
            growth_stage=growth_stage,
            recorded_at=recorded_at
        )
        
        # 创建记录
        record = GrowthRecordCRUD.create(db, record_in)
        
        # 保存上传的文件（如果有）
        if file and record_type in ["image", "video"]:
            try:
                file_path, file_type = save_upload_file(file, record_type)
                GrowthRecordCRUD.update_with_file(db, record, file_path, file_type)
            except HTTPException:
                # 如果文件保存失败，删除已创建的记录并重新抛出
                GrowthRecordCRUD.delete(db, record)
                raise
            except Exception as e:
                GrowthRecordCRUD.delete(db, record)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"文件保存失败: {str(e)}"
                )
            
            # 模拟AI图像识别诊断（仅对图片类型）
            if record_type == "image":
                diagnosis_result = simulate_ai_diagnosis()
                GrowthRecordCRUD.update_ai_diagnosis(
                    db, record,
                    ai_diagnosis=diagnosis_result["ai_diagnosis"],
                    disease_detected=diagnosis_result["disease_detected"],
                    nutrition_status=diagnosis_result["nutrition_status"],
                    confidence=diagnosis_result["diagnosis_confidence"]
                )
        
        # 刷新记录获取最新数据
        db.refresh(record)
        
        return ApiResponse(
            success=True,
            message="创建生长记录成功",
            data=GrowthRecordResponse.model_validate(record).model_dump()
        )
    
    except HTTPException:
        # 重新抛出 HTTPException
        raise
    except Exception as e:
        # 捕获其他异常，返回 500 错误
        import traceback
        print(f"[ERROR] create_growth_record: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建记录失败: {str(e)}"
        )


@router.put("/{record_id}", response_model=ApiResponse)
def update_growth_record(
    record_id: int,
    record_in: GrowthRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新生长记录信息
    
    Args:
        record_id: 记录ID
        record_in: 更新数据
        db: 数据库会话
    
    Returns:
        更新后的生长记录
    """
    record = GrowthRecordCRUD.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"生长记录ID {record_id} 不存在"
        )
    
    updated_record = GrowthRecordCRUD.update(db, record, record_in)
    
    return ApiResponse(
        success=True,
        message="更新生长记录成功",
        data=GrowthRecordResponse.model_validate(updated_record).model_dump()
    )


@router.delete("/{record_id}", response_model=ApiResponse)
def delete_growth_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除生长记录
    
    Args:
        record_id: 记录ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    record = GrowthRecordCRUD.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"生长记录ID {record_id} 不存在"
        )
    
    # 删除关联的文件（如果有）
    if record.file_path:
        # record.file_path 的格式是 /uploads/images/xxx.jpg 或 /uploads/videos/xxx.mp4
        # settings.UPLOAD_DIR 是上传目录的绝对路径
        try:
            # 去掉开头的 /uploads/ 前缀
            if record.file_path.startswith("/uploads/"):
                # 截取 /uploads/ 之后的部分
                relative_part = record.file_path[len("/uploads/"):]
                abs_file_path = os.path.join(settings.UPLOAD_DIR, relative_part)
            elif record.file_path.startswith("/"):
                # 去掉开头的斜杠
                abs_file_path = os.path.join(settings.UPLOAD_DIR, record.file_path[1:])
            else:
                abs_file_path = os.path.join(settings.UPLOAD_DIR, record.file_path)
            
            # 检查文件是否存在并删除
            if os.path.exists(abs_file_path):
                os.remove(abs_file_path)
        except Exception as e:
            # 文件删除失败不影响数据库操作，但记录日志
            print(f"[WARNING] 删除文件失败: {record.file_path}, error: {str(e)}")
    
    GrowthRecordCRUD.delete(db, record)
    
    return ApiResponse(
        success=True,
        message="删除生长记录成功",
        data={"id": record_id}
    )
