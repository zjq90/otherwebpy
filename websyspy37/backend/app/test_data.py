"""
测试数据生成模块
用于生成各模块的测试数据
"""
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models import sales, production, inventory, finance, hr


def generate_customers(db: Session):
    """
    生成客户测试数据
    """
    customers = [
        {
            "name": "阿里巴巴科技有限公司",
            "contact_person": "马云",
            "phone": "13800138001",
            "email": "mayun@alibaba.com",
            "address": "杭州市余杭区文一西路969号"
        },
        {
            "name": "腾讯科技有限公司",
            "contact_person": "马化腾",
            "phone": "13800138002",
            "email": "mht@tencent.com",
            "address": "深圳市南山区科技园"
        },
        {
            "name": "百度在线网络技术有限公司",
            "contact_person": "李彦宏",
            "phone": "13800138003",
            "email": "liyanhong@baidu.com",
            "address": "北京市海淀区上地十街10号"
        },
        {
            "name": "京东集团",
            "contact_person": "刘强东",
            "phone": "13800138004",
            "email": "liuqiangdong@jd.com",
            "address": "北京市亦庄经济技术开发区"
        },
        {
            "name": "字节跳动科技有限公司",
            "contact_person": "张一鸣",
            "phone": "13800138005",
            "email": "zhangyiming@bytedance.com",
            "address": "北京市海淀区知春路甲48号"
        }
    ]
    
    for customer_data in customers:
        customer = sales.Customer(**customer_data)
        db.add(customer)
    
    db.commit()
    print(f"已生成 {len(customers)} 条客户测试数据")


def generate_products(db: Session):
    """
    生成产品测试数据
    """
    products = [
        {
            "product_no": "PROD001",
            "name": "智能笔记本电脑",
            "specification": "15.6英寸 i7 16G 512G",
            "unit": "台",
            "cost_price": 4500.00,
            "selling_price": 6999.00,
            "description": "高性能商务笔记本电脑，适合办公和设计使用"
        },
        {
            "product_no": "PROD002",
            "name": "无线蓝牙耳机",
            "specification": "降噪版 白色",
            "unit": "个",
            "cost_price": 180.00,
            "selling_price": 399.00,
            "description": "主动降噪，续航30小时"
        },
        {
            "product_no": "PROD003",
            "name": "智能手表",
            "specification": "GPS版 42mm",
            "unit": "块",
            "cost_price": 1200.00,
            "selling_price": 2499.00,
            "description": "心率监测，GPS定位，50米防水"
        },
        {
            "product_no": "PROD004",
            "name": "机械键盘",
            "specification": "RGB背光 青轴",
            "unit": "个",
            "cost_price": 250.00,
            "selling_price": 499.00,
            "description": "全键无冲，铝合金面板"
        },
        {
            "product_no": "PROD005",
            "name": "27寸4K显示器",
            "specification": "IPS面板 60Hz",
            "unit": "台",
            "cost_price": 1800.00,
            "selling_price": 3299.00,
            "description": "4K分辨率，100% sRGB色域"
        }
    ]
    
    for product_data in products:
        product = production.Product(**product_data)
        db.add(product)
    
    db.commit()
    print(f"已生成 {len(products)} 条产品测试数据")


def generate_warehouses(db: Session):
    """
    生成仓库测试数据
    """
    warehouses = [
        {
            "warehouse_no": "WH001",
            "name": "北京中心仓库",
            "location": "北京市朝阳区",
            "manager": "张三",
            "phone": "010-12345678",
            "description": "主要存储电子产品"
        },
        {
            "warehouse_no": "WH002",
            "name": "上海分仓库",
            "location": "上海市浦东新区",
            "manager": "李四",
            "phone": "021-87654321",
            "description": "华东地区配送中心"
        },
        {
            "warehouse_no": "WH003",
            "name": "深圳保税仓",
            "location": "深圳市福田区",
            "manager": "王五",
            "phone": "0755-11112222",
            "description": "进出口货物存储"
        }
    ]
    
    for warehouse_data in warehouses:
        warehouse = inventory.Warehouse(**warehouse_data)
        db.add(warehouse)
    
    db.commit()
    print(f"已生成 {len(warehouses)} 条仓库测试数据")


def generate_departments(db: Session):
    """
    生成部门测试数据
    """
    departments = [
        {
            "dept_no": "DEPT001",
            "name": "总经办",
            "manager": "陈总",
            "phone": "010-88888888",
            "description": "公司最高管理层"
        },
        {
            "dept_no": "DEPT002",
            "name": "销售部",
            "manager": "王经理",
            "phone": "010-88888801",
            "description": "负责产品销售和客户关系维护"
        },
        {
            "dept_no": "DEPT003",
            "name": "生产部",
            "manager": "李经理",
            "phone": "010-88888802",
            "description": "负责产品生产和质量控制"
        },
        {
            "dept_no": "DEPT004",
            "name": "财务部",
            "manager": "赵经理",
            "phone": "010-88888803",
            "description": "负责公司财务管理"
        },
        {
            "dept_no": "DEPT005",
            "name": "人事部",
            "manager": "刘经理",
            "phone": "010-88888804",
            "description": "负责人力资源管理"
        }
    ]
    
    for dept_data in departments:
        dept = hr.Department(**dept_data)
        db.add(dept)
    
    db.commit()
    print(f"已生成 {len(departments)} 条部门测试数据")


def generate_positions(db: Session):
    """
    生成职位测试数据
    """
    positions = [
        {
            "position_no": "POS001",
            "name": "总经理",
            "level": 1,
            "base_salary": 50000.00,
            "description": "公司最高负责人"
        },
        {
            "position_no": "POS002",
            "name": "部门经理",
            "level": 2,
            "base_salary": 25000.00,
            "description": "各部门负责人"
        },
        {
            "position_no": "POS003",
            "name": "销售代表",
            "level": 3,
            "base_salary": 8000.00,
            "description": "负责产品销售"
        },
        {
            "position_no": "POS004",
            "name": "生产工人",
            "level": 4,
            "base_salary": 6000.00,
            "description": "负责产品生产"
        },
        {
            "position_no": "POS005",
            "name": "会计",
            "level": 3,
            "base_salary": 10000.00,
            "description": "负责财务核算"
        }
    ]
    
    for pos_data in positions:
        position = hr.Position(**pos_data)
        db.add(position)
    
    db.commit()
    print(f"已生成 {len(positions)} 条职位测试数据")


def generate_employees(db: Session):
    """
    生成员工测试数据
    """
    employees = [
        {
            "employee_no": "EMP001",
            "name": "陈建国",
            "gender": "男",
            "birthday": date(1970, 5, 15),
            "id_card": "110101197005150011",
            "phone": "13900139001",
            "email": "chenjg@company.com",
            "address": "北京市朝阳区建国路88号",
            "department_id": 1,
            "position_id": 1,
            "entry_date": date(2000, 1, 1),
            "status": "在职",
            "salary": 50000.00
        },
        {
            "employee_no": "EMP002",
            "name": "王美丽",
            "gender": "女",
            "birthday": date(1985, 8, 20),
            "id_card": "110101198508200022",
            "phone": "13900139002",
            "email": "wangml@company.com",
            "address": "北京市海淀区中关村大街1号",
            "department_id": 2,
            "position_id": 2,
            "entry_date": date(2010, 3, 15),
            "status": "在职",
            "salary": 25000.00
        },
        {
            "employee_no": "EMP003",
            "name": "李明",
            "gender": "男",
            "birthday": date(1988, 12, 5),
            "id_card": "110101198812050033",
            "phone": "13900139003",
            "email": "liming@company.com",
            "address": "北京市丰台区丰台路5号",
            "department_id": 3,
            "position_id": 2,
            "entry_date": date(2012, 6, 20),
            "status": "在职",
            "salary": 25000.00
        },
        {
            "employee_no": "EMP004",
            "name": "赵小红",
            "gender": "女",
            "birthday": date(1990, 3, 18),
            "id_card": "110101199003180044",
            "phone": "13900139004",
            "email": "zhaoxh@company.com",
            "address": "北京市西城区西单大街10号",
            "department_id": 4,
            "position_id": 5,
            "entry_date": date(2015, 9, 1),
            "status": "在职",
            "salary": 10000.00
        },
        {
            "employee_no": "EMP005",
            "name": "刘阳",
            "gender": "男",
            "birthday": date(1992, 7, 22),
            "id_card": "110101199207220055",
            "phone": "13900139005",
            "email": "liuyang@company.com",
            "address": "北京市东城区东长安街1号",
            "department_id": 5,
            "position_id": 3,
            "entry_date": date(2018, 2, 14),
            "status": "在职",
            "salary": 8000.00
        }
    ]
    
    for emp_data in employees:
        employee = hr.Employee(**emp_data)
        db.add(employee)
    
    db.commit()
    print(f"已生成 {len(employees)} 条员工测试数据")


def generate_accounts(db: Session):
    """
    生成账户测试数据
    """
    accounts = [
        {
            "account_no": "ACC001",
            "name": "工商银行基本账户",
            "type": "银行账户",
            "bank_name": "中国工商银行北京分行",
            "bank_account": "6222020200012345678",
            "balance": 500000.00,
            "description": "公司主要经营账户"
        },
        {
            "account_no": "ACC002",
            "name": "建设银行一般账户",
            "type": "银行账户",
            "bank_name": "中国建设银行北京分行",
            "bank_account": "6227000200012345678",
            "balance": 200000.00,
            "description": "备用金账户"
        },
        {
            "account_no": "ACC003",
            "name": "现金账户",
            "type": "现金账户",
            "balance": 50000.00,
            "description": "日常零星开支"
        }
    ]
    
    for acc_data in accounts:
        account = finance.Account(**acc_data)
        db.add(account)
    
    db.commit()
    print(f"已生成 {len(accounts)} 条账户测试数据")


def generate_inventories(db: Session):
    """
    生成库存测试数据
    """
    inventories = [
        {
            "warehouse_id": 1,
            "product_id": 1,
            "quantity": 100,
            "min_quantity": 10,
            "max_quantity": 500
        },
        {
            "warehouse_id": 1,
            "product_id": 2,
            "quantity": 500,
            "min_quantity": 50,
            "max_quantity": 2000
        },
        {
            "warehouse_id": 1,
            "product_id": 3,
            "quantity": 200,
            "min_quantity": 20,
            "max_quantity": 1000
        },
        {
            "warehouse_id": 2,
            "product_id": 1,
            "quantity": 50,
            "min_quantity": 10,
            "max_quantity": 200
        },
        {
            "warehouse_id": 2,
            "product_id": 4,
            "quantity": 300,
            "min_quantity": 30,
            "max_quantity": 1500
        }
    ]
    
    for inv_data in inventories:
        inventory_obj = inventory.Inventory(**inv_data)
        db.add(inventory_obj)
    
    db.commit()
    print(f"已生成 {len(inventories)} 条库存测试数据")


def generate_all_test_data(db: Session):
    """
    生成所有测试数据
    """
    print("开始生成测试数据...")
    
    # 按依赖顺序生成数据
    generate_customers(db)
    generate_products(db)
    generate_warehouses(db)
    generate_departments(db)
    generate_positions(db)
    generate_employees(db)
    generate_accounts(db)
    generate_inventories(db)
    
    print("测试数据生成完成！")
