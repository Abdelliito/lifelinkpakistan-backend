"""
Gunicorn configuration for production deployment.

Usage:
    gunicorn app.main:app -c gunicorn_config.py

Or via Procfile:
    web: gunicorn app.main:app -c gunicorn_config.py
"""

import multiprocessing
import os

# Bind to PORT env var (cloud platforms set this) or default to 8000
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Workers: 2-4 per CPU core is recommended for I/O-bound apps
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

# Use Uvicorn's ASGI worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout (seconds) — increase if Gemini calls are slow
timeout = 120

# Graceful restart timeout
graceful_timeout = 30

# Keep-alive connections
keepalive = 5

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.getenv("LOG_LEVEL", "info")
