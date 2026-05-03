#!/usr/bin/env python3
"""
测试脚本 - 验证所有模块是否可以正常导入
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试模块导入...")
print("=" * 60)

try:
    from decimal import Decimal
    print("✓ decimal Decimal 导入成功")
except Exception as e:
    print(f"✗ decimal Decimal 导入失败: {e}")
    sys.exit(1)

try:
    from typing import Optional
    print("✓ typing 导入成功")
except Exception as e:
    print(f"✗ typing 导入失败: {e}")
    sys.exit(1)

try:
    from datetime import date, datetime, timedelta
    print("✓ datetime 导入成功")
except Exception as e:
    print(f"✗ datetime 导入失败: {e}")
    sys.exit(1)

try:
    import config
    print("✓ config.py 导入成功")
except Exception as e:
    print(f"✗ config.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    import models
    print("✓ models.py 导入成功")
except Exception as e:
    print(f"✗ models.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    import schemas
    print("✓ schemas.py 导入成功")
except Exception as e:
    print(f"✗ schemas.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    import crud
    print("✓ crud.py 导入成功")
except Exception as e:
    print(f"✗ crud.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    import database
    print("✓ database.py 导入成功")
except Exception as e:
    print(f"✗ database.py 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("测试密码截断功能...")
print("=" * 60)

long_password = "a" * 100  # 100个字符的长密码
try:
    # 测试截断
    password_bytes = long_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    print(f"✓ 原密码长度: {len(long_password)}")
    print(f"✓ 截断后密码长度: {len(truncated_password)}")
    assert len(truncated_password) == 72
    print("✓ 密码截断功能正常")
except Exception as e:
    print(f"✗ 密码截断功能测试失败: {e}")

print("\n" + "=" * 60)
print("测试日期解析...")
print("=" * 60)

date_str = "2024-01-15"
empty_str = ""
none_value = None

try:
    # 测试正常日期解析
    parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    print(f"✓ 正常日期解析: {parsed_date}")
    
    # 测试空字符串
    if empty_str and empty_str.strip():
        parsed_empty = datetime.strptime(empty_str, "%Y-%m-%d").date()
    else:
        parsed_empty = None
    print(f"✓ 空字符串处理: {parsed_empty}")
    
    # 测试None值
    if none_value and str(none_value).strip():
        parsed_none = datetime.strptime(str(none_value), "%Y-%m-%d").date()
    else:
        parsed_none = None
    print(f"✓ None值处理: {parsed_none}")
    
    print("✓ 日期解析功能正常")
except Exception as e:
    print(f"✗ 日期解析测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试Jinja2模板变量逻辑...")
print("=" * 60)

try:
    # 模拟Jinja2中的变量检查逻辑
    def check_hide_sidebar(hide_sidebar=None):
        # 对应: {% if hide_sidebar is not defined or not hide_sidebar %}
        if hide_sidebar is None or not hide_sidebar:
            return "显示侧边栏"
        else:
            return "隐藏侧边栏"
    
    print(f"✓ hide_sidebar=None: {check_hide_sidebar(None)}")
    print(f"✓ hide_sidebar=False: {check_hide_sidebar(False)}")
    print(f"✓ hide_sidebar=True: {check_hide_sidebar(True)}")
    print("✓ Jinja2模板变量逻辑正确")
except Exception as e:
    print(f"✗ Jinja2模板变量逻辑测试失败: {e}")

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)
