from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.db.database import Base, engine
from app.routers import (
    auth_router, classes_router, bookings_router,
    checkin_router, private_router, cards_router, admin_router
)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Fitness API starting up...")
    yield
    print("Fitness API shutting down...")

app = FastAPI(
    title="健身课程预约系统 API",
    description="提供课程预约、签到、私教课等功能的后端API",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

app.include_router(auth_router)
app.include_router(classes_router)
app.include_router(bookings_router)
app.include_router(checkin_router)
app.include_router(private_router)
app.include_router(cards_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "健身课程预约系统 API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": __import__('datetime').datetime.now().isoformat()}
