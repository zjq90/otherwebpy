from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app import schemas
from app.crud import product_crud

router = APIRouter(prefix="/api/products", tags=["产品管理"])

@router.get("/", response_model=schemas.ProductList)
def read_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    grade: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    
    if name or grade:
        products = product_crud.search(db, name=name, grade=grade, skip=skip, limit=limit)
    elif keyword:
        from app.models import Product
        products = db.query(Product).filter(
            Product.name.contains(keyword)
        ).offset(skip).limit(limit).all()
    else:
        products = product_crud.get_multi(db, skip=skip, limit=limit)
    
    total = product_crud.get_count(db)
    return {"products": products, "total": total}

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    product_data = product.model_dump()
    return product_crud.create(db, obj_in=product_data)

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = product_crud.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    update_data = product.model_dump(exclude_unset=True)
    return product_crud.update(db, db_obj=db_product, obj_in=update_data)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_crud.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    product_crud.remove(db, id=product_id)
    return {"message": "删除成功"}
