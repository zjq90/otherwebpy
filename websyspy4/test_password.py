"""
密码处理测试脚本
用于验证修复后的密码哈希和验证功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.security import get_password_hash, verify_password, _preprocess_password


def test_password_processing():
    """
    测试密码处理功能
    """
    print("=" * 60)
    print("密码处理测试")
    print("=" * 60)
    
    test_passwords = [
        ("短密码", "123456"),
        ("中等长度", "MyTestPassword123!"),
        ("长密码测试", "a" * 100),
        ("包含中文字符", "密码测试123!@#"),
        ("管理员密码", "admin123"),
        ("用户密码", "123456"),
    ]
    
    all_passed = True
    
    for name, password in test_passwords:
        print(f"\n测试: {name}")
        print(f"  密码: {password[:50]}{'...' if len(password) > 50 else ''}")
        print(f"  原始长度: {len(password)} 字符, {len(password.encode('utf-8'))} 字节")
        
        processed = _preprocess_password(password)
        print(f"  处理后长度: {len(processed.encode('utf-8'))} 字节")
        
        try:
            password_hash = get_password_hash(password)
            print(f"  哈希成功: {password_hash[:30]}...")
            
            is_valid = verify_password(password, password_hash)
            print(f"  验证结果: {'通过' if is_valid else '失败'}")
            
            wrong_password = password + "wrong"
            is_wrong_valid = verify_password(wrong_password, password_hash)
            print(f"  错误密码验证: {'通过 (不应该通过!)' if is_wrong_valid else '正确拒绝'}")
            
            if not is_valid or is_wrong_valid:
                all_passed = False
                print(f"  [错误] 密码验证测试失败!")
            
        except Exception as e:
            all_passed = False
            print(f"  [错误] {e}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过!")
    else:
        print("部分测试失败!")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    test_password_processing()
