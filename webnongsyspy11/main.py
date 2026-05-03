"""
农资管理系统主应用
基于FastAPI + SQLite + SQLAlchemy
"""
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date, datetime
import math
import json

import models
import schemas
import crud
from database import engine, SessionLocal, get_db, init_db
from config import settings

DEFAULT_PAGE_SIZE = 10


def get_skip_from_page(page: int, page_size: int) -> int:
    """根据页码和每页数量计算跳过的记录数"""
    return (page - 1) * page_size


def get_pagination_info(total: int, page: int, page_size: int) -> dict:
    """获取分页信息"""
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "start_index": (page - 1) * page_size + 1,
        "end_index": min(page * page_size, total)
    }

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


@app.on_event("startup")
def startup_event():
    """
    应用启动时初始化数据库
    """
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """
    首页 - 显示系统概览和统计信息
    """
    stats = crud.get_statistics(db)
    alerts = crud.get_low_inventory_alerts(db)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "alerts": alerts,
        "active_menu": "dashboard"
    })


@app.get("/api/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """
    获取系统统计数据API
    """
    return crud.get_statistics(db)


@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """
    获取库存预警列表API
    """
    return crud.get_low_inventory_alerts(db)


@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    供应商管理页面
    """
    total = crud.get_supplier_count(db)
    skip = get_skip_from_page(page, page_size)
    suppliers = crud.get_suppliers(db, skip=skip, limit=page_size)
    pagination = get_pagination_info(total, page, page_size)
    
    return templates.TemplateResponse("suppliers.html", {
        "request": request,
        "suppliers": suppliers,
        "pagination": pagination,
        "active_menu": "suppliers"
    })


@app.get("/api/suppliers")
def read_suppliers(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取供应商列表API（支持分页）
    """
    total = crud.get_supplier_count(db)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_suppliers(db, skip=skip, limit=page_size)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.get("/api/suppliers/{supplier_id}")
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    获取单个供应商API
    """
    supplier = crud.get_supplier_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


@app.post("/api/suppliers")
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    """
    创建供应商API
    """
    if crud.get_supplier_by_name(db, supplier.name):
        raise HTTPException(status_code=400, detail=f"供应商名称 '{supplier.name}' 已存在")
    return crud.create_supplier(db=db, supplier=supplier)


@app.put("/api/suppliers/{supplier_id}")
def update_supplier(supplier_id: int, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    """
    更新供应商API
    """
    existing = crud.get_supplier_by_id(db, supplier_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    if crud.get_supplier_by_name(db, supplier.name, exclude_id=supplier_id):
        raise HTTPException(status_code=400, detail=f"供应商名称 '{supplier.name}' 已存在")
    
    db_supplier = crud.update_supplier(db, supplier_id, supplier)
    return db_supplier


@app.delete("/api/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    删除供应商API
    """
    from sqlalchemy import func
    purchase_count = db.query(func.count(models.Purchase.id)).filter(
        models.Purchase.supplier_id == supplier_id
    ).scalar() or 0
    
    if purchase_count > 0:
        raise HTTPException(status_code=400, detail=f"该供应商已关联 {purchase_count} 条采购记录，无法删除")
    
    success = crud.delete_supplier(db, supplier_id)
    if not success:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return {"message": "删除成功"}


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    农资分类管理页面
    """
    total = db.query(func.count(models.Category.id)).scalar() or 0
    skip = get_skip_from_page(page, page_size)
    categories = crud.get_categories(db, skip=skip, limit=page_size)
    pagination = get_pagination_info(total, page, page_size)
    
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": categories,
        "pagination": pagination,
        "active_menu": "categories"
    })


@app.get("/api/categories")
def read_categories(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取分类列表API（支持分页）
    """
    total = db.query(func.count(models.Category.id)).scalar() or 0
    skip = get_skip_from_page(page, page_size)
    items = crud.get_categories(db, skip=skip, limit=page_size)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.post("/api/categories")
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """
    创建分类API
    """
    if db.query(models.Category).filter(models.Category.code == category.code).first():
        raise HTTPException(status_code=400, detail=f"分类编码 '{category.code}' 已存在")
    if db.query(models.Category).filter(models.Category.name == category.name).first():
        raise HTTPException(status_code=400, detail=f"分类名称 '{category.name}' 已存在")
    return crud.create_category(db=db, category=category)


@app.put("/api/categories/{category_id}")
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    """
    更新分类API
    """
    existing = crud.get_category_by_id(db, category_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if db.query(models.Category).filter(
        models.Category.code == category.code,
        models.Category.id != category_id
    ).first():
        raise HTTPException(status_code=400, detail=f"分类编码 '{category.code}' 已存在")
    
    if db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.id != category_id
    ).first():
        raise HTTPException(status_code=400, detail=f"分类名称 '{category.name}' 已存在")
    
    db_category = crud.update_category(db, category_id, category)
    return db_category


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    删除分类API
    """
    supply_count = db.query(func.count(models.Supply.id)).filter(
        models.Supply.category_id == category_id
    ).scalar() or 0
    
    if supply_count > 0:
        raise HTTPException(status_code=400, detail=f"该分类已关联 {supply_count} 种农资，无法删除")
    
    success = crud.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


@app.get("/supplies", response_class=HTMLResponse)
async def supplies_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    农资管理页面
    """
    total = crud.get_supply_count(db, category_id=category_id)
    skip = get_skip_from_page(page, page_size)
    supplies = crud.get_supplies(db, skip=skip, limit=page_size, category_id=category_id)
    pagination = get_pagination_info(total, page, page_size)
    categories = crud.get_categories(db)
    
    return templates.TemplateResponse("supplies.html", {
        "request": request,
        "supplies": supplies,
        "categories": categories,
        "pagination": pagination,
        "category_id": category_id,
        "active_menu": "supplies"
    })


@app.get("/api/supplies")
def read_supplies(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    获取农资列表API（支持分页）
    """
    total = crud.get_supply_count(db, category_id=category_id)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_supplies(db, skip=skip, limit=page_size, category_id=category_id)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.get("/api/supplies/{supply_id}")
def read_supply(supply_id: int, db: Session = Depends(get_db)):
    """
    获取单个农资API
    """
    supply = crud.get_supply_by_id(db, supply_id)
    if supply is None:
        raise HTTPException(status_code=404, detail="农资不存在")
    return supply


@app.post("/api/supplies")
def create_supply(supply: schemas.SupplyCreate, db: Session = Depends(get_db)):
    """
    创建农资API
    """
    if crud.get_supply_by_name(db, supply.name):
        raise HTTPException(status_code=400, detail=f"农资名称 '{supply.name}' 已存在")
    
    category = crud.get_category_by_id(db, supply.category_id)
    if category is None:
        raise HTTPException(status_code=400, detail=f"分类ID {supply.category_id} 不存在")
    
    return crud.create_supply(db=db, supply=supply)


@app.put("/api/supplies/{supply_id}")
def update_supply(supply_id: int, supply: schemas.SupplyUpdate, db: Session = Depends(get_db)):
    """
    更新农资API
    """
    existing = crud.get_supply_by_id(db, supply_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="农资不存在")
    
    if crud.get_supply_by_name(db, supply.name, exclude_id=supply_id):
        raise HTTPException(status_code=400, detail=f"农资名称 '{supply.name}' 已存在")
    
    category = crud.get_category_by_id(db, supply.category_id)
    if category is None:
        raise HTTPException(status_code=400, detail=f"分类ID {supply.category_id} 不存在")
    
    db_supply = crud.update_supply(db, supply_id, supply)
    return db_supply


@app.delete("/api/supplies/{supply_id}")
def delete_supply(supply_id: int, db: Session = Depends(get_db)):
    """
    删除农资API
    """
    from sqlalchemy import func
    purchase_count = db.query(func.count(models.Purchase.id)).filter(
        models.Purchase.supply_id == supply_id
    ).scalar() or 0
    
    inventory_count = db.query(func.count(models.Inventory.id)).filter(
        models.Inventory.supply_id == supply_id,
        models.Inventory.quantity > 0
    ).scalar() or 0
    
    if purchase_count > 0:
        raise HTTPException(status_code=400, detail=f"该农资已关联 {purchase_count} 条采购记录，无法删除")
    
    if inventory_count > 0:
        raise HTTPException(status_code=400, detail=f"该农资还有库存，无法删除")
    
    success = crud.delete_supply(db, supply_id)
    if not success:
        raise HTTPException(status_code=404, detail="农资不存在")
    return {"message": "删除成功"}


@app.get("/plots", response_class=HTMLResponse)
async def plots_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    地块管理页面
    """
    total = crud.get_plot_count(db)
    skip = get_skip_from_page(page, page_size)
    plots = crud.get_plots(db, skip=skip, limit=page_size)
    pagination = get_pagination_info(total, page, page_size)
    
    return templates.TemplateResponse("plots.html", {
        "request": request,
        "plots": plots,
        "pagination": pagination,
        "active_menu": "plots"
    })


@app.get("/api/plots")
def read_plots(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取地块列表API（支持分页）
    """
    total = crud.get_plot_count(db)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_plots(db, skip=skip, limit=page_size)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.post("/api/plots")
def create_plot(plot: schemas.PlotCreate, db: Session = Depends(get_db)):
    """
    创建地块API
    """
    if crud.get_plot_by_name(db, plot.name):
        raise HTTPException(status_code=400, detail=f"地块名称 '{plot.name}' 已存在")
    
    return crud.create_plot(db=db, plot=plot)


@app.put("/api/plots/{plot_id}")
def update_plot(plot_id: int, plot: schemas.PlotUpdate, db: Session = Depends(get_db)):
    """
    更新地块API
    """
    existing = crud.get_plot_by_id(db, plot_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="地块不存在")
    
    if crud.get_plot_by_name(db, plot.name, exclude_id=plot_id):
        raise HTTPException(status_code=400, detail=f"地块名称 '{plot.name}' 已存在")
    
    db_plot = crud.update_plot(db, plot_id, plot)
    return db_plot


@app.delete("/api/plots/{plot_id}")
def delete_plot(plot_id: int, db: Session = Depends(get_db)):
    """
    删除地块API
    """
    usage_count = db.query(func.count(models.UsageRecord.id)).filter(
        models.UsageRecord.plot_id == plot_id
    ).scalar() or 0
    
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"该地块已关联 {usage_count} 条使用记录，无法删除")
    
    success = crud.delete_plot(db, plot_id)
    if not success:
        raise HTTPException(status_code=404, detail="地块不存在")
    return {"message": "删除成功"}


@app.get("/crops", response_class=HTMLResponse)
async def crops_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    作物管理页面
    """
    total = crud.get_crop_count(db)
    skip = get_skip_from_page(page, page_size)
    crops = crud.get_crops(db, skip=skip, limit=page_size)
    pagination = get_pagination_info(total, page, page_size)
    
    return templates.TemplateResponse("crops.html", {
        "request": request,
        "crops": crops,
        "pagination": pagination,
        "active_menu": "crops"
    })


@app.get("/api/crops")
def read_crops(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取作物列表API（支持分页）
    """
    total = crud.get_crop_count(db)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_crops(db, skip=skip, limit=page_size)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.post("/api/crops")
def create_crop(crop: schemas.CropCreate, db: Session = Depends(get_db)):
    """
    创建作物API
    """
    if crud.get_crop_by_name(db, crop.name):
        raise HTTPException(status_code=400, detail=f"作物名称 '{crop.name}' 已存在")
    
    return crud.create_crop(db=db, crop=crop)


@app.put("/api/crops/{crop_id}")
def update_crop(crop_id: int, crop: schemas.CropUpdate, db: Session = Depends(get_db)):
    """
    更新作物API
    """
    existing = crud.get_crop_by_id(db, crop_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="作物不存在")
    
    if crud.get_crop_by_name(db, crop.name, exclude_id=crop_id):
        raise HTTPException(status_code=400, detail=f"作物名称 '{crop.name}' 已存在")
    
    db_crop = crud.update_crop(db, crop_id, crop)
    return db_crop


@app.delete("/api/crops/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    """
    删除作物API
    """
    usage_count = db.query(func.count(models.UsageRecord.id)).filter(
        models.UsageRecord.crop_id == crop_id
    ).scalar() or 0
    
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"该作物已关联 {usage_count} 条使用记录，无法删除")
    
    success = crud.delete_crop(db, crop_id)
    if not success:
        raise HTTPException(status_code=404, detail="作物不存在")
    return {"message": "删除成功"}


@app.get("/purchases", response_class=HTMLResponse)
async def purchases_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    supply_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    采购管理页面
    """
    total = crud.get_purchase_count(db, supply_id=supply_id)
    skip = get_skip_from_page(page, page_size)
    purchases = crud.get_purchases(db, skip=skip, limit=page_size, supply_id=supply_id)
    pagination = get_pagination_info(total, page, page_size)
    suppliers = crud.get_suppliers(db)
    supplies = crud.get_supplies(db)
    
    return templates.TemplateResponse("purchases.html", {
        "request": request,
        "purchases": purchases,
        "suppliers": suppliers,
        "supplies": supplies,
        "pagination": pagination,
        "supply_id": supply_id,
        "active_menu": "purchases"
    })


@app.get("/api/purchases")
def read_purchases(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    supply_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    获取采购记录列表API（支持分页）
    """
    total = crud.get_purchase_count(db, supply_id=supply_id)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_purchases(db, skip=skip, limit=page_size, supply_id=supply_id)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.get("/api/purchases/{purchase_id}")
def read_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """
    获取单个采购记录API
    """
    purchase = crud.get_purchase_by_id(db, purchase_id)
    if purchase is None:
        raise HTTPException(status_code=404, detail="采购记录不存在")
    return purchase


@app.post("/api/purchases")
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    """
    创建采购记录API
    """
    if crud.get_purchase_by_batch_no(db, purchase.batch_no):
        raise HTTPException(status_code=400, detail=f"批次号 '{purchase.batch_no}' 已存在，请使用其他批次号")
    
    supplier = crud.get_supplier_by_id(db, purchase.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=400, detail=f"供应商ID {purchase.supplier_id} 不存在")
    
    supply = crud.get_supply_by_id(db, purchase.supply_id)
    if supply is None:
        raise HTTPException(status_code=400, detail=f"农资ID {purchase.supply_id} 不存在")
    
    return crud.create_purchase(db=db, purchase=purchase)


@app.put("/api/purchases/{purchase_id}")
def update_purchase(purchase_id: int, purchase: schemas.PurchaseUpdate, db: Session = Depends(get_db)):
    """
    更新采购记录API
    """
    existing = crud.get_purchase_by_id(db, purchase_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="采购记录不存在")
    
    if crud.get_purchase_by_batch_no(db, purchase.batch_no, exclude_id=purchase_id):
        raise HTTPException(status_code=400, detail=f"批次号 '{purchase.batch_no}' 已存在，请使用其他批次号")
    
    supplier = crud.get_supplier_by_id(db, purchase.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=400, detail=f"供应商ID {purchase.supplier_id} 不存在")
    
    supply = crud.get_supply_by_id(db, purchase.supply_id)
    if supply is None:
        raise HTTPException(status_code=400, detail=f"农资ID {purchase.supply_id} 不存在")
    
    db_purchase = crud.update_purchase(db, purchase_id, purchase)
    if db_purchase is None:
        raise HTTPException(status_code=400, detail="更新失败，可能是库存数量发生了变化")
    return db_purchase


@app.delete("/api/purchases/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """
    删除采购记录API
    """
    success = crud.delete_purchase(db, purchase_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法删除，库存不为空或记录不存在")
    return {"message": "删除成功"}


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    supply_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    库存管理页面
    """
    inventory_summary = crud.get_inventory_summary(db)
    total = crud.get_inventory_count(db, supply_id=supply_id)
    skip = get_skip_from_page(page, page_size)
    inventories = crud.get_inventories(db, skip=skip, limit=page_size, supply_id=supply_id)
    pagination = get_pagination_info(total, page, page_size)
    supplies = crud.get_supplies(db)
    alerts = crud.get_low_inventory_alerts(db)
    
    return templates.TemplateResponse("inventory.html", {
        "request": request,
        "inventory_summary": inventory_summary,
        "inventories": inventories,
        "supplies": supplies,
        "alerts": alerts,
        "pagination": pagination,
        "supply_id": supply_id,
        "active_menu": "inventory"
    })


@app.get("/api/inventory")
def read_inventory(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    supply_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    获取库存列表API（支持分页）
    """
    total = crud.get_inventory_count(db, supply_id=supply_id)
    skip = get_skip_from_page(page, page_size)
    items = crud.get_inventories(db, skip=skip, limit=page_size, supply_id=supply_id)
    return schemas.create_paginated_response(items, total, page, page_size)


@app.get("/api/inventory/summary")
def get_inventory_summary(db: Session = Depends(get_db)):
    """
    获取库存汇总API
    """
    return crud.get_inventory_summary(db)


@app.get("/api/inventory/supply/{supply_id}")
def get_inventory_by_supply(supply_id: int, db: Session = Depends(get_db)):
    """
    获取指定农资的库存批次API（先进先出顺序）
    """
    return crud.get_inventory_by_supply(db, supply_id)


@app.get("/usage_records", response_class=HTMLResponse)
async def usage_records_page(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    supply_id: Optional[int] = Query(None),
    plot_id: Optional[int] = Query(None),
    crop_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    使用记录管理页面
    """
    total = crud.get_usage_record_count(
        db, 
        supply_id=supply_id, 
        plot_id=plot_id, 
        crop_id=crop_id
    )
    skip = get_skip_from_page(page, page_size)
    usage_records = crud.get_usage_records(
        db, 
        skip=skip, 
        limit=page_size, 
        supply_id=supply_id, 
        plot_id=plot_id, 
        crop_id=crop_id
    )
    pagination = get_pagination_info(total, page, page_size)
    supplies = crud.get_supplies(db)
    plots = crud.get_plots(db)
    crops = crud.get_crops(db)
    inventories = crud.get_inventories(db)
    
    return templates.TemplateResponse("usage_records.html", {
        "request": request,
        "usage_records": usage_records,
        "supplies": supplies,
        "plots": plots,
        "crops": crops,
        "inventories": inventories,
        "pagination": pagination,
        "supply_id": supply_id,
        "plot_id": plot_id,
        "crop_id": crop_id,
        "active_menu": "usage_records"
    })


@app.get("/api/usage_records")
def read_usage_records(
    page: int = Query(1, ge=1), 
    page_size: int = Query(100, ge=1, le=100),
    supply_id: Optional[int] = None,
    plot_id: Optional[int] = None,
    crop_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取使用记录列表API（支持分页）
    """
    total = crud.get_usage_record_count(
        db, 
        supply_id=supply_id, 
        plot_id=plot_id, 
        crop_id=crop_id
    )
    skip = get_skip_from_page(page, page_size)
    items = crud.get_usage_records(
        db, 
        skip=skip, 
        limit=page_size, 
        supply_id=supply_id,
        plot_id=plot_id,
        crop_id=crop_id
    )
    return schemas.create_paginated_response(items, total, page, page_size)


@app.get("/api/usage_records/{usage_id}")
def read_usage_record(usage_id: int, db: Session = Depends(get_db)):
    """
    获取单个使用记录API
    """
    usage = crud.get_usage_record_by_id(db, usage_id)
    if usage is None:
        raise HTTPException(status_code=404, detail="使用记录不存在")
    return usage


@app.post("/api/usage_records")
def create_usage_record(usage: schemas.UsageRecordCreate, db: Session = Depends(get_db)):
    """
    创建使用记录API
    """
    db_usage = crud.create_usage_record(db=db, usage=usage)
    if db_usage is None:
        raise HTTPException(status_code=400, detail="库存不足")
    return db_usage


@app.post("/api/usage_records/fifo")
def create_usage_record_fifo(usage_data: dict, db: Session = Depends(get_db)):
    """
    使用先进先出策略创建使用记录API
    """
    db_usage = crud.create_usage_record_fifo(db=db, usage_data=usage_data)
    if db_usage is None:
        raise HTTPException(status_code=400, detail="库存不足或参数错误")
    return db_usage


@app.put("/api/usage_records/{usage_id}")
def update_usage_record(usage_id: int, usage: schemas.UsageRecordUpdate, db: Session = Depends(get_db)):
    """
    更新使用记录API
    """
    db_usage = crud.update_usage_record(db, usage_id, usage)
    if db_usage is None:
        raise HTTPException(status_code=404, detail="使用记录不存在或库存不足")
    return db_usage


@app.delete("/api/usage_records/{usage_id}")
def delete_usage_record(usage_id: int, db: Session = Depends(get_db)):
    """
    删除使用记录API
    """
    success = crud.delete_usage_record(db, usage_id)
    if not success:
        raise HTTPException(status_code=404, detail="使用记录不存在")
    return {"message": "删除成功"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
