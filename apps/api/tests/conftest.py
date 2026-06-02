"""Test bootstrap.

`app.config` instantiates `Settings()` at import time, and several fields are
required. Set harmless dummy values before any app module is imported so the unit
tests (which mock all LLM/DB/network calls) can run without a real .env or secrets.
"""

import os

_DUMMY_ENV = {
    "ANTHROPIC_API_KEY": "test-key",
    "NOTION_API_KEY": "test-key",
    "NOTION_PARENT_ID": "test-parent",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "test-key",
}

for key, value in _DUMMY_ENV.items():
    os.environ.setdefault(key, value)
