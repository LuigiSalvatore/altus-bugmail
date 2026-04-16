#!/usr/bin/env python3
"""Test if API works without authentication"""
import requests
import json

URL = "https://vmbugzilla.altus.com.br/demandas/rest/bug"

print("Testing /demandas/rest/bug without authentication:\n")

try:
    response = requests.get(URL, verify=False, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ SUCCESS! Response keys: {list(data.keys())}")
        if 'bugs' in data:
            print(f"Bugs found: {len(data.get('bugs', []))}")
            if data.get('bugs'):
                print(f"First bug: {data['bugs'][0]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
