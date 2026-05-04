import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting server...")
print(f"Python version: {sys.version}")
print(f"Current path: {os.path.dirname(os.path.abspath(__file__))}")

try:
    from app.main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
