#!/usr/bin/env python3
"""Validate that all project imports resolve correctly after refactor."""

# Core API client
from apiBugzilla import Bugzilla

# Backend package
from backend import create_app
from backend.services.persistence import load_config, save_config, load_data, save_data
from backend.services.state import get_state
from backend.services.bugzilla_service import create_client, normalize_bug, fetch_bugs
from backend.routes import register_routes

# Logger
from logger import logger

# Smoke-test Bugzilla URL construction
print(Bugzilla('abc').Url_Bugzilla)
print(Bugzilla('abc', 'https://vmbugzilla.altus.com.br').Url_Bugzilla)
print(Bugzilla('abc', 'https://vmbugzilla.altus.com.br/demandas').Url_Bugzilla)

# Verify app factory
app = create_app()
print(f'Flask app created: {app.name}')
print(f'Registered routes: {len(app.url_map._rules)}')

print('All imports OK')
