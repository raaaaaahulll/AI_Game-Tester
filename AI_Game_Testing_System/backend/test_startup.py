"""
Quick test script to check if the app can be imported and started.
"""
import sys

print("Testing imports...")

try:
    print("1. Importing app...")
    from app import app
    print("   ✓ App imported successfully")
    
    print("2. Checking app instance...")
    print(f"   ✓ App type: {type(app)}")
    print(f"   ✓ App title: {app.title}")
    
    print("3. Testing routes...")
    routes = [route.path for route in app.routes]
    print(f"   ✓ Found {len(routes)} routes")
    print(f"   ✓ Sample routes: {routes[:5]}")
    
    print("\n✅ All imports successful! The app should start correctly.")
    print("\nTry running: python app.py")
    
except Exception as e:
    print(f"\n❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

