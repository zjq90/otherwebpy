from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database import engine, Base
from app.routers import products, customers, orders, contracts, logistics, feedbacks

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="农产品电商管理系统",
    description="基于Python+FastAPI+SQLite的农产品电商管理系统",
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

static_dir = os.path.join(BASE_DIR, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates_dir = os.path.join(BASE_DIR, "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
templates = Jinja2Templates(directory=templates_dir)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(contracts.router)
app.include_router(logistics.router)
app.include_router(feedbacks.router)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/products")
async def products_page(request: Request):
    return templates.TemplateResponse("products/list.html", {"request": request})

@app.get("/products/add")
async def products_add_page(request: Request):
    return templates.TemplateResponse("products/form.html", {"request": request, "edit_mode": False})

@app.get("/products/edit/{product_id}")
async def products_edit_page(request: Request, product_id: int):
    return templates.TemplateResponse("products/form.html", {"request": request, "edit_mode": True, "product_id": product_id})

@app.get("/customers")
async def customers_page(request: Request):
    return templates.TemplateResponse("customers/list.html", {"request": request})

@app.get("/customers/add")
async def customers_add_page(request: Request):
    return templates.TemplateResponse("customers/form.html", {"request": request, "edit_mode": False})

@app.get("/customers/edit/{customer_id}")
async def customers_edit_page(request: Request, customer_id: int):
    return templates.TemplateResponse("customers/form.html", {"request": request, "edit_mode": True, "customer_id": customer_id})

@app.get("/customers/detail/{customer_id}")
async def customers_detail_page(request: Request, customer_id: int):
    return templates.TemplateResponse("customers/detail.html", {"request": request, "customer_id": customer_id})

@app.get("/orders")
async def orders_page(request: Request):
    return templates.TemplateResponse("orders/list.html", {"request": request})

@app.get("/orders/add")
async def orders_add_page(request: Request):
    return templates.TemplateResponse("orders/form.html", {"request": request, "edit_mode": False})

@app.get("/orders/edit/{order_id}")
async def orders_edit_page(request: Request, order_id: int):
    return templates.TemplateResponse("orders/form.html", {"request": request, "edit_mode": True, "order_id": order_id})

@app.get("/orders/detail/{order_id}")
async def orders_detail_page(request: Request, order_id: int):
    return templates.TemplateResponse("orders/detail.html", {"request": request, "order_id": order_id})

@app.get("/contracts")
async def contracts_page(request: Request):
    return templates.TemplateResponse("contracts/list.html", {"request": request})

@app.get("/logistics")
async def logistics_page(request: Request):
    return templates.TemplateResponse("logistics/list.html", {"request": request})

@app.get("/logistics/track/{logistics_id}")
async def logistics_track_page(request: Request, logistics_id: int):
    return templates.TemplateResponse("logistics/track.html", {"request": request, "logistics_id": logistics_id})

@app.get("/feedbacks")
async def feedbacks_page(request: Request):
    return templates.TemplateResponse("feedbacks/list.html", {"request": request})
