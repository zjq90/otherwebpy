import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from app.schemas.common import ChartResponse
    print("✓ app.schemas.common.ChartResponse imported successfully")
except Exception as e:
    print(f"✗ Failed to import ChartResponse: {e}")

try:
    from app.schemas.production import ChartResponse
    print("✓ app.schemas.production.ChartResponse imported successfully")
except Exception as e:
    print(f"✗ Failed to import from production: {e}")

try:
    from app.routers import quality
    print("✓ app.routers.quality imported successfully")
except Exception as e:
    print(f"✗ Failed to import quality router: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import equipment
    print("✓ app.routers.equipment imported successfully")
except Exception as e:
    print(f"✗ Failed to import equipment router: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import production
    print("✓ app.routers.production imported successfully")
except Exception as e:
    print(f"✗ Failed to import production router: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import test
    print("✓ app.routers.test imported successfully")
except Exception as e:
    print(f"✗ Failed to import test router: {e}")
    import traceback
    traceback.print_exc()

try:
    from main import app
    print("✓ main.app imported successfully")
    print("\nAll imports successful! Application should start correctly.")
except Exception as e:
    print(f"✗ Failed to import main app: {e}")
    import traceback
    traceback.print_exc()
