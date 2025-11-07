#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '.')

# Set environment variable
os.environ['AGENT_HTTP_SHARED_SECRET'] = 'A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2'

from api.fastapi_agent import check_auth

print("Testing check_auth function...")

# Test with correct secret
try:
    check_auth('A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2')
    print("✅ Correct secret: SUCCESS")
except Exception as e:
    print(f"❌ Correct secret: FAILED - {e}")

# Test with wrong secret
try:
    check_auth('wrong_secret')
    print("❌ Wrong secret: SHOULD HAVE FAILED")
except Exception as e:
    print(f"✅ Wrong secret: CORRECTLY FAILED - {e}")

# Test with None
try:
    check_auth(None)
    print("❌ None secret: SHOULD HAVE FAILED")
except Exception as e:
    print(f"✅ None secret: CORRECTLY FAILED - {e}")
