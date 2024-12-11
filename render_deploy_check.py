import os
import sys
import logging
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('render_deploy_log.txt')
    ]
)
logger = logging.getLogger(__name__)

def check_environment_vars():
    """Verificar variáveis de ambiente críticas"""
    critical_vars = ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV']
    
    logger.info("Verificando variáveis de ambiente...")
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"{var}: {'*' * len(value)}")  # Mascara o valor real
        else:
            logger.warning(f"Variável {var} NÃO ENCONTRADA")

def validate_database_connection():
    """Tentar validar conexão com o banco de dados"""
    try:
        from app import db
        from sqlalchemy import text
        
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Conexão com banco de dados bem-sucedida")
    except Exception as e:
        logger.error("Erro de conexão com banco de dados:")
        logger.error(traceback.format_exc())

def check_dependencies():
    """Verificar dependências instaladas"""
    try:
        import pkg_resources
        
        dependencies = [
            'flask', 'sqlalchemy', 'psycopg2', 
            'flask-login', 'flask-sqlalchemy'
        ]
        
        logger.info("Verificando dependências...")
        for dep in dependencies:
            try:
                version = pkg_resources.get_distribution(dep).version
                logger.info(f"{dep}: {version}")
            except pkg_resources.DistributionNotFound:
                logger.warning(f"{dep} NÃO INSTALADO")
    except Exception as e:
        logger.error("Erro ao verificar dependências:")
        logger.error(traceback.format_exc())

def main():
    logger.info("Iniciando diagnóstico de deploy")
    
    check_environment_vars()
    validate_database_connection()
    check_dependencies()
    
    logger.info("Diagnóstico concluído")

if __name__ == "__main__":
    main()
