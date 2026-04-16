#!/usr/bin/env python3
"""Test different auth methods for Bugzilla API"""
import requests
import json

API_KEY = "KhVdJIDhc3jhfo0SDNl2bCzJydx3vLkWduLwNlrT"
URL = "https://vmbugzilla.altus.com.br/demandas/rest/bug"

print("Testing authentication methods:\n")

# Method 1: Bugzilla_api_key header
print("1. Testing with Bugzilla_api_key header:")
headers = {'Bugzilla_api_key': API_KEY}
try:
    response = requests.get(URL, headers=headers, verify=False, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ SUCCESS!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Method 2: Bearer token
print("2. Testing with Bearer token:")
headers = {'Authorization': f'Bearer {API_KEY}'}
try:
    response = requests.get(URL, headers=headers, verify=False, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ SUCCESS!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Method 3: Query parameter
print("3. Testing with api_key query parameter:")
try:
    response = requests.get(URL, params={'api_key': API_KEY}, verify=False, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ SUCCESS!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Method 4: X-Bugzilla-API-Key header
print("4. Testing with X-Bugzilla-API-Key header:")
headers = {'X-Bugzilla-API-Key': API_KEY}
try:
    response = requests.get(URL, headers=headers, verify=False, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ SUCCESS!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")
