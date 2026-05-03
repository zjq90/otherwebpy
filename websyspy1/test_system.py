"""
系统功能测试模块
用于测试系统的各项功能是否正常工作
"""
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User, Product, Service, Case, Document, KeyApplication
from security import verify_password, get_password_hash


class SystemTester:
    """
    系统功能测试类
    """
    
    def __init__(self):
        self.session = SessionLocal()
        self.test_results = []
        self.passed_count = 0
        self.failed_count = 0
    
    def log(self, message, level="INFO"):
        """
        记录日志
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_result(self, test_name, passed, detail=""):
        """
        记录测试结果
        """
        if passed:
            self.passed_count += 1
            self.log(f"✓ {test_name} 通过", "SUCCESS")
        else:
            self.failed_count += 1
            self.log(f"✗ {test_name} 失败: {detail}", "ERROR")
        
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "detail": detail
        })
    
    def test_database_connection(self):
        """
        测试数据库连接
        """
        try:
            result = self.session.execute("SELECT 1")
            self.test_result("数据库连接测试", True)
            return True
        except Exception as e:
            self.test_result("数据库连接测试", False, str(e))
            return False
    
    def test_user_model(self):
        """
        测试用户模型
        """
        self.log("开始测试用户模型...")
        
        try:
            test_user = User(
                username="test_user_" + str(int(time.time())),
                email=f"test{int(time.time())}@test.com",
                hashed_password=get_password_hash("test123"),
                full_name="测试用户",
                is_active=True,
                is_admin=False
            )
            self.session.add(test_user)
            self.session.commit()
            self.session.refresh(test_user)
            
            self.test_result("用户创建测试", test_user.id is not None)
            
            user_from_db = self.session.query(User).filter(User.id == test_user.id).first()
            self.test_result("用户查询测试", user_from_db is not None)
            
            self.test_result("密码验证测试", verify_password("test123", user_from_db.hashed_password))
            
            user_from_db.full_name = "更新后的测试用户"
            self.session.commit()
            self.session.refresh(user_from_db)
            self.test_result("用户更新测试", user_from_db.full_name == "更新后的测试用户")
            
            self.session.delete(user_from_db)
            self.session.commit()
            user_deleted = self.session.query(User).filter(User.id == test_user.id).first()
            self.test_result("用户删除测试", user_deleted is None)
            
            return True
            
        except Exception as e:
            self.test_result("用户模型测试", False, str(e))
            return False
    
    def test_product_model(self):
        """
        测试产品模型
        """
        self.log("开始测试产品模型...")
        
        try:
            test_product = Product(
                name="测试产品",
                short_desc="这是一个测试产品的简短描述",
                description="这是测试产品的详细描述",
                price="999.00",
                category="测试分类",
                is_active=True,
                sort_order=1
            )
            self.session.add(test_product)
            self.session.commit()
            self.session.refresh(test_product)
            
            self.test_result("产品创建测试", test_product.id is not None)
            
            product_from_db = self.session.query(Product).filter(Product.id == test_product.id).first()
            self.test_result("产品查询测试", product_from_db is not None)
            
            self.session.delete(product_from_db)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.test_result("产品模型测试", False, str(e))
            return False
    
    def test_service_model(self):
        """
        测试服务模型
        """
        self.log("开始测试服务模型...")
        
        try:
            test_service = Service(
                name="测试服务",
                short_desc="这是测试服务的简短描述",
                description="这是测试服务的详细描述",
                icon="bi bi-test",
                is_active=True,
                sort_order=1
            )
            self.session.add(test_service)
            self.session.commit()
            self.session.refresh(test_service)
            
            self.test_result("服务创建测试", test_service.id is not None)
            
            service_from_db = self.session.query(Service).filter(Service.id == test_service.id).first()
            self.test_result("服务查询测试", service_from_db is not None)
            
            self.session.delete(service_from_db)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.test_result("服务模型测试", False, str(e))
            return False
    
    def test_case_model(self):
        """
        测试案例模型
        """
        self.log("开始测试案例模型...")
        
        try:
            test_case = Case(
                title="测试案例",
                short_desc="这是测试案例的简短描述",
                description="这是测试案例的详细描述",
                client="测试客户",
                category="测试行业",
                is_featured=True,
                is_active=True,
                sort_order=1
            )
            self.session.add(test_case)
            self.session.commit()
            self.session.refresh(test_case)
            
            self.test_result("案例创建测试", test_case.id is not None)
            
            case_from_db = self.session.query(Case).filter(Case.id == test_case.id).first()
            self.test_result("案例查询测试", case_from_db is not None)
            
            self.session.delete(case_from_db)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.test_result("案例模型测试", False, str(e))
            return False
    
    def test_document_model(self):
        """
        测试文档模型
        """
        self.log("开始测试文档模型...")
        
        try:
            test_doc = Document(
                title="测试文档",
                short_desc="这是测试文档的简短描述",
                description="这是测试文档的详细描述",
                content="# 测试文档内容\n\n这是测试文档的内容。",
                category="测试分类",
                tags="测试,文档",
                view_count=0,
                is_active=True,
                sort_order=1
            )
            self.session.add(test_doc)
            self.session.commit()
            self.session.refresh(test_doc)
            
            self.test_result("文档创建测试", test_doc.id is not None)
            
            doc_from_db = self.session.query(Document).filter(Document.id == test_doc.id).first()
            self.test_result("文档查询测试", doc_from_db is not None)
            
            self.session.delete(doc_from_db)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.test_result("文档模型测试", False, str(e))
            return False
    
    def test_key_application_model(self):
        """
        测试秘钥申请模型
        """
        self.log("开始测试秘钥申请模型...")
        
        try:
            admin = self.session.query(User).filter(User.username == "admin").first()
            
            if not admin:
                self.log("未找到admin用户，使用第一个用户进行测试", "WARNING")
                admin = self.session.query(User).first()
            
            if not admin:
                self.test_result("秘钥申请模型测试", False, "没有可用的测试用户")
                return False
            
            test_app = KeyApplication(
                user_id=admin.id,
                application_type="trial",
                company_name="测试公司",
                website="https://test.com",
                use_case="测试使用场景",
                expected_calls="<1000",
                status="pending"
            )
            self.session.add(test_app)
            self.session.commit()
            self.session.refresh(test_app)
            
            self.test_result("秘钥申请创建测试", test_app.id is not None)
            
            app_from_db = self.session.query(KeyApplication).filter(KeyApplication.id == test_app.id).first()
            self.test_result("秘钥申请查询测试", app_from_db is not None)
            
            self.session.delete(app_from_db)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.test_result("秘钥申请模型测试", False, str(e))
            return False
    
    def test_data_integrity(self):
        """
        测试数据完整性
        """
        self.log("开始测试数据完整性...")
        
        try:
            user_count = self.session.query(User).count()
            product_count = self.session.query(Product).count()
            service_count = self.session.query(Service).count()
            case_count = self.session.query(Case).count()
            doc_count = self.session.query(Document).count()
            
            self.log(f"当前数据库数据统计：")
            self.log(f"  - 用户数: {user_count}")
            self.log(f"  - 产品数: {product_count}")
            self.log(f"  - 服务数: {service_count}")
            self.log(f"  - 案例数: {case_count}")
            self.log(f"  - 文档数: {doc_count}")
            
            self.test_result("数据完整性测试", True, f"用户:{user_count}, 产品:{product_count}, 服务:{service_count}, 案例:{case_count}, 文档:{doc_count}")
            
            return True
            
        except Exception as e:
            self.test_result("数据完整性测试", False, str(e))
            return False
    
    def test_admin_user_exists(self):
        """
        测试管理员用户是否存在
        """
        self.log("检查管理员用户...")
        
        try:
            admin = self.session.query(User).filter(
                User.username == "admin",
                User.is_admin == True
            ).first()
            
            if admin:
                self.test_result("管理员用户存在测试", True, f"用户名: {admin.username}, 邮箱: {admin.email}")
                return True
            else:
                self.test_result("管理员用户存在测试", False, "未找到admin用户")
                return False
                
        except Exception as e:
            self.test_result("管理员用户存在测试", False, str(e))
            return False
    
    def run_all_tests(self):
        """
        运行所有测试
        """
        self.log("=" * 60)
        self.log("      开始系统功能测试")
        self.log("=" * 60)
        print()
        
        tests = [
            ("数据库连接", self.test_database_connection),
            ("用户模型", self.test_user_model),
            ("产品模型", self.test_product_model),
            ("服务模型", self.test_service_model),
            ("案例模型", self.test_case_model),
            ("文档模型", self.test_document_model),
            ("秘钥申请模型", self.test_key_application_model),
            ("管理员用户检查", self.test_admin_user_exists),
            ("数据完整性", self.test_data_integrity),
        ]
        
        for test_name, test_func in tests:
            print()
            self.log(f"--- 开始测试: {test_name} ---")
            test_func()
        
        print()
        self.log("=" * 60)
        self.log("      测试结果汇总")
        self.log("=" * 60)
        print()
        
        for result in self.test_results:
            status = "✓ 通过" if result["passed"] else "✗ 失败"
            detail = f": {result['detail']}" if result["detail"] else ""
            self.log(f"  {status} - {result['name']}{detail}")
        
        print()
        total = len(self.test_results)
        self.log(f"总计: {total} 项测试")
        self.log(f"通过: {self.passed_count} 项", "SUCCESS")
        self.log(f"失败: {self.failed_count} 项", "ERROR" if self.failed_count > 0 else "INFO")
        
        if self.failed_count == 0:
            print()
            self.log("所有测试通过！系统运行正常。", "SUCCESS")
        else:
            print()
            self.log(f"有 {self.failed_count} 项测试失败，请检查系统配置。", "ERROR")
        
        return self.failed_count == 0
    
    def close(self):
        """
        关闭数据库会话
        """
        self.session.close()


def main():
    """
    主函数
    """
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.close()


if __name__ == "__main__":
    sys.exit(main())
