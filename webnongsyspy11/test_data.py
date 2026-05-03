"""
测试数据生成脚本
用于初始化数据库并生成用于功能测试的数据
"""
import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import engine, SessionLocal, init_db
import models
import crud
import schemas


def generate_test_data():
    """
    生成测试数据
    """
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("开始生成测试数据...")
        print("=" * 50)
        
        print("\n[1/7] 创建农资分类...")
        categories_data = [
            {"name": "种子", "code": "SEED", "description": "各类作物种子，包括水稻、小麦、玉米、蔬菜等"},
            {"name": "肥料", "code": "FERT", "description": "化肥、有机肥、复合肥等"},
            {"name": "农药", "code": "PEST", "description": "杀虫剂、杀菌剂、除草剂等"},
            {"name": "农膜", "code": "FILM", "description": "地膜、棚膜等农用塑料薄膜"}
        ]
        
        for cat_data in categories_data:
            existing = db.query(models.Category).filter(models.Category.code == cat_data["code"]).first()
            if not existing:
                category = models.Category(**cat_data)
                db.add(category)
                print(f"  [OK] 创建分类: {cat_data['name']} ({cat_data['code']})")
            else:
                print(f"  [INFO] 分类已存在: {cat_data['name']}")
        
        db.commit()
        
        print("\n[2/7] 创建供应商...")
        suppliers_data = [
            {"name": "绿源农资有限公司", "contact_person": "张经理", "phone": "13800138001", "address": "北京市朝阳区农资批发市场A区12号", "remark": "主营种子和肥料，长期合作供应商"},
            {"name": "丰收农业科技公司", "contact_person": "李经理", "phone": "13800138002", "address": "上海市浦东新区农业园区B栋", "remark": "专业农药供应商，资质齐全"},
            {"name": "金土地农资服务中心", "contact_person": "王经理", "phone": "13800138003", "address": "广州市白云区农资街88号", "remark": "综合供应商，价格优惠"}
        ]
        
        for sup_data in suppliers_data:
            existing = db.query(models.Supplier).filter(models.Supplier.name == sup_data["name"]).first()
            if not existing:
                supplier = models.Supplier(**sup_data)
                db.add(supplier)
                print(f"  [OK] 创建供应商: {sup_data['name']}")
            else:
                print(f"  [INFO] 供应商已存在: {sup_data['name']}")
        
        db.commit()
        
        print("\n[3/7] 创建农资...")
        seed_category = db.query(models.Category).filter(models.Category.code == "SEED").first()
        fert_category = db.query(models.Category).filter(models.Category.code == "FERT").first()
        pest_category = db.query(models.Category).filter(models.Category.code == "PEST").first()
        film_category = db.query(models.Category).filter(models.Category.code == "FILM").first()
        
        supplies_data = [
            {"name": "水稻种子-籼稻950", "category_id": seed_category.id if seed_category else 1, "unit": "公斤", "specification": "1kg/袋", "brand": "隆平高科", "warning_threshold": 10.0, "remark": "高产杂交水稻品种"},
            {"name": "小麦种子-济麦22", "category_id": seed_category.id if seed_category else 1, "unit": "公斤", "specification": "25kg/袋", "brand": "山农种业", "warning_threshold": 15.0, "remark": "冬小麦优良品种"},
            {"name": "玉米种子-登海605", "category_id": seed_category.id if seed_category else 1, "unit": "公斤", "specification": "4200粒/袋", "brand": "登海种业", "warning_threshold": 8.0, "remark": "夏播玉米品种"},
            {"name": "尿素(46%)", "category_id": fert_category.id if fert_category else 2, "unit": "袋", "specification": "50kg/袋", "brand": "心连心", "warning_threshold": 20.0, "remark": "氮肥，含氮量46%"},
            {"name": "复合肥(15-15-15)", "category_id": fert_category.id if fert_category else 2, "unit": "袋", "specification": "50kg/袋", "brand": "史丹利", "warning_threshold": 15.0, "remark": "氮磷钾平衡肥"},
            {"name": "磷酸二铵", "category_id": fert_category.id if fert_category else 2, "unit": "袋", "specification": "50kg/袋", "brand": "云天化", "warning_threshold": 10.0, "remark": "高磷复合肥"},
            {"name": "草甘膦除草剂", "category_id": pest_category.id if pest_category else 3, "unit": "瓶", "specification": "1L/瓶", "brand": "陶氏益农", "warning_threshold": 5.0, "remark": "广谱除草剂，注意安全间隔期"},
            {"name": "吡虫啉杀虫剂", "category_id": pest_category.id if pest_category else 3, "unit": "袋", "specification": "10g/袋", "brand": "拜耳", "warning_threshold": 20.0, "remark": "防治蚜虫、飞虱等刺吸式口器害虫"},
            {"name": "多菌灵杀菌剂", "category_id": pest_category.id if pest_category else 3, "unit": "瓶", "specification": "500g/瓶", "brand": "蓝丰", "warning_threshold": 10.0, "remark": "广谱杀菌剂"},
            {"name": "黑色地膜", "category_id": film_category.id if film_category else 4, "unit": "卷", "specification": "1.5m×500m", "brand": "华盾", "warning_threshold": 5.0, "remark": "厚度0.008mm，黑色防草"},
            {"name": "白色棚膜", "category_id": film_category.id if film_category else 4, "unit": "卷", "specification": "8m×100m", "brand": "宝利德", "warning_threshold": 3.0, "remark": "厚度0.10mm，大棚专用"}
        ]
        
        for sup_data in supplies_data:
            existing = db.query(models.Supply).filter(models.Supply.name == sup_data["name"]).first()
            if not existing:
                supply = models.Supply(**sup_data)
                db.add(supply)
                print(f"  [OK] 创建农资: {sup_data['name']}")
            else:
                print(f"  [INFO] 农资已存在: {sup_data['name']}")
        
        db.commit()
        
        print("\n[4/7] 创建地块...")
        plots_data = [
            {"name": "东河地块1号", "location": "村东头", "area": 50.0, "soil_type": "壤土", "remark": "主要种植水稻"},
            {"name": "东河地块2号", "location": "村东头", "area": 35.0, "soil_type": "壤土", "remark": "种植小麦和玉米轮作"},
            {"name": "西河地块1号", "location": "村西河边", "area": 40.0, "soil_type": "水稻土", "remark": "优质稻田，灌溉方便"},
            {"name": "北坡地块", "location": "村北坡地", "area": 25.0, "soil_type": "褐土", "remark": "坡地，适合种植耐旱作物"},
            {"name": "大棚园区", "location": "村南园区", "area": 15.0, "soil_type": "壤土", "remark": "设施农业大棚区"}
        ]
        
        for plot_data in plots_data:
            existing = db.query(models.Plot).filter(models.Plot.name == plot_data["name"]).first()
            if not existing:
                plot = models.Plot(**plot_data)
                db.add(plot)
                print(f"  [OK] 创建地块: {plot_data['name']}")
            else:
                print(f"  [INFO] 地块已存在: {plot_data['name']}")
        
        db.commit()
        
        print("\n[5/7] 创建作物...")
        crops_data = [
            {"name": "水稻", "variety": "籼稻", "growth_cycle": 120, "remark": "主要粮食作物"},
            {"name": "小麦", "variety": "冬小麦", "growth_cycle": 230, "remark": "冬小麦，秋播夏收"},
            {"name": "玉米", "variety": "夏玉米", "growth_cycle": 105, "remark": "夏播玉米"},
            {"name": "西红柿", "variety": "粉果番茄", "growth_cycle": 90, "remark": "大棚种植，早熟品种"},
            {"name": "黄瓜", "variety": "津优系列", "growth_cycle": 60, "remark": "大棚种植，耐高温"},
            {"name": "辣椒", "variety": "朝天椒", "growth_cycle": 120, "remark": "露地种植，抗病品种"}
        ]
        
        for crop_data in crops_data:
            existing = db.query(models.Crop).filter(models.Crop.name == crop_data["name"]).first()
            if not existing:
                crop = models.Crop(**crop_data)
                db.add(crop)
                print(f"  [OK] 创建作物: {crop_data['name']}")
            else:
                print(f"  [INFO] 作物已存在: {crop_data['name']}")
        
        db.commit()
        
        print("\n[6/7] 创建采购记录和库存...")
        supplier1 = db.query(models.Supplier).filter(models.Supplier.name == "绿源农资有限公司").first()
        supplier2 = db.query(models.Supplier).filter(models.Supplier.name == "丰收农业科技公司").first()
        supplier3 = db.query(models.Supplier).filter(models.Supplier.name == "金土地农资服务中心").first()
        
        today = date.today()
        
        purchase_data_list = [
            {"supplier_id": supplier1.id if supplier1 else 1, "supply_name": "水稻种子-籼稻950", "purchase_date": today - timedelta(days=30), "quantity": 100.0, "unit_price": 25.0, "batch_no": "B20260401001", "expiry_date": today + timedelta(days=365)},
            {"supplier_id": supplier1.id if supplier1 else 1, "supply_name": "尿素(46%)", "purchase_date": today - timedelta(days=25), "quantity": 50.0, "unit_price": 120.0, "batch_no": "B20260405001", "expiry_date": today + timedelta(days=730)},
            {"supplier_id": supplier2.id if supplier2 else 2, "supply_name": "复合肥(15-15-15)", "purchase_date": today - timedelta(days=20), "quantity": 30.0, "unit_price": 150.0, "batch_no": "B20260410001", "expiry_date": today + timedelta(days=730)},
            {"supplier_id": supplier2.id if supplier2 else 2, "supply_name": "草甘膦除草剂", "purchase_date": today - timedelta(days=15), "quantity": 20.0, "unit_price": 45.0, "batch_no": "B20260415001", "expiry_date": today + timedelta(days=730)},
            {"supplier_id": supplier3.id if supplier3 else 3, "supply_name": "黑色地膜", "purchase_date": today - timedelta(days=10), "quantity": 10.0, "unit_price": 180.0, "batch_no": "B20260420001", "expiry_date": today + timedelta(days=1095)},
            {"supplier_id": supplier1.id if supplier1 else 1, "supply_name": "吡虫啉杀虫剂", "purchase_date": today - timedelta(days=5), "quantity": 50.0, "unit_price": 3.5, "batch_no": "B20260425001", "expiry_date": today + timedelta(days=730)},
            {"supplier_id": supplier2.id if supplier2 else 2, "supply_name": "多菌灵杀菌剂", "purchase_date": today - timedelta(days=3), "quantity": 15.0, "unit_price": 28.0, "batch_no": "B20260427001", "expiry_date": today + timedelta(days=730)},
        ]
        
        for pur_data in purchase_data_list:
            supply = db.query(models.Supply).filter(models.Supply.name == pur_data["supply_name"]).first()
            if supply:
                existing = db.query(models.Purchase).filter(models.Purchase.batch_no == pur_data["batch_no"]).first()
                if not existing:
                    purchase_data = schemas.PurchaseCreate(
                        supplier_id=pur_data["supplier_id"],
                        supply_id=supply.id,
                        purchase_date=pur_data["purchase_date"],
                        quantity=pur_data["quantity"],
                        unit_price=pur_data["unit_price"],
                        batch_no=pur_data["batch_no"],
                        expiry_date=pur_data["expiry_date"]
                    )
                    crud.create_purchase(db, purchase_data)
                    print(f"  [OK] 创建采购: {pur_data['supply_name']} - {pur_data['batch_no']}")
                else:
                    print(f"  [INFO] 采购已存在: {pur_data['supply_name']}")
        
        print("\n[7/7] 创建使用记录（形成投入品-地块-作物闭环）...")
        
        plot1 = db.query(models.Plot).filter(models.Plot.name == "东河地块1号").first()
        plot3 = db.query(models.Plot).filter(models.Plot.name == "西河地块1号").first()
        plot5 = db.query(models.Plot).filter(models.Plot.name == "大棚园区").first()
        
        crop_rice = db.query(models.Crop).filter(models.Crop.name == "水稻").first()
        crop_tomato = db.query(models.Crop).filter(models.Crop.name == "西红柿").first()
        crop_cucumber = db.query(models.Crop).filter(models.Crop.name == "黄瓜").first()
        
        usage_data_list = [
            {"supply_name": "水稻种子-籼稻950", "plot": plot1, "crop": crop_rice, "quantity": 25.0, "usage_date": today - timedelta(days=28), "usage_method": "撒施", "operator": "李师傅", "remark": "水稻育秧用种"},
            {"supply_name": "尿素(46%)", "plot": plot1, "crop": crop_rice, "quantity": 10.0, "usage_date": today - timedelta(days=20), "usage_method": "撒施", "operator": "李师傅", "remark": "水稻基肥"},
            {"supply_name": "复合肥(15-15-15)", "plot": plot3, "crop": crop_rice, "quantity": 8.0, "usage_date": today - timedelta(days=15), "usage_method": "撒施", "operator": "王师傅", "remark": "水稻追肥"},
            {"supply_name": "草甘膦除草剂", "plot": plot1, "crop": crop_rice, "quantity": 3.0, "usage_date": today - timedelta(days=10), "usage_method": "叶面喷施", "operator": "李师傅", "remark": "播前除草"},
            {"supply_name": "吡虫啉杀虫剂", "plot": plot1, "crop": crop_rice, "quantity": 10.0, "usage_date": today - timedelta(days=5), "usage_method": "叶面喷施", "operator": "李师傅", "remark": "防治稻飞虱"},
            {"supply_name": "黑色地膜", "plot": plot5, "crop": crop_tomato, "quantity": 2.0, "usage_date": today - timedelta(days=12), "usage_method": "覆盖", "operator": "张师傅", "remark": "西红柿定植覆盖"},
            {"supply_name": "复合肥(15-15-15)", "plot": plot5, "crop": crop_tomato, "quantity": 3.0, "usage_date": today - timedelta(days=10), "usage_method": "穴施", "operator": "张师傅", "remark": "西红柿基肥"},
            {"supply_name": "多菌灵杀菌剂", "plot": plot5, "crop": crop_tomato, "quantity": 2.0, "usage_date": today - timedelta(days=3), "usage_method": "叶面喷施", "operator": "张师傅", "remark": "防治病害"},
            {"supply_name": "尿素(46%)", "plot": plot5, "crop": crop_cucumber, "quantity": 2.0, "usage_date": today - timedelta(days=8), "usage_method": "随水冲施", "operator": "张师傅", "remark": "黄瓜追肥"},
        ]
        
        for use_data in usage_data_list:
            supply = db.query(models.Supply).filter(models.Supply.name == use_data["supply_name"]).first()
            if supply and use_data["plot"] and use_data["crop"]:
                inventories = crud.get_inventory_by_supply(db, supply.id)
                if inventories and inventories[0].quantity >= use_data["quantity"]:
                    usage_data_dict = {
                        "supply_id": supply.id,
                        "plot_id": use_data["plot"].id,
                        "crop_id": use_data["crop"].id,
                        "quantity": use_data["quantity"],
                        "usage_date": use_data["usage_date"],
                        "usage_method": use_data["usage_method"],
                        "operator": use_data["operator"],
                        "remark": use_data["remark"]
                    }
                    crud.create_usage_record_fifo(db, usage_data_dict)
                    print(f"  [OK] 创建使用记录: {use_data['supply_name']} -> {use_data['plot'].name} -> {use_data['crop'].name}")
        
        print("\n" + "=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        print("\n数据统计:")
        print(f"  - 分类: {db.query(models.Category).count()} 种")
        print(f"  - 供应商: {db.query(models.Supplier).count()} 家")
        print(f"  - 农资: {db.query(models.Supply).count()} 种")
        print(f"  - 地块: {db.query(models.Plot).count()} 个")
        print(f"  - 作物: {db.query(models.Crop).count()} 种")
        print(f"  - 采购记录: {db.query(models.Purchase).count()} 条")
        print(f"  - 库存记录: {db.query(models.Inventory).count()} 条")
        print(f"  - 使用记录: {db.query(models.UsageRecord).count()} 条")
        
        print("\n[OK] 系统已准备就绪，可以进行功能测试！")
        print("   请运行 `python main.py` 启动服务器")
        
    except Exception as e:
        print(f"\n[ERROR] 生成测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    generate_test_data()
