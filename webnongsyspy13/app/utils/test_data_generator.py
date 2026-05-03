"""
测试数据生成模块
用于生成示例数据，方便系统功能测试
"""
from datetime import date, timedelta, datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app import models, crud
from app.utils.qrcode_generator import generate_qrcode_for_batch


def generate_test_products(db: Session) -> Dict[str, Any]:
    """
    生成测试产品数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    products_data = [
        {
            "name": "有机西红柿",
            "category": "蔬菜",
            "description": "采用有机种植方式，无农药无化肥，绿色健康",
            "origin": "山东省寿光市蔬菜基地",
            "supplier": "绿源有机农场"
        },
        {
            "name": "无公害黄瓜",
            "category": "蔬菜",
            "description": "严格按照无公害标准种植，品质有保障",
            "origin": "河北省保定市蔬菜基地",
            "supplier": "惠农蔬菜专业合作社"
        },
        {
            "name": "红富士苹果",
            "category": "水果",
            "description": "产自烟台，口感脆甜，果香浓郁",
            "origin": "山东省烟台市栖霞区",
            "supplier": "烟台苹果集团"
        },
        {
            "name": "赣南脐橙",
            "category": "水果",
            "description": "赣南特产，果肉细嫩，酸甜可口",
            "origin": "江西省赣州市",
            "supplier": "赣南脐橙合作社"
        },
        {
            "name": "有机大米",
            "category": "谷物",
            "description": "东北黑土地种植，一年一季，营养丰富",
            "origin": "黑龙江省五常市",
            "supplier": "五常大米集团"
        }
    ]
    
    created_count = 0
    created_products = []
    
    for product_data in products_data:
        existing = crud.product.get_by_name(db, name=product_data["name"])
        if existing is None:
            product = crud.product.create(db, obj_in=product_data)
            created_products.append(product)
            created_count += 1
    
    return {
        "created_count": created_count,
        "products": created_products
    }


def generate_test_batches(db: Session) -> Dict[str, Any]:
    """
    生成测试批次数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    all_products = crud.product.get_multi(db, limit=100)
    if not all_products:
        return {"created_count": 0, "batches": [], "message": "没有产品数据，请先生成产品"}
    
    today = date.today()
    created_count = 0
    created_batches = []
    
    batches_data = [
        {
            "batch_number": "BATCH20240101001",
            "quantity": 5000,
            "unit": "公斤",
            "planting_date": today - timedelta(days=90),
            "harvest_date": today - timedelta(days=10)
        },
        {
            "batch_number": "BATCH20240101002",
            "quantity": 3000,
            "unit": "公斤",
            "planting_date": today - timedelta(days=120),
            "harvest_date": today - timedelta(days=30)
        },
        {
            "batch_number": "BATCH20240102001",
            "quantity": 8000,
            "unit": "公斤",
            "planting_date": today - timedelta(days=60),
            "harvest_date": None
        },
        {
            "batch_number": "BATCH20240103001",
            "quantity": 10000,
            "unit": "公斤",
            "planting_date": today - timedelta(days=180),
            "harvest_date": today - timedelta(days=60)
        }
    ]
    
    for i, batch_data in enumerate(batches_data):
        if i < len(all_products):
            batch_data["product_id"] = all_products[i].id
            
            existing = crud.batch.get_by_batch_number(db, batch_number=batch_data["batch_number"])
            if existing is None:
                batch = crud.batch.create(db, obj_in=batch_data)
                batch = generate_qrcode_for_batch(db, batch_id=batch.id)
                created_batches.append(batch)
                created_count += 1
    
    return {
        "created_count": created_count,
        "batches": created_batches
    }


def generate_test_planting_records(db: Session) -> Dict[str, Any]:
    """
    生成测试种植记录数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    all_batches = crud.batch.get_multi(db, limit=100)
    if not all_batches:
        return {"created_count": 0, "records": [], "message": "没有批次数据"}
    
    operation_types = ["播种", "施肥", "浇水", "除草", "病虫害防治", "整枝", "搭架", "采收准备"]
    operators = ["张三", "李四", "王五", "赵六", "钱七"]
    
    created_count = 0
    created_records = []
    
    for batch in all_batches:
        existing_records = crud.planting_record.get_by_batch_id(db, batch_id=batch.id, limit=1)
        if existing_records:
            continue
        
        if batch.planting_date:
            start_date = batch.planting_date
        else:
            start_date = date.today() - timedelta(days=90)
        
        for i in range(5):
            record_date = start_date + timedelta(days=i * 15)
            
            record_data = {
                "batch_id": batch.id,
                "record_date": record_date,
                "operation_type": operation_types[i % len(operation_types)],
                "description": f"执行{operation_types[i % len(operation_types)]}操作，根据作物生长情况进行针对性管理",
                "operator": operators[i % len(operators)],
                "remarks": f"第{i+1}次田间操作记录"
            }
            
            record = crud.planting_record.create(db, obj_in=record_data)
            created_records.append(record)
            created_count += 1
    
    return {
        "created_count": created_count,
        "records": created_records
    }


def generate_test_agrochemical_usages(db: Session) -> Dict[str, Any]:
    """
    生成测试农资使用记录数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    all_batches = crud.batch.get_multi(db, limit=100)
    if not all_batches:
        return {"created_count": 0, "usages": [], "message": "没有批次数据"}
    
    chemicals_data = [
        {"type": "农药", "name": "多菌灵", "quantity": 0.5, "unit": "公斤/亩", "method": "喷雾", "interval": 14},
        {"type": "农药", "name": "百菌清", "quantity": 0.3, "unit": "公斤/亩", "method": "喷雾", "interval": 7},
        {"type": "化肥", "name": "尿素", "quantity": 15, "unit": "公斤/亩", "method": "撒施", "interval": 0},
        {"type": "化肥", "name": "复合肥", "quantity": 20, "unit": "公斤/亩", "method": "穴施", "interval": 0},
        {"type": "除草剂", "name": "草甘膦", "quantity": 0.2, "unit": "升/亩", "method": "定向喷雾", "interval": 30}
    ]
    
    operators = ["张三", "李四", "王五"]
    
    created_count = 0
    created_usages = []
    
    for batch in all_batches:
        existing_usages = crud.agrochemical_usage.get_by_batch_id(db, batch_id=batch.id, limit=1)
        if existing_usages:
            continue
        
        if batch.planting_date:
            start_date = batch.planting_date
        else:
            start_date = date.today() - timedelta(days=90)
        
        for i, chemical in enumerate(chemicals_data[:3]):
            usage_date = start_date + timedelta(days=i * 20 + 10)
            
            usage_data = {
                "batch_id": batch.id,
                "usage_date": usage_date,
                "chemical_type": chemical["type"],
                "chemical_name": chemical["name"],
                "quantity": chemical["quantity"],
                "unit": chemical["unit"],
                "usage_method": chemical["method"],
                "safety_interval": chemical["interval"],
                "operator": operators[i % len(operators)],
                "remarks": f"按照标准操作规程使用{chemical['name']}"
            }
            
            usage = crud.agrochemical_usage.create(db, obj_in=usage_data)
            created_usages.append(usage)
            created_count += 1
    
    return {
        "created_count": created_count,
        "usages": created_usages
    }


def generate_test_results(db: Session) -> Dict[str, Any]:
    """
    生成测试检测结果数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    all_batches = crud.batch.get_multi(db, limit=100)
    if not all_batches:
        return {"created_count": 0, "results": [], "message": "没有批次数据"}
    
    test_params = [
        {"item": "农残", "name": "敌敌畏", "value": "0.02 mg/kg", "limit": "0.2 mg/kg", "result": "合格"},
        {"item": "农残", "name": "乐果", "value": "0.01 mg/kg", "limit": "0.1 mg/kg", "result": "合格"},
        {"item": "农残", "name": "马拉硫磷", "value": "0.05 mg/kg", "limit": "0.5 mg/kg", "result": "合格"},
        {"item": "重金属", "name": "铅(Pb)", "value": "0.08 mg/kg", "limit": "0.2 mg/kg", "result": "合格"},
        {"item": "重金属", "name": "镉(Cd)", "value": "0.03 mg/kg", "limit": "0.05 mg/kg", "result": "合格"},
        {"item": "重金属", "name": "砷(As)", "value": "0.04 mg/kg", "limit": "0.2 mg/kg", "result": "合格"},
        {"item": "微生物", "name": "菌落总数", "value": "1.2×10³ CFU/g", "limit": "1.0×10⁴ CFU/g", "result": "合格"},
        {"item": "微生物", "name": "大肠杆菌", "value": "未检出", "limit": "不得检出", "result": "合格"}
    ]
    
    created_count = 0
    created_results = []
    
    for batch in all_batches:
        existing_results = crud.test_result.get_by_batch_id(db, batch_id=batch.id, limit=1)
        if existing_results:
            continue
        
        test_date = date.today() - timedelta(days=5)
        
        for i, param in enumerate(test_params):
            test_type = "自检" if i < 4 else "第三方检测"
            
            result_data = {
                "batch_id": batch.id,
                "test_type": test_type,
                "test_organization": "内部质检中心" if test_type == "自检" else "市农产品质量检测中心",
                "test_date": test_date,
                "test_item": param["item"],
                "parameter_name": param["name"],
                "test_value": param["value"],
                "limit_value": param["limit"],
                "result": param["result"],
                "report_number": f"RPT{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                "tester": "检测员" + str(i + 1),
                "remarks": "符合国家标准要求"
            }
            
            result = crud.test_result.create(db, obj_in=result_data)
            created_results.append(result)
            created_count += 1
    
    return {
        "created_count": created_count,
        "results": created_results
    }


def generate_test_certificates(db: Session) -> Dict[str, Any]:
    """
    生成测试认证证书数据
    包含有效证书和即将过期的证书，用于测试到期提醒功能
    
    Args:
        db: 数据库会话
        
    Returns:
        包含生成统计的字典
    """
    all_products = crud.product.get_multi(db, limit=100)
    if not all_products:
        return {"created_count": 0, "certificates": [], "message": "没有产品数据"}
    
    today = date.today()
    
    certificates_data = [
        {
            "certificate_number": "CERT-GREEN-2024-001",
            "certificate_type": "绿色食品",
            "issuing_organization": "中国绿色食品发展中心",
            "issue_date": today - timedelta(days=365),
            "valid_until": today + timedelta(days=365),
            "status": "有效",
            "holder": "绿源有机农场",
            "scope": "西红柿、黄瓜等蔬菜类产品",
            "remarks": "A级绿色食品认证"
        },
        {
            "certificate_number": "CERT-ORGANIC-2024-001",
            "certificate_type": "有机产品",
            "issuing_organization": "有机食品认证中心",
            "issue_date": today - timedelta(days=700),
            "valid_until": today + timedelta(days=20),
            "status": "即将过期",
            "holder": "烟台苹果集团",
            "scope": "红富士苹果有机种植",
            "remarks": "即将过期，请及时续证"
        },
        {
            "certificate_number": "CERT-POLLUTION-2024-001",
            "certificate_type": "无公害产品",
            "issuing_organization": "农业部农产品质量安全中心",
            "issue_date": today - timedelta(days=180),
            "valid_until": today + timedelta(days=180),
            "status": "有效",
            "holder": "惠农蔬菜专业合作社",
            "scope": "黄瓜、西红柿等无公害蔬菜",
            "remarks": "认证有效期内"
        },
        {
            "certificate_number": "CERT-GEO-2024-001",
            "certificate_type": "地理标志产品",
            "issuing_organization": "国家知识产权局",
            "issue_date": today - timedelta(days=365),
            "valid_until": today + timedelta(days=720),
            "status": "有效",
            "holder": "赣南脐橙合作社",
            "scope": "赣南脐橙地理标志保护产品",
            "remarks": "地理标志产品认证"
        }
    ]
    
    created_count = 0
    created_certificates = []
    
    for i, cert_data in enumerate(certificates_data):
        if i < len(all_products):
            cert_data["product_id"] = all_products[i].id
            
            existing = crud.certificate.get_by_certificate_number(db, certificate_number=cert_data["certificate_number"])
            if existing is None:
                certificate = crud.certificate.create(db, obj_in=cert_data)
                created_certificates.append(certificate)
                created_count += 1
    
    return {
        "created_count": created_count,
        "certificates": created_certificates
    }


def generate_all_test_data(db: Session) -> Dict[str, Any]:
    """
    生成所有测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含所有生成统计的字典
    """
    results = {}
    
    results["products"] = generate_test_products(db)
    results["batches"] = generate_test_batches(db)
    results["planting_records"] = generate_test_planting_records(db)
    results["agrochemical_usages"] = generate_test_agrochemical_usages(db)
    results["test_results"] = generate_test_results(db)
    results["certificates"] = generate_test_certificates(db)
    
    total_created = (
        results["products"]["created_count"] +
        results["batches"]["created_count"] +
        results["planting_records"]["created_count"] +
        results["agrochemical_usages"]["created_count"] +
        results["test_results"]["created_count"] +
        results["certificates"]["created_count"]
    )
    
    results["total_created"] = total_created
    results["message"] = f"测试数据生成完成，共创建 {total_created} 条记录"
    
    return results
