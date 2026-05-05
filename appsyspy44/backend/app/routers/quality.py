from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.quality import (
    QualityDataCreate, QualityDataUpdate, QualityDataResponse,
    ProductStrengthCreate, ProductStrengthUpdate, ProductStrengthResponse,
    QualityTrendResponse, StrengthTrendResponse
)
from app.schemas.common import ChartResponse
from app.crud.quality_crud import QualityDataCRUD, ProductStrengthCRUD

router = APIRouter()

@router.get("/quality-data", response_model=List[QualityDataResponse])
def get_quality_data_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return QualityDataCRUD.get_all(db, skip=skip, limit=limit)

@router.get("/quality-data/{data_id}", response_model=QualityDataResponse)
def get_quality_data(data_id: int, db: Session = Depends(get_db)):
    data = QualityDataCRUD.get_by_id(db, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="质量数据不存在")
    return data

@router.post("/quality-data", response_model=QualityDataResponse)
def create_quality_data(data: QualityDataCreate, db: Session = Depends(get_db)):
    return QualityDataCRUD.create(db, data)

@router.put("/quality-data/{data_id}", response_model=QualityDataResponse)
def update_quality_data(data_id: int, data: QualityDataUpdate, db: Session = Depends(get_db)):
    db_data = QualityDataCRUD.update(db, data_id, data)
    if not db_data:
        raise HTTPException(status_code=404, detail="质量数据不存在")
    return db_data

@router.delete("/quality-data/{data_id}")
def delete_quality_data(data_id: int, db: Session = Depends(get_db)):
    success = QualityDataCRUD.delete(db, data_id)
    if not success:
        raise HTTPException(status_code=404, detail="质量数据不存在")
    return {"message": "删除成功"}

@router.get("/quality-trend", response_model=QualityTrendResponse)
def get_quality_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    return QualityDataCRUD.get_quality_trend(db, start_date, end_date)

@router.get("/chart/quality-pass-rate", response_model=ChartResponse)
def get_quality_pass_rate_chart(
    chart_type: str = Query("line", description="图表类型：line或bar"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    trend = QualityDataCRUD.get_quality_trend(db, start_date, end_date)
    
    x_axis_data = [d["date"] for d in trend["data"]]
    pass_rates = [d["pass_rate"] for d in trend["data"]]
    
    return {
        "chart_type": chart_type,
        "title": "原材料检验合格率趋势",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "合格率(%)", "data": pass_rates, "type": chart_type}
        ]
    }

@router.get("/product-strength", response_model=List[ProductStrengthResponse])
def get_product_strength_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ProductStrengthCRUD.get_all(db, skip=skip, limit=limit)

@router.get("/product-strength/{data_id}", response_model=ProductStrengthResponse)
def get_product_strength(data_id: int, db: Session = Depends(get_db)):
    data = ProductStrengthCRUD.get_by_id(db, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="强度数据不存在")
    return data

@router.post("/product-strength", response_model=ProductStrengthResponse)
def create_product_strength(data: ProductStrengthCreate, db: Session = Depends(get_db)):
    return ProductStrengthCRUD.create(db, data)

@router.put("/product-strength/{data_id}", response_model=ProductStrengthResponse)
def update_product_strength(data_id: int, data: ProductStrengthUpdate, db: Session = Depends(get_db)):
    db_data = ProductStrengthCRUD.update(db, data_id, data)
    if not db_data:
        raise HTTPException(status_code=404, detail="强度数据不存在")
    return db_data

@router.delete("/product-strength/{data_id}")
def delete_product_strength(data_id: int, db: Session = Depends(get_db)):
    success = ProductStrengthCRUD.delete(db, data_id)
    if not success:
        raise HTTPException(status_code=404, detail="强度数据不存在")
    return {"message": "删除成功"}

@router.get("/strength-trend", response_model=StrengthTrendResponse)
def get_strength_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    return ProductStrengthCRUD.get_strength_trend(db, start_date, end_date)

@router.get("/chart/strength-trend", response_model=ChartResponse)
def get_strength_chart(
    chart_type: str = Query("line", description="图表类型：line或bar"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    trend = ProductStrengthCRUD.get_strength_trend(db, start_date, end_date)
    
    x_axis_data = [d["date"] for d in trend["data"]]
    actual_strength = [d["avg_actual_strength"] for d in trend["data"]]
    standard_strength = [d["standard_strength"] for d in trend["data"]]
    pass_rates = [d["pass_rate"] for d in trend["data"]]
    
    return {
        "chart_type": chart_type,
        "title": "成品强度达标率趋势",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "实际强度", "data": actual_strength, "type": chart_type},
            {"name": "标准强度", "data": standard_strength, "type": chart_type},
            {"name": "达标率(%)", "data": pass_rates, "type": "line"}
        ]
    }
