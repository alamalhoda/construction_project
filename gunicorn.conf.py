"""
Gunicorn configuration file for Chabokan.net deployment
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes (optimized for Chabokan.net)
# Use environment variable or default to 3 workers
workers = int(os.environ.get('GUNICORN_WORKERS', '3'))
# CRITICAL: Must use 'sync' worker class for SQLite compatibility
# gevent worker causes "DatabaseWrapper objects created in a thread can only be used in that same thread" error
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'construction_project'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Preload app for better performance
# Disabled for SQLite compatibility (SQLite doesn't work well with preload_app)
preload_app = False

# Worker timeout
graceful_timeout = 30

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
