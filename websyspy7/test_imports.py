"""测试脚本"""
import sys
import traceback

print("Testing import...")
try:
    from config import settings
    print(f"config OK: {settings.PROJECT_NAME}")
except Exception as e:
    print(f"config FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from database import engine, async_session_maker
    print(f"database OK")
except Exception as e:
    print(f"database FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from models import User, Passenger
    print(f"models OK")
except Exception as e:
    print(f"models FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from auth import get_password_hash
    print(f"auth OK")
except Exception as e:
    print(f"auth FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from http_client import http_client
    print(f"http_client OK")
except Exception as e:
    print(f"http_client FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from monitor_service import monitor_service
    print(f"monitor_service OK")
except Exception as e:
    print(f"monitor_service FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

print("All module imports OK!")

print("\nNow testing main app import...")
try:
    import main
    print(f"main OK! App title: {main.app.title}")
    print(f"Routes count: {len(main.app.routes)}")
except Exception as e:
    print(f"main FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
