"""
ERP系统主应用文件
使用FastAPI框架，包含销售、生产、库存、财务、人事等模块
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.config import engine, Base, get_db
from app.models import sales, production, inventory, finance, hr
from app.schemas import sales as sales_schemas
from app.schemas import production as production_schemas
from app.schemas import inventory as inventory_schemas
from app.schemas import finance as finance_schemas
from app.schemas import hr as hr_schemas
from app.crud.base import CRUDBase

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="ERP系统",
    description="企业资源管理系统，包含销售、生产、库存、财务、人事等模块",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 销售模块API ====================

# 客户CRUD
crud_customer = CRUDBase[sales.Customer, sales_schemas.CustomerCreate, sales_schemas.CustomerUpdate](sales.Customer)

@app.get("/api/customers/", response_model=List[sales_schemas.CustomerResponse], tags=["销售模块-客户管理"])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取客户列表
    """
    customers = crud_customer.get_multi(db, skip=skip, limit=limit)
    return customers


@app.get("/api/customers/{customer_id}", response_model=sales_schemas.CustomerResponse, tags=["销售模块-客户管理"])
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取客户信息
    """
    customer = crud_customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@app.post("/api/customers/", response_model=sales_schemas.CustomerResponse, tags=["销售模块-客户管理"])
def create_customer(customer: sales_schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    创建新客户
    """
    return crud_customer.create(db, obj_in=customer)


@app.put("/api/customers/{customer_id}", response_model=sales_schemas.CustomerResponse, tags=["销售模块-客户管理"])
def update_customer(customer_id: int, customer: sales_schemas.CustomerUpdate, db: Session = Depends(get_db)):
    """
    更新客户信息
    """
    db_customer = crud_customer.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return crud_customer.update(db, db_obj=db_customer, obj_in=customer)


@app.delete("/api/customers/{customer_id}", response_model=sales_schemas.CustomerResponse, tags=["销售模块-客户管理"])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    删除客户
    """
    db_customer = crud_customer.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return crud_customer.remove(db, id=customer_id)


# 订单API
@app.get("/api/orders/", response_model=List[sales_schemas.OrderResponse], tags=["销售模块-订单管理"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取订单列表
    """
    orders = db.query(sales.Order).offset(skip).limit(limit).all()
    return orders


@app.get("/api/orders/{order_id}", response_model=sales_schemas.OrderResponse, tags=["销售模块-订单管理"])
def read_order(order_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取订单信息
    """
    order = db.query(sales.Order).filter(sales.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@app.post("/api/orders/", response_model=sales_schemas.OrderResponse, tags=["销售模块-订单管理"])
def create_order(order: sales_schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    创建新订单
    """
    # 生成订单编号
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_order = sales.Order(
        order_no=order_no,
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # 创建订单明细
    for item in order.order_items:
        db_item = sales.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@app.put("/api/orders/{order_id}", response_model=sales_schemas.OrderResponse, tags=["销售模块-订单管理"])
def update_order(order_id: int, order: sales_schemas.OrderUpdate, db: Session = Depends(get_db)):
    """
    更新订单信息
    """
    db_order = db.query(sales.Order).filter(sales.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@app.delete("/api/orders/{order_id}", response_model=sales_schemas.OrderResponse, tags=["销售模块-订单管理"])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    删除订单
    """
    db_order = db.query(sales.Order).filter(sales.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 删除订单明细
    db.query(sales.OrderItem).filter(sales.OrderItem.order_id == order_id).delete()
    
    db.delete(db_order)
    db.commit()
    return db_order


# ==================== 生产模块API ====================

# 产品CRUD
crud_product = CRUDBase[production.Product, production_schemas.ProductCreate, production_schemas.ProductUpdate](production.Product)

@app.get("/api/products/", response_model=List[production_schemas.ProductResponse], tags=["生产模块-产品管理"])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取产品列表
    """
    products = crud_product.get_multi(db, skip=skip, limit=limit)
    return products


@app.get("/api/products/{product_id}", response_model=production_schemas.ProductResponse, tags=["生产模块-产品管理"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取产品信息
    """
    product = crud_product.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@app.post("/api/products/", response_model=production_schemas.ProductResponse, tags=["生产模块-产品管理"])
def create_product(product: production_schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    创建新产品
    """
    return crud_product.create(db, obj_in=product)


@app.put("/api/products/{product_id}", response_model=production_schemas.ProductResponse, tags=["生产模块-产品管理"])
def update_product(product_id: int, product: production_schemas.ProductUpdate, db: Session = Depends(get_db)):
    """
    更新产品信息
    """
    db_product = crud_product.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return crud_product.update(db, db_obj=db_product, obj_in=product)


@app.delete("/api/products/{product_id}", response_model=production_schemas.ProductResponse, tags=["生产模块-产品管理"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    删除产品
    """
    db_product = crud_product.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return crud_product.remove(db, id=product_id)


# 生产计划API
@app.get("/api/production-plans/", response_model=List[production_schemas.ProductionPlanResponse], tags=["生产模块-生产计划"])
def read_production_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取生产计划列表
    """
    plans = db.query(production.ProductionPlan).offset(skip).limit(limit).all()
    return plans


@app.get("/api/production-plans/{plan_id}", response_model=production_schemas.ProductionPlanResponse, tags=["生产模块-生产计划"])
def read_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产计划
    """
    plan = db.query(production.ProductionPlan).filter(production.ProductionPlan.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    return plan


@app.post("/api/production-plans/", response_model=production_schemas.ProductionPlanResponse, tags=["生产模块-生产计划"])
def create_production_plan(plan: production_schemas.ProductionPlanCreate, db: Session = Depends(get_db)):
    """
    创建生产计划
    """
    db_plan = production.ProductionPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.put("/api/production-plans/{plan_id}", response_model=production_schemas.ProductionPlanResponse, tags=["生产模块-生产计划"])
def update_production_plan(plan_id: int, plan: production_schemas.ProductionPlanUpdate, db: Session = Depends(get_db)):
    """
    更新生产计划
    """
    db_plan = db.query(production.ProductionPlan).filter(production.ProductionPlan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    
    update_data = plan.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.delete("/api/production-plans/{plan_id}", response_model=production_schemas.ProductionPlanResponse, tags=["生产模块-生产计划"])
def delete_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除生产计划
    """
    db_plan = db.query(production.ProductionPlan).filter(production.ProductionPlan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    
    db.delete(db_plan)
    db.commit()
    return db_plan


# 生产任务API
@app.get("/api/production-tasks/", response_model=List[production_schemas.ProductionTaskResponse], tags=["生产模块-生产任务"])
def read_production_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取生产任务列表
    """
    tasks = db.query(production.ProductionTask).offset(skip).limit(limit).all()
    return tasks


@app.get("/api/production-tasks/{task_id}", response_model=production_schemas.ProductionTaskResponse, tags=["生产模块-生产任务"])
def read_production_task(task_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产任务
    """
    task = db.query(production.ProductionTask).filter(production.ProductionTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="生产任务不存在")
    return task


@app.post("/api/production-tasks/", response_model=production_schemas.ProductionTaskResponse, tags=["生产模块-生产任务"])
def create_production_task(task: production_schemas.ProductionTaskCreate, db: Session = Depends(get_db)):
    """
    创建生产任务
    """
    # 生成任务编号
    task_no = task.task_no if task.task_no else f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_task = production.ProductionTask(
        task_no=task_no,
        plan_id=task.plan_id,
        product_id=task.product_id,
        quantity=task.quantity,
        start_date=task.start_date,
        end_date=task.end_date,
        actual_quantity=task.actual_quantity,
        status=task.status,
        description=task.description
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.put("/api/production-tasks/{task_id}", response_model=production_schemas.ProductionTaskResponse, tags=["生产模块-生产任务"])
def update_production_task(task_id: int, task: production_schemas.ProductionTaskUpdate, db: Session = Depends(get_db)):
    """
    更新生产任务
    """
    db_task = db.query(production.ProductionTask).filter(production.ProductionTask.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="生产任务不存在")
    
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/api/production-tasks/{task_id}", response_model=production_schemas.ProductionTaskResponse, tags=["生产模块-生产任务"])
def delete_production_task(task_id: int, db: Session = Depends(get_db)):
    """
    删除生产任务
    """
    db_task = db.query(production.ProductionTask).filter(production.ProductionTask.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="生产任务不存在")
    
    db.delete(db_task)
    db.commit()
    return db_task


# ==================== 库存模块API ====================

# 仓库CRUD
crud_warehouse = CRUDBase[inventory.Warehouse, inventory_schemas.WarehouseCreate, inventory_schemas.WarehouseUpdate](inventory.Warehouse)

@app.get("/api/warehouses/", response_model=List[inventory_schemas.WarehouseResponse], tags=["库存模块-仓库管理"])
def read_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取仓库列表
    """
    warehouses = crud_warehouse.get_multi(db, skip=skip, limit=limit)
    return warehouses


@app.get("/api/warehouses/{warehouse_id}", response_model=inventory_schemas.WarehouseResponse, tags=["库存模块-仓库管理"])
def read_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取仓库信息
    """
    warehouse = crud_warehouse.get(db, id=warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return warehouse


@app.post("/api/warehouses/", response_model=inventory_schemas.WarehouseResponse, tags=["库存模块-仓库管理"])
def create_warehouse(warehouse: inventory_schemas.WarehouseCreate, db: Session = Depends(get_db)):
    """
    创建新仓库
    """
    return crud_warehouse.create(db, obj_in=warehouse)


@app.put("/api/warehouses/{warehouse_id}", response_model=inventory_schemas.WarehouseResponse, tags=["库存模块-仓库管理"])
def update_warehouse(warehouse_id: int, warehouse: inventory_schemas.WarehouseUpdate, db: Session = Depends(get_db)):
    """
    更新仓库信息
    """
    db_warehouse = crud_warehouse.get(db, id=warehouse_id)
    if db_warehouse is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return crud_warehouse.update(db, db_obj=db_warehouse, obj_in=warehouse)


@app.delete("/api/warehouses/{warehouse_id}", response_model=inventory_schemas.WarehouseResponse, tags=["库存模块-仓库管理"])
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """
    删除仓库
    """
    db_warehouse = crud_warehouse.get(db, id=warehouse_id)
    if db_warehouse is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return crud_warehouse.remove(db, id=warehouse_id)


# 库存API
@app.get("/api/inventories/", response_model=List[inventory_schemas.InventoryResponse], tags=["库存模块-库存管理"])
def read_inventories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取库存列表
    """
    inventories = db.query(inventory.Inventory).offset(skip).limit(limit).all()
    return inventories


@app.get("/api/inventories/{inventory_id}", response_model=inventory_schemas.InventoryResponse, tags=["库存模块-库存管理"])
def read_inventory(inventory_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取库存信息
    """
    inventory_obj = db.query(inventory.Inventory).filter(inventory.Inventory.id == inventory_id).first()
    if inventory_obj is None:
        raise HTTPException(status_code=404, detail="库存不存在")
    return inventory_obj


@app.post("/api/inventories/", response_model=inventory_schemas.InventoryResponse, tags=["库存模块-库存管理"])
def create_inventory(inventory_data: inventory_schemas.InventoryCreate, db: Session = Depends(get_db)):
    """
    创建库存记录
    """
    db_inventory = inventory.Inventory(**inventory_data.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@app.put("/api/inventories/{inventory_id}", response_model=inventory_schemas.InventoryResponse, tags=["库存模块-库存管理"])
def update_inventory(inventory_id: int, inventory_data: inventory_schemas.InventoryUpdate, db: Session = Depends(get_db)):
    """
    更新库存信息
    """
    db_inventory = db.query(inventory.Inventory).filter(inventory.Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="库存不存在")
    
    update_data = inventory_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inventory, key, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


# 入库单API
@app.get("/api/stock-in-orders/", response_model=List[inventory_schemas.StockInOrderResponse], tags=["库存模块-入库管理"])
def read_stock_in_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取入库单列表
    """
    orders = db.query(inventory.StockInOrder).offset(skip).limit(limit).all()
    return orders


@app.post("/api/stock-in-orders/", response_model=inventory_schemas.StockInOrderResponse, tags=["库存模块-入库管理"])
def create_stock_in_order(order: inventory_schemas.StockInOrderCreate, db: Session = Depends(get_db)):
    """
    创建入库单
    """
    # 生成入库单编号
    order_no = f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_order = inventory.StockInOrder(
        order_no=order_no,
        warehouse_id=order.warehouse_id,
        supplier=order.supplier,
        total_amount=order.total_amount,
        status=order.status,
        remark=order.remark
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # 创建入库明细
    for item in order.stock_in_items:
        db_item = inventory.StockInItem(
            stock_in_order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(db_item)
        
        # 更新库存
        db_inventory = db.query(inventory.Inventory).filter(
            inventory.Inventory.warehouse_id == order.warehouse_id,
            inventory.Inventory.product_id == item.product_id
        ).first()
        
        if db_inventory:
            db_inventory.quantity += item.quantity
        else:
            db_inventory = inventory.Inventory(
                warehouse_id=order.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(db_inventory)
    
    db.commit()
    db.refresh(db_order)
    return db_order


# 出库单API
@app.get("/api/stock-out-orders/", response_model=List[inventory_schemas.StockOutOrderResponse], tags=["库存模块-出库管理"])
def read_stock_out_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取出库单列表
    """
    orders = db.query(inventory.StockOutOrder).offset(skip).limit(limit).all()
    return orders


@app.post("/api/stock-out-orders/", response_model=inventory_schemas.StockOutOrderResponse, tags=["库存模块-出库管理"])
def create_stock_out_order(order: inventory_schemas.StockOutOrderCreate, db: Session = Depends(get_db)):
    """
    创建出库单
    """
    # 生成出库单编号
    order_no = f"OUT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_order = inventory.StockOutOrder(
        order_no=order_no,
        warehouse_id=order.warehouse_id,
        customer=order.customer,
        total_amount=order.total_amount,
        status=order.status,
        remark=order.remark
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # 创建出库明细并更新库存
    for item in order.stock_out_items:
        db_item = inventory.StockOutItem(
            stock_out_order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(db_item)
        
        # 更新库存
        db_inventory = db.query(inventory.Inventory).filter(
            inventory.Inventory.warehouse_id == order.warehouse_id,
            inventory.Inventory.product_id == item.product_id
        ).first()
        
        if db_inventory:
            if db_inventory.quantity >= item.quantity:
                db_inventory.quantity -= item.quantity
            else:
                raise HTTPException(status_code=400, detail=f"产品ID {item.product_id} 库存不足")
        else:
            raise HTTPException(status_code=400, detail=f"产品ID {item.product_id} 不存在库存")
    
    db.commit()
    db.refresh(db_order)
    return db_order


# ==================== 财务模块API ====================

# 账户CRUD
crud_account = CRUDBase[finance.Account, finance_schemas.AccountCreate, finance_schemas.AccountUpdate](finance.Account)

@app.get("/api/accounts/", response_model=List[finance_schemas.AccountResponse], tags=["财务模块-账户管理"])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取账户列表
    """
    accounts = crud_account.get_multi(db, skip=skip, limit=limit)
    return accounts


@app.get("/api/accounts/{account_id}", response_model=finance_schemas.AccountResponse, tags=["财务模块-账户管理"])
def read_account(account_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取账户信息
    """
    account = crud_account.get(db, id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="账户不存在")
    return account


@app.post("/api/accounts/", response_model=finance_schemas.AccountResponse, tags=["财务模块-账户管理"])
def create_account(account: finance_schemas.AccountCreate, db: Session = Depends(get_db)):
    """
    创建新账户
    """
    return crud_account.create(db, obj_in=account)


@app.put("/api/accounts/{account_id}", response_model=finance_schemas.AccountResponse, tags=["财务模块-账户管理"])
def update_account(account_id: int, account: finance_schemas.AccountUpdate, db: Session = Depends(get_db)):
    """
    更新账户信息
    """
    db_account = crud_account.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="账户不存在")
    return crud_account.update(db, db_obj=db_account, obj_in=account)


@app.delete("/api/accounts/{account_id}", response_model=finance_schemas.AccountResponse, tags=["财务模块-账户管理"])
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """
    删除账户
    """
    db_account = crud_account.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="账户不存在")
    return crud_account.remove(db, id=account_id)


# 收入API
@app.get("/api/incomes/", response_model=List[finance_schemas.IncomeResponse], tags=["财务模块-收入管理"])
def read_incomes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取收入列表
    """
    incomes = db.query(finance.Income).offset(skip).limit(limit).all()
    return incomes


@app.post("/api/incomes/", response_model=finance_schemas.IncomeResponse, tags=["财务模块-收入管理"])
def create_income(income: finance_schemas.IncomeCreate, db: Session = Depends(get_db)):
    """
    创建收入记录
    """
    # 生成收入编号
    income_no = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_income = finance.Income(
        income_no=income_no,
        account_id=income.account_id,
        income_date=income.income_date,
        amount=income.amount,
        category=income.category,
        source=income.source,
        description=income.description
    )
    db.add(db_income)
    
    # 更新账户余额
    db_account = crud_account.get(db, id=income.account_id)
    if db_account:
        db_account.balance += income.amount
    
    db.commit()
    db.refresh(db_income)
    return db_income


# 支出API
@app.get("/api/expenses/", response_model=List[finance_schemas.ExpenseResponse], tags=["财务模块-支出管理"])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取支出列表
    """
    expenses = db.query(finance.Expense).offset(skip).limit(limit).all()
    return expenses


@app.post("/api/expenses/", response_model=finance_schemas.ExpenseResponse, tags=["财务模块-支出管理"])
def create_expense(expense: finance_schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """
    创建支出记录
    """
    # 生成支出编号
    expense_no = f"EXP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_expense = finance.Expense(
        expense_no=expense_no,
        account_id=expense.account_id,
        expense_date=expense.expense_date,
        amount=expense.amount,
        category=expense.category,
        recipient=expense.recipient,
        description=expense.description
    )
    db.add(db_expense)
    
    # 更新账户余额
    db_account = crud_account.get(db, id=expense.account_id)
    if db_account:
        if db_account.balance >= expense.amount:
            db_account.balance -= expense.amount
        else:
            raise HTTPException(status_code=400, detail="账户余额不足")
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


# 发票API
@app.get("/api/invoices/", response_model=List[finance_schemas.InvoiceResponse], tags=["财务模块-发票管理"])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取发票列表
    """
    invoices = db.query(finance.Invoice).offset(skip).limit(limit).all()
    return invoices


@app.post("/api/invoices/", response_model=finance_schemas.InvoiceResponse, tags=["财务模块-发票管理"])
def create_invoice(invoice: finance_schemas.InvoiceCreate, db: Session = Depends(get_db)):
    """
    创建发票记录
    """
    # 生成发票编号
    invoice_no = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_invoice = finance.Invoice(
        invoice_no=invoice_no,
        **invoice.model_dump()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


# ==================== 人事模块API ====================

# 部门CRUD
crud_department = CRUDBase[hr.Department, hr_schemas.DepartmentCreate, hr_schemas.DepartmentUpdate](hr.Department)

@app.get("/api/departments/", response_model=List[hr_schemas.DepartmentResponse], tags=["人事模块-部门管理"])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取部门列表
    """
    departments = crud_department.get_multi(db, skip=skip, limit=limit)
    return departments


@app.get("/api/departments/{department_id}", response_model=hr_schemas.DepartmentResponse, tags=["人事模块-部门管理"])
def read_department(department_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取部门信息
    """
    department = crud_department.get(db, id=department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    return department


@app.post("/api/departments/", response_model=hr_schemas.DepartmentResponse, tags=["人事模块-部门管理"])
def create_department(department: hr_schemas.DepartmentCreate, db: Session = Depends(get_db)):
    """
    创建新部门
    """
    return crud_department.create(db, obj_in=department)


@app.put("/api/departments/{department_id}", response_model=hr_schemas.DepartmentResponse, tags=["人事模块-部门管理"])
def update_department(department_id: int, department: hr_schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    """
    更新部门信息
    """
    db_department = crud_department.get(db, id=department_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    return crud_department.update(db, db_obj=db_department, obj_in=department)


@app.delete("/api/departments/{department_id}", response_model=hr_schemas.DepartmentResponse, tags=["人事模块-部门管理"])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    """
    删除部门
    """
    db_department = crud_department.get(db, id=department_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    return crud_department.remove(db, id=department_id)


# 职位CRUD
crud_position = CRUDBase[hr.Position, hr_schemas.PositionCreate, hr_schemas.PositionUpdate](hr.Position)

@app.get("/api/positions/", response_model=List[hr_schemas.PositionResponse], tags=["人事模块-职位管理"])
def read_positions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取职位列表
    """
    positions = crud_position.get_multi(db, skip=skip, limit=limit)
    return positions


@app.get("/api/positions/{position_id}", response_model=hr_schemas.PositionResponse, tags=["人事模块-职位管理"])
def read_position(position_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取职位信息
    """
    position = crud_position.get(db, id=position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="职位不存在")
    return position


@app.post("/api/positions/", response_model=hr_schemas.PositionResponse, tags=["人事模块-职位管理"])
def create_position(position: hr_schemas.PositionCreate, db: Session = Depends(get_db)):
    """
    创建新职位
    """
    return crud_position.create(db, obj_in=position)


@app.put("/api/positions/{position_id}", response_model=hr_schemas.PositionResponse, tags=["人事模块-职位管理"])
def update_position(position_id: int, position: hr_schemas.PositionUpdate, db: Session = Depends(get_db)):
    """
    更新职位信息
    """
    db_position = crud_position.get(db, id=position_id)
    if db_position is None:
        raise HTTPException(status_code=404, detail="职位不存在")
    return crud_position.update(db, db_obj=db_position, obj_in=position)


@app.delete("/api/positions/{position_id}", response_model=hr_schemas.PositionResponse, tags=["人事模块-职位管理"])
def delete_position(position_id: int, db: Session = Depends(get_db)):
    """
    删除职位
    """
    db_position = crud_position.get(db, id=position_id)
    if db_position is None:
        raise HTTPException(status_code=404, detail="职位不存在")
    return crud_position.remove(db, id=position_id)


# 员工API
@app.get("/api/employees/", response_model=List[hr_schemas.EmployeeResponse], tags=["人事模块-员工管理"])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取员工列表
    """
    employees = db.query(hr.Employee).offset(skip).limit(limit).all()
    return employees


@app.get("/api/employees/{employee_id}", response_model=hr_schemas.EmployeeResponse, tags=["人事模块-员工管理"])
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取员工信息
    """
    employee = db.query(hr.Employee).filter(hr.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    return employee


@app.post("/api/employees/", response_model=hr_schemas.EmployeeResponse, tags=["人事模块-员工管理"])
def create_employee(employee: hr_schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """
    创建新员工
    """
    db_employee = hr.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.put("/api/employees/{employee_id}", response_model=hr_schemas.EmployeeResponse, tags=["人事模块-员工管理"])
def update_employee(employee_id: int, employee: hr_schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    """
    更新员工信息
    """
    db_employee = db.query(hr.Employee).filter(hr.Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.delete("/api/employees/{employee_id}", response_model=hr_schemas.EmployeeResponse, tags=["人事模块-员工管理"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    删除员工
    """
    db_employee = db.query(hr.Employee).filter(hr.Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    db.delete(db_employee)
    db.commit()
    return db_employee


# 考勤API
@app.get("/api/attendances/", response_model=List[hr_schemas.AttendanceResponse], tags=["人事模块-考勤管理"])
def read_attendances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取考勤记录列表
    """
    attendances = db.query(hr.Attendance).offset(skip).limit(limit).all()
    return attendances


@app.post("/api/attendances/", response_model=hr_schemas.AttendanceResponse, tags=["人事模块-考勤管理"])
def create_attendance(attendance: hr_schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """
    创建考勤记录
    """
    db_attendance = hr.Attendance(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


# 薪资记录API
@app.get("/api/salary-records/", response_model=List[hr_schemas.SalaryRecordResponse], tags=["人事模块-薪资管理"])
def read_salary_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取薪资记录列表
    """
    records = db.query(hr.SalaryRecord).offset(skip).limit(limit).all()
    return records


@app.post("/api/salary-records/", response_model=hr_schemas.SalaryRecordResponse, tags=["人事模块-薪资管理"])
def create_salary_record(record: hr_schemas.SalaryRecordCreate, db: Session = Depends(get_db)):
    """
    创建薪资记录
    """
    db_record = hr.SalaryRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# ==================== 系统信息API ====================

@app.get("/", tags=["系统信息"])
def read_root():
    """
    系统根路径，返回系统信息
    """
    return {
        "name": "ERP系统",
        "description": "企业资源管理系统",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/health", tags=["系统信息"])
def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "timestamp": datetime.now()}


# ==================== 测试数据生成API ====================

@app.post("/api/test-data/generate", tags=["测试功能"])
def generate_test_data(db: Session = Depends(get_db)):
    """
    生成测试数据
    """
    from app.test_data import generate_all_test_data
    generate_all_test_data(db)
    return {"message": "测试数据生成成功"}


@app.get("/api/test-data/status", tags=["测试功能"])
def check_test_data_status(db: Session = Depends(get_db)):
    """
    检查测试数据状态
    """
    customer_count = db.query(sales.Customer).count()
    product_count = db.query(production.Product).count()
    employee_count = db.query(hr.Employee).count()
    
    return {
        "customers": customer_count,
        "products": product_count,
        "employees": employee_count,
        "has_test_data": customer_count > 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
