## 混凝土搅拌站库存管理系统

一个前后端分离的Web系统，实现动态库存管理、物料需求预测、供应商评级与结算管理。

### 技术栈

**后端:**
- Python 3.8+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- SQLite (数据库)

**前端:**
- Vue 3
- Vite (构建工具)
- Element Plus (UI组件库)
- ECharts (图表库)
- Axios (HTTP客户端)

### 项目结构

```
websyspy32/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── routers/           # API路由
│   │   │   ├── silos.py       # 料仓与库存管理
│   │   │   ├── production.py  # 生产计划与物料需求预测
│   │   │   ├── suppliers.py   # 供应商评级与采购订单
│   │   │   └── settlements.py # 结算管理
│   │   ├── models.py          # 数据库模型
│   │   ├── schemas.py         # Pydantic模型
│   │   ├── crud.py            # CRUD操作
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── scripts/
│   │   └── generate_test_data.py  # 测试数据生成
│   └── requirements.txt       # Python依赖
│
└── frontend/                   # 前端项目
    ├── src/
    │   ├── api/               # API调用封装
    │   ├── layout/            # 布局组件
    │   ├── router/            # 路由配置
    │   ├── views/             # 页面组件
    │   │   ├── dashboard/     # 仪表盘
    │   │   ├── inventory/     # 动态库存
    │   │   ├── production/    # 物料需求预测
    │   │   ├── suppliers/     # 供应商管理
    │   │   └── settlements/   # 结算管理
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```

### 功能模块

#### 1. 动态库存管理
- 料仓管理（增删改查）
- 实时库存显示（图形化展示）
- 库存调整（入库/出库/调整）
- 低库存预警
- 库存变更记录查询

#### 2. 物料需求预测
- 生产计划管理
- 根据生产计划自动计算物料需求
- 物料缺口计算与优先级排序
- 支持重新生成需求预测
- 直接跳转创建采购订单

#### 3. 供应商评级与结算管理
- 供应商管理（增删改查）
- 供应商评级系统（供货及时性、材料质量、价格合理性、服务态度）
- 综合评分自动计算
- 采购订单管理
- 结算单自动生成
- 付款状态跟踪

### 数据库表

| 表名 | 说明 |
|------|------|
| silos | 料仓表 |
| inventory_records | 库存变更记录表 |
| production_plans | 生产计划表 |
| material_demands | 物料需求预测表 |
| suppliers | 供应商表 |
| supplier_ratings | 供应商评级记录表 |
| purchase_orders | 采购订单表 |
| settlements | 结算单表 |

### 快速开始

#### 1. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 生成测试数据（可选）
python -m scripts.generate_test_data --action generate

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务启动后，访问以下地址：
- API文档: http://localhost:8000/api/docs
- Redoc文档: http://localhost:8000/api/redoc
- OpenAPI Schema: http://localhost:8000/api/openapi.json

#### 2. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端服务启动后，访问: http://localhost:3000

### 测试数据生成

后端提供了测试数据生成脚本，可以快速填充测试数据：

```bash
# 生成测试数据
python -m scripts.generate_test_data --action generate

# 清除所有数据
python -m scripts.generate_test_data --action clear

# 重置数据（清除后重新生成）
python -m scripts.generate_test_data --action reset
```

生成的测试数据包括：
- 6个料仓（水泥、砂石、粉煤灰、外加剂等）
- 4个供应商（包含评级记录）
- 3个生产计划
- 15条物料需求预测记录
- 3个采购订单
- 1个结算单

### API接口概览

| 模块 | 接口前缀 | 功能 |
|------|----------|------|
| 料仓与库存 | /api/silos | 料仓CRUD、库存调整、库存记录、低库存预警 |
| 生产计划 | /api/production/plans | 生产计划CRUD、生成物料需求 |
| 物料需求 | /api/production/demands | 需求查询、待处理需求 |
| 供应商 | /api/suppliers | 供应商CRUD、评级管理 |
| 采购订单 | /api/suppliers/orders | 订单CRUD、状态管理 |
| 结算管理 | /api/settlements | 结算单CRUD、付款管理 |
| 仪表盘 | /api/dashboard | 统计数据 |

### 注意事项

1. 前端配置了API代理，所有 `/api` 请求会自动转发到 `http://localhost:8000`
2. 数据库文件 `inventory_system.db` 会在首次启动时自动创建
3. 确保前后端服务同时运行才能正常访问所有功能
4. 生产环境建议使用 PostgreSQL 或 MySQL 替代 SQLite
