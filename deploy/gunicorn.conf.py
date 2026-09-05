# deploy/gunicorn.conf.py
import multiprocessing

# Server socket
# NOTE: port 8000 is already used by another site on the shared VPS
# (getqissa.com). 8002 is free — keep this in sync with
# deploy/nginx_notifi.conf's upstream if you ever change it.
bind = "127.0.0.1:8002"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = "/var/log/notifi/gunicorn_access.log"
errorlog = "/var/log/notifi/gunicorn_error.log"
loglevel = "warning"
capture_output = True

# Process naming
proc_name = "notifi_gunicorn"

# Server mechanics
daemon = False
pidfile = "/var/run/notifi/gunicorn.pid"
umask = 0
user = "notifi"
group = "notifi"
tmp_upload_dir = None

# SSL (handled by Nginx, not Gunicorn)
keyfile = None
certfile = None
