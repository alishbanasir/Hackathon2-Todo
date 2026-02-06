"""Debug script to identify what's causing Internal Server Error."""

import sys
import traceback

print("=" * 50)
print("PHASE 3 BACKEND DEBUG SCRIPT")
print("=" * 50)

# Step 1: Test basic imports
print("\n[1] Testing basic imports...")
try:
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("    Working directory:", os.getcwd())
    print("    ✓ Basic imports OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

# Step 2: Test config loading
print("\n[2] Testing config loading...")
try:
    from src.config import settings
    print(f"    DATABASE_URL: {settings.database_url[:50]}...")
    print(f"    GOOGLE_API_KEY: {settings.google_api_key[:20]}...")
    print(f"    APP_ENV: {settings.app_env}")
    print(f"    LOG_LEVEL: {settings.log_level}")
    print("    ✓ Config loaded OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test structlog configuration
print("\n[3] Testing structlog...")
try:
    import logging
    import structlog

    _log_level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    _log_level = _log_level_map.get(settings.log_level.lower(), logging.INFO)
    print(f"    Log level: {settings.log_level} -> {_log_level}")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(_log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger()
    logger.info("test_log_message", test="success")
    print("    ✓ Structlog configured OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test database engine creation
print("\n[4] Testing database engine...")
try:
    from src.database import engine
    print(f"    Engine: {engine}")
    print("    ✓ Database engine created OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test Gemini client import (but don't initialize)
print("\n[5] Testing Gemini client import...")
try:
    from src.ai.gemini_client import GeminiClient
    print("    ✓ GeminiClient import OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 6: Test Gemini client initialization
print("\n[6] Testing Gemini client initialization...")
try:
    client = GeminiClient()
    print(f"    Model: {client.model}")
    print("    ✓ GeminiClient initialized OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    # Continue anyway

# Step 7: Test API router imports
print("\n[7] Testing API router imports...")
try:
    from src.api import chat, conversations
    print("    ✓ API routers imported OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 8: Test FastAPI app creation
print("\n[8] Testing FastAPI app creation...")
try:
    from fastapi import FastAPI
    app = FastAPI(title="Test")
    print("    ✓ FastAPI app created OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 9: Test full main.py import
print("\n[9] Testing main.py import...")
try:
    from src.main import app
    print(f"    App: {app}")
    print(f"    Routes: {len(app.routes)}")
    print("    ✓ main.py imported OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 10: Test OpenAPI schema generation
print("\n[10] Testing OpenAPI schema generation...")
try:
    schema = app.openapi()
    print(f"    Schema title: {schema.get('info', {}).get('title')}")
    print(f"    Paths: {len(schema.get('paths', {}))}")
    print("    ✓ OpenAPI schema generated OK")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
print("\nIf you still see Internal Server Error, run the server with:")
print("  uvicorn src.main:app --reload --port 8000")
print("\nAnd check the terminal output for error messages.")
