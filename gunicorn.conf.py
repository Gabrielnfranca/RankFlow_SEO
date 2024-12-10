import multiprocessing
import os

# Configurações do Gunicorn
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = 1  # Para aplicações pequenas/médias
worker_class = "sync"
threads = 2
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
reload = True
capture_output = True
enable_stdio_inheritance = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
