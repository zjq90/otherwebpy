# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Starting module import test...")
print("=" * 60)

try:
    print("\n1. Importing config...")
    from config import settings
    print("   [OK] App name: ", settings.APP_NAME)
    print("   [OK] Database URL: ", settings.DATABASE_URL)
except Exception as e:
    print("   [ERROR] Import failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Importing database...")
    from database import engine, Base, SessionLocal, get_db, init_db
    print("   [OK] Database module imported")
except Exception as e:
    print("   [ERROR] Import failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Importing models...")
    from models import (
        User, Coach, Course, MemberPreference, Booking,
        Message, ChatSession, ChatMessage, Review,
        NutritionProduct, Recommendation
    )
    print("   [OK] All models imported")
except Exception as e:
    print("   [ERROR] Import failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. Importing schemas...")
    from schemas import (
        UserCreate, UserLogin, UserResponse,
        CourseResponse, CoachResponse,
        MessageResponse, ReviewResponse,
        NutritionProductResponse, BookingResponse
    )
    print("   [OK] Schema models imported")
except Exception as e:
    print("   [ERROR] Import failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n5. Importing utils...")
    from utils import (
        get_password_hash, verify_password,
        create_access_token, get_current_user,
        paginate_query, require_role
    )
    print("   [OK] Utility functions imported")
except Exception as e:
    print("   [ERROR] Import failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n6. Initializing database...")
    init_db()
    print("   [OK] Database initialized")
except Exception as e:
    print("   [ERROR] Init failed: ", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n7. Creating test admin...")
    db = SessionLocal()
    from models import User, UserRole
    from utils import get_password_hash
    
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@gym.com",
            phone="13800138000",
            real_name="System Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("   [OK] Admin account created: admin / admin123")
    else:
        print("   [OK] Admin account already exists")
    db.close()
except Exception as e:
    print("   [ERROR] Create failed: ", e)
    import traceback
    traceback.print_exc()
    db.rollback()

print("\n" + "=" * 60)
print("All checks passed! Backend modules imported successfully.")
print("=" * 60)
print("\nNext steps:")
print("1. Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
print("2. Visit: http://localhost:8000/docs to see API docs")
print("\nTest accounts:")
print("  Admin: admin / admin123")
