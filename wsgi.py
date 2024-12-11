import os
from app import app, db, init_db
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando a aplicação...")
    # Garante que o banco de dados seja inicializado
    init_db()
    logger.info("Banco de dados inicializado com sucesso!")
except Exception as e:
    logger.error(f"Erro ao inicializar a aplicação: {str(e)}")
    raise

# Configuração da porta
port = int(os.environ.get("PORT", 8000))
logger.info(f"Configurando aplicação para usar a porta {port}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
