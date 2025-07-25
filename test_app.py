#!/usr/bin/env python3
"""
Simple test script to check if app.py can be imported
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🔍 Testing app.py import...")
    import app
    print("✅ app.py imported successfully!")
    
    # Test if FastAPI app is defined
    if hasattr(app, 'app'):
        print("✅ FastAPI app found!")
    else:
        print("❌ FastAPI app not found!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Test completed!") 