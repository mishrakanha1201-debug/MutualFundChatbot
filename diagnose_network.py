#!/usr/bin/env python3
"""
Diagnose network connectivity issues for pip installation
"""
import urllib.request
import ssl
import subprocess
import sys

print("=" * 60)
print("Network Diagnostics for pip Installation")
print("=" * 60)

# Test 1: Basic connectivity
print("\n1. Testing basic connectivity...")
try:
    response = urllib.request.urlopen('https://www.google.com', timeout=5)
    print("   ✓ Internet connectivity: OK")
except Exception as e:
    print(f"   ✗ Internet connectivity: FAILED ({e})")

# Test 2: PyPI access
print("\n2. Testing PyPI access...")
endpoints = [
    ('pypi.org', 'https://pypi.org'),
    ('pypi.org/simple', 'https://pypi.org/simple/'),
    ('files.pythonhosted.org', 'https://files.pythonhosted.org/'),
]

for name, url in endpoints:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        response = urllib.request.urlopen(url, context=ctx, timeout=10)
        print(f"   ✓ {name}: Accessible (Status: {response.getcode()})")
    except Exception as e:
        print(f"   ✗ {name}: FAILED ({type(e).__name__})")

# Test 3: pip configuration
print("\n3. Checking pip configuration...")
result = subprocess.run([sys.executable, '-m', 'pip', 'config', 'list'], 
                       capture_output=True, text=True)
if result.stdout.strip():
    print("   Pip config found:")
    print("   " + result.stdout.replace("\n", "\n   "))
else:
    print("   No pip configuration found")

# Test 4: Environment variables
print("\n4. Checking environment variables...")
import os
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
              'NO_PROXY', 'no_proxy', 'ALL_PROXY', 'all_proxy']
found = False
for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"   {var} = {value}")
        found = True
if not found:
    print("   No proxy environment variables set")

# Test 5: Try pip install with verbose output
print("\n5. Testing pip install (this may take a moment)...")
result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--dry-run', 
                        '--user', 'beautifulsoup4'], 
                       capture_output=True, text=True, timeout=30)

if result.returncode == 0:
    print("   ✓ pip can query package index")
else:
    print("   ✗ pip cannot query package index")
    if '403' in result.stderr or 'Forbidden' in result.stderr:
        print("   → 403 Forbidden error detected")
    if 'from versions: none' in result.stderr:
        print("   → Cannot retrieve package versions")
    print(f"   Error: {result.stderr[-200:]}")

print("\n" + "=" * 60)
print("Diagnostics complete")
print("=" * 60)


