"""
系统功能测试脚本
用于验证农产品溯源与认证管理系统的核心功能
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8001"


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*60)
    print("测试1: 健康检查接口")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务状态: {data['status']}")
            print(f"✓ 应用名称: {data['app_name']}")
            print(f"✓ 版本: {data['version']}")
            return True
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_generate_test_data():
    """测试生成测试数据接口"""
    print("\n" + "="*60)
    print("测试2: 生成测试数据")
    print("="*60)
    
    try:
        response = requests.post(f"{BASE_URL}/api/test-data/generate/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功: {data['message']}")
            print(f"✓ 总创建记录数: {data['total_created']}")
            print("✓ 详细统计:")
            for key, count in data['details'].items():
                print(f"  - {key}: {count}")
            return True
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            print(f"  详情: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_products_crud():
    """测试产品CRUD功能"""
    print("\n" + "="*60)
    print("测试3: 产品管理CRUD")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/")
        if response.status_code == 200:
            products = response.json()
            print(f"✓ 获取产品列表成功，共 {len(products)} 个产品")
            
            if products:
                p = products[0]
                print(f"✓ 示例产品:")
                print(f"  - ID: {p['id']}")
                print(f"  - 名称: {p['name']}")
                print(f"  - 类别: {p.get('category', '-')}")
                print(f"  - 产地: {p.get('origin', '-')}")
            
            return True
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_batches_with_qrcode():
    """测试批次管理和二维码生成"""
    print("\n" + "="*60)
    print("测试4: 批次管理与二维码生成")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/batches/")
        if response.status_code == 200:
            batches = response.json()
            print(f"✓ 获取批次列表成功，共 {len(batches)} 个批次")
            
            if batches:
                b = batches[0]
                print(f"✓ 示例批次:")
                print(f"  - 批次编号: {b['batch_number']}")
                print(f"  - 数量: {b.get('quantity', '-')} {b.get('unit', '')}")
                print(f"  - 二维码路径: {b.get('qrcode_path', '未生成')}")
                if b.get('qrcode_path'):
                    print(f"  - 二维码已生成 ✓")
            
            return True
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_traceability_query():
    """测试溯源查询功能"""
    print("\n" + "="*60)
    print("测试5: 溯源查询功能")
    print("="*60)
    
    try:
        batches_response = requests.get(f"{BASE_URL}/api/batches/")
        if batches_response.status_code != 200:
            print("✗ 无法获取批次列表")
            return False
        
        batches = batches_response.json()
        if not batches:
            print("⚠ 没有批次数据，请先生成测试数据")
            return False
        
        batch_number = batches[0]['batch_number']
        print(f"测试批次: {batch_number}")
        
        response = requests.get(f"{BASE_URL}/api/traceability/batch/{batch_number}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 溯源查询成功")
            print(f"  - 产品: {data['product']['name']}")
            print(f"  - 批次: {data['batch']['batch_number']}")
            print(f"  - 种植记录数: {len(data.get('planting_records', []))}")
            print(f"  - 农资使用记录数: {len(data.get('agrochemical_usages', []))}")
            print(f"  - 检测结果数: {len(data.get('test_results', []))}")
            
            return True
        else:
            print(f"✗ 查询失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_certificates_reminder():
    """测试认证证书管理和到期提醒"""
    print("\n" + "="*60)
    print("测试6: 认证证书管理与到期提醒")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/certificates/")
        if response.status_code == 200:
            certificates = response.json()
            print(f"✓ 获取证书列表成功，共 {len(certificates)} 个证书")
            
            if certificates:
                print("✓ 证书状态分布:")
                status_count = {}
                for cert in certificates:
                    status = cert.get('status', '未知')
                    status_count[status] = status_count.get(status, 0) + 1
                
                for status, count in status_count.items():
                    print(f"  - {status}: {count}")
        
        expiring_response = requests.get(f"{BASE_URL}/api/certificates/expiring-soon/")
        if expiring_response.status_code == 200:
            expiring = expiring_response.json()
            print(f"✓ 即将过期证书数量: {len(expiring)}")
            if expiring:
                for cert in expiring[:2]:
                    print(f"  - {cert['certificate_type']}: {cert['certificate_number']}")
                    print(f"    有效期至: {cert['valid_until']}")
            
            return True
        else:
            print(f"✗ 获取即将过期证书失败，状态码: {expiring_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_test_results():
    """测试检测结果管理"""
    print("\n" + "="*60)
    print("测试7: 检测结果管理")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/test-results/")
        if response.status_code == 200:
            results = response.json()
            print(f"✓ 获取检测结果成功，共 {len(results)} 条记录")
            
            if results:
                print("✓ 检测结果统计:")
                type_count = {}
                result_count = {}
                for r in results:
                    t = r.get('test_type', '未知')
                    type_count[t] = type_count.get(t, 0) + 1
                    res = r.get('result', '未知')
                    result_count[res] = result_count.get(res, 0) + 1
                
                print(f"  检测类型分布:")
                for t, count in type_count.items():
                    print(f"    - {t}: {count}")
                
                print(f"  检测结果分布:")
                for res, count in result_count.items():
                    badge = "✓" if res == "合格" else "✗"
                    print(f"    {badge} {res}: {count}")
            
            return True
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#    农产品溯源与认证管理系统 - 功能测试报告     #")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    results = []
    
    results.append(("健康检查", test_health_check()))
    results.append(("生成测试数据", test_generate_test_data()))
    results.append(("产品管理CRUD", test_products_crud()))
    results.append(("批次管理与二维码", test_batches_with_qrcode()))
    results.append(("溯源查询", test_traceability_query()))
    results.append(("证书管理与提醒", test_certificates_reminder()))
    results.append(("检测结果管理", test_test_results()))
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n✓ 所有测试通过！系统运行正常！")
        return True
    else:
        print(f"\n✗ 有 {total - passed} 项测试失败，请检查系统配置")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
