from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db
from app.routers import silos, production, suppliers, settlements
from app.schemas import DashboardStats

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="混凝土搅拌站库存管理系统",
    description="一个前后端分离的库存管理、物料需求预测、供应商评级与结算管理系统",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(silos.router)
app.include_router(production.router)
app.include_router(suppliers.router)
app.include_router(settlements.router)

@app.get("/")
def root():
    return {
        "message": "混凝土搅拌站库存管理系统 API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }

@app.get("/api/dashboard", response_model=DashboardStats, summary="获取仪表盘统计数据")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取系统仪表盘的统计数据
    """
    from app.models import Silo, ProductionPlan, MaterialDemand, Supplier, Settlement
    from sqlalchemy import func
    
    total_silos = db.query(func.count(Silo.id)).scalar()
    
    low_inventory_count = db.query(func.count(Silo.id)).filter(
        Silo.current_level <= Silo.min_threshold
    ).scalar()
    
    total_production_plans = db.query(func.count(ProductionPlan.id)).scalar()
    
    pending_demands = db.query(func.count(MaterialDemand.id)).filter(
        MaterialDemand.status.in_(["待处理", "部分补货"])
    ).scalar()
    
    total_suppliers = db.query(func.count(Supplier.id)).scalar()
    
    pending_settlements = db.query(func.count(Settlement.id)).filter(
        Settlement.payment_status.in_(["待付款", "部分付款"])
    ).scalar()
    
    return DashboardStats(
        total_silos=total_silos or 0,
        low_inventory_count=low_inventory_count or 0,
        total_production_plans=total_production_plans or 0,
        pending_demands=pending_demands or 0,
        total_suppliers=total_suppliers or 0,
        pending_settlements=pending_settlements or 0
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
