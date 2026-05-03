"""
CD管理系统API测试脚本
用于测试各个功能模块
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import execute_query, execute_insert, execute_update, execute_delete
from utils.security import get_password_hash, verify_password, BCRYPT_AVAILABLE


def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    try:
        result = execute_query("SELECT 1 as test")
        print("数据库连接成功!")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def test_password_hash():
    """测试密码哈希功能"""
    print("\n=== 测试密码哈希 ===")
    
    # 检查bcrypt是否可用
    if BCRYPT_AVAILABLE:
        print("bcrypt库可用，使用bcrypt进行密码哈希")
    else:
        print("bcrypt库不可用，使用SHA256作为备用方案")
    
    test_password = "test123"
    
    # 测试哈希生成
    hashed = get_password_hash(test_password)
    print(f"密码哈希生成成功: {hashed[:40]}...")
    
    # 测试哈希验证
    is_valid = verify_password(test_password, hashed)
    print(f"密码验证成功: {is_valid}")
    
    # 测试错误密码
    is_invalid = verify_password("wrongpassword", hashed)
    print(f"错误密码验证: {is_invalid} (应为False)")
    
    # 测试长密码（超过72字节）
    long_password = "a" * 100
    print(f"\n测试长密码（{len(long_password)}字符）:")
    long_hashed = get_password_hash(long_password)
    print(f"长密码哈希生成成功")
    long_valid = verify_password(long_password, long_hashed)
    print(f"长密码验证成功: {long_valid}")
    
    return is_valid and not is_invalid and long_valid


def test_user_operations():
    """测试用户操作"""
    print("\n=== 测试用户操作 ===")
    
    # 检查现有用户
    users = execute_query("SELECT id, username, email, role FROM users LIMIT 5")
    if users:
        print(f"现有用户数量: {len(users)}")
        for user in users:
            print(f"  - {user['username']} ({user['role']})")
        return True
    else:
        print("没有找到用户，请先初始化数据库")
        return False


def test_category_operations():
    """测试分类操作"""
    print("\n=== 测试分类操作 ===")
    
    # 检查现有分类
    categories = execute_query("SELECT id, name, description FROM categories LIMIT 5")
    if categories:
        print(f"现有分类数量: {len(categories)}")
        for cat in categories:
            print(f"  - {cat['name']}: {cat['description'][:30] if cat['description'] else '无描述'}...")
        return True
    else:
        print("没有找到分类，请先初始化数据库")
        return False


def test_cd_operations():
    """测试CD操作"""
    print("\n=== 测试CD操作 ===")
    
    # 检查现有CD
    cds = execute_query("""
        SELECT c.id, c.title, c.artist, cat.name as category_name, 
               c.total_quantity, c.available_quantity
        FROM cds c
        LEFT JOIN categories cat ON c.category_id = cat.id
        LIMIT 5
    """)
    
    if cds:
        print(f"现有CD数量: {len(execute_query('SELECT COUNT(*) as count FROM cds')[0]['count'])}")
        for cd in cds:
            print(f"  - {cd['title']} - {cd['artist']}")
            print(f"    分类: {cd['category_name'] or '未分类'}")
            print(f"    库存: {cd['total_quantity']}, 可用: {cd['available_quantity']}")
        return True
    else:
        print("没有找到CD，请先初始化数据库")
        return False


def test_borrow_records():
    """测试借还记录"""
    print("\n=== 测试借还记录 ===")
    
    # 检查现有借还记录
    records = execute_query("""
        SELECT br.id, br.status, br.borrow_date, br.return_date,
               c.title as cd_title, u.username
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        JOIN users u ON br.user_id = u.id
        LIMIT 5
    """)
    
    if records:
        print(f"现有借还记录数量: {len(execute_query('SELECT COUNT(*) as count FROM borrow_records')[0]['count'])}")
        for record in records:
            status_text = "借阅中" if record['status'] == 'borrowed' else "已归还"
            print(f"  - {record['cd_title']} 借阅者: {record['username']}")
            print(f"    状态: {status_text}")
            print(f"    借阅日期: {record['borrow_date']}")
            if record['return_date']:
                print(f"    归还日期: {record['return_date']}")
        return True
    else:
        print("没有找到借还记录")
        return True  # 没有记录也是正常的


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("CD管理系统测试")
    print("=" * 60)
    
    results = []
    
    # 运行各个测试
    results.append(("数据库连接", test_database_connection()))
    results.append(("密码哈希", test_password_hash()))
    results.append(("用户操作", test_user_operations()))
    results.append(("分类操作", test_category_operations()))
    results.append(("CD操作", test_cd_operations()))
    results.append(("借还记录", test_borrow_records()))
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "通过" if passed else "失败"
        status_icon = "✓" if passed else "✗"
        print(f"{status_icon} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("所有测试通过! 系统运行正常。")
    else:
        print("部分测试失败，请检查系统配置。")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
