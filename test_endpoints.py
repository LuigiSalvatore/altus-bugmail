#!/usr/bin/env python3
"""Test different Bugzilla API endpoints"""
import requests
import json

API_KEY = "KhVdJIDhc3jhfo0SDNl2bCzJydx3vLkWduLwNlrT"
BASE_URL = "https://vmbugzilla.altus.com.br"

# Endpoints to test
endpoints = [
    f"{BASE_URL}/rest/bug",
    f"{BASE_URL}/demandas/rest/bug",
    f"{BASE_URL}/bugzilla/rest/bug",
    f"{BASE_URL}/api/bug",
    f"{BASE_URL}/demandas/api/bug",
]

headers = {'Bugzilla_api_key': API_KEY}

print("Testing Bugzilla API endpoints:\n")
for url in endpoints:
    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ SUCCESS!")
            data = response.json()
            print(f"  Response keys: {list(data.keys())}")
            if 'bugs' in data:
                print(f"  Bugs found: {len(data.get('bugs', []))}")
        elif response.status_code == 404:
            print(f"  ✗ Not found")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Also test if we can access the UI directly to verify the domain
print("\nTesting UI endpoints:")
ui_endpoints = [
    f"{BASE_URL}/demandas/show_bug.cgi?id=1",
    f"{BASE_URL}/show_bug.cgi?id=1",
]

for url in ui_endpoints:
    try:
        print(f"Testing: {url}")
        response = requests.get(url, verify=False, timeout=5)
        print(f"  Status: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
