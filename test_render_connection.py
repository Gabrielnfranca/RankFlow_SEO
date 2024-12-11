import os
import sys
import logging
import traceback
import psycopg2
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('render_connection_log.txt')
    ]
)
logger = logging.getLogger(__name__)

def test_database_connection():
    # Obter URL do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL não encontrada nas variáveis de ambiente")
        return False
    
    logger.info(f"DATABASE_URL encontrada: {database_url}")
    
    try:
        # Teste de conexão com psycopg2
        url = urlparse(database_url)
        conn_params = {
            'dbname': url.path[1:],
            'user': url.username,
            'password': url.password,
            'host': url.hostname,
            'port': url.port
        }
        
        logger.info("Tentando conexão com psycopg2...")
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                logger.info(f"Conexão psycopg2 bem-sucedida. Versão do PostgreSQL: {version}")
        
        # Teste de conexão com SQLAlchemy
        logger.info("Tentando conexão com SQLAlchemy...")
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            result = session.execute("SELECT current_database();")
            db_name = result.scalar()
            logger.info(f"Conexão SQLAlchemy bem-sucedida. Banco de dados atual: {db_name}")
        
        return True
    
    except psycopg2.Error as e:
        logger.error(f"Erro de conexão psycopg2: {e}")
        logger.error(traceback.format_exc())
    except SQLAlchemyError as e:
        logger.error(f"Erro de conexão SQLAlchemy: {e}")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        logger.error(traceback.format_exc())
    
    return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
