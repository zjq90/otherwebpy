from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import security, environment, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="物业秩序与环境管理系统",
    description="前后端分离的物业秩序维护管理与环境保洁绿化养护管理系统",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(security.router)
app.include_router(environment.router)
app.include_router(test.router)


@app.get("/", tags=["根路由"])
async def root():
    return {
        "message": "物业秩序与环境管理系统API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}
