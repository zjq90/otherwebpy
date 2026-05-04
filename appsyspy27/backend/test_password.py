"""
测试密码加密功能
验证bcrypt 72字节限制的修复是否有效
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.security import get_password_hash, verify_password, _truncate_password_for_bcrypt


def test_password_truncation():
    """测试密码截断功能"""
    print("=" * 60)
    print("测试密码截断功能")
    print("=" * 60)
    
    # 测试1: 短密码（小于72字节）
    short_pwd = "123456"
    short_truncated = _truncate_password_for_bcrypt(short_pwd)
    print(f"\n1. 短密码测试:")
    print(f"   原始密码: {short_pwd}")
    print(f"   截断后: {short_truncated}")
    print(f"   结果: {'通过' if short_pwd == short_truncated else '失败'}")
    
    # 测试2: 长密码（超过72字节）
    long_pwd = "a" * 80
    long_truncated = _truncate_password_for_bcrypt(long_pwd)
    long_truncated_bytes = long_truncated.encode('utf-8')
    print(f"\n2. 长密码测试:")
    print(f"   原始密码长度: {len(long_pwd)} 字符")
    print(f"   原始密码字节数: {len(long_pwd.encode('utf-8'))} 字节")
    print(f"   截断后字节数: {len(long_truncated_bytes)} 字节")
    print(f"   结果: {'通过' if len(long_truncated_bytes) <= 72 else '失败'}")
    
    # 测试3: 中文字符（多字节字符）
    chinese_pwd = "测试密码测试密码测试密码测试密码测试密码测试密码测试密码测试密码"
    chinese_truncated = _truncate_password_for_bcrypt(chinese_pwd)
    chinese_truncated_bytes = chinese_truncated.encode('utf-8')
    print(f"\n3. 中文字符测试:")
    print(f"   原始密码: {chinese_pwd}")
    print(f"   原始字节数: {len(chinese_pwd.encode('utf-8'))} 字节")
    print(f"   截断后字节数: {len(chinese_truncated_bytes)} 字节")
    print(f"   结果: {'通过' if len(chinese_truncated_bytes) <= 72 else '失败'}")


def test_password_hash_and_verify():
    """测试密码哈希和验证功能"""
    print("\n" + "=" * 60)
    print("测试密码哈希和验证功能")
    print("=" * 60)
    
    # 测试1: 正常密码
    print("\n1. 正常密码测试:")
    pwd1 = "123456"
    hash1 = get_password_hash(pwd1)
    print(f"   密码: {pwd1}")
    print(f"   哈希: {hash1[:50]}...")
    verify_result1 = verify_password(pwd1, hash1)
    print(f"   验证结果: {'通过' if verify_result1 else '失败'}")
    
    # 测试2: 长密码（超过72字节）
    print("\n2. 长密码测试:")
    pwd2 = "wx_mock_" + "a" * 60  # 模拟微信登录的openid，可能很长
    hash2 = get_password_hash(pwd2)
    print(f"   密码长度: {len(pwd2)} 字符")
    print(f"   密码字节数: {len(pwd2.encode('utf-8'))} 字节")
    print(f"   哈希: {hash2[:50]}...")
    
    # 验证同样的密码
    verify_result2 = verify_password(pwd2, hash2)
    print(f"   验证结果: {'通过' if verify_result2 else '失败'}")
    
    # 验证截断后的密码（应该也能通过）
    truncated_pwd2 = _truncate_password_for_bcrypt(pwd2)
    verify_result2b = verify_password(truncated_pwd2, hash2)
    print(f"   截断密码验证: {'通过' if verify_result2b else '失败'}")
    
    # 测试3: 错误密码
    print("\n3. 错误密码测试:")
    wrong_pwd = "wrongpassword"
    verify_result3 = verify_password(wrong_pwd, hash1)
    print(f"   错误密码验证: {'通过(预期失败)' if not verify_result3 else '失败(错误)'}")


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试边界情况")
    print("=" * 60)
    
    # 空密码
    print("\n1. 空密码测试:")
    empty_pwd = ""
    try:
        hash_empty = get_password_hash(empty_pwd)
        verify_empty = verify_password(empty_pwd, hash_empty)
        print(f"   结果: {'通过' if verify_empty else '失败'}")
    except Exception as e:
        print(f"   结果: 异常 - {e}")
    
    # 恰好72字节
    print("\n2. 恰好72字节测试:")
    pwd_72 = "a" * 72
    hash_72 = get_password_hash(pwd_72)
    verify_72 = verify_password(pwd_72, hash_72)
    print(f"   密码字节数: {len(pwd_72.encode('utf-8'))} 字节")
    print(f"   结果: {'通过' if verify_72 else '失败'}")


if __name__ == "__main__":
    test_password_truncation()
    test_password_hash_and_verify()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
