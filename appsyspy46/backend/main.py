import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from routers import auth_router, orders_router, users_router, route_router, test_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="旧衣物回收系统API - 回收人员端",
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

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(users_router)
app.include_router(route_router)
app.include_router(test_router)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/", tags=["根路径"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
