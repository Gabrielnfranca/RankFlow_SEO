import multiprocessing
import os

# Configurações do Gunicorn otimizadas para Render
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")

# Cálculo automático de workers baseado nos núcleos disponíveis
# Render Free tier tem 0.1-0.5 vCPU, então manteremos em 2
workers = 2

# Usando worker class uvicorn para melhor performance
worker_class = "uvicorn.workers.UvicornWorker"

# Aumentando número de threads por worker
threads = 4

# Timeouts e configurações de conexão
timeout = 60  # Reduzindo timeout para liberar recursos mais rápido
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Configurações de performance
worker_connections = 1000
backlog = 2048

# Configurações de logging
capture_output = True
enable_stdio_inheritance = True
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações de buffer
forwarded_allow_ips = '*'
proxy_allow_ips = '*'

# Desativando reload em produção
reload = False
