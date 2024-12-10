from app import db, app
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Testa a conexão com o banco de dados e verifica a estrutura das tabelas"""
    try:
        with app.app_context():
            # Tenta fazer uma consulta simples
            logger.info("Testando conexão com o banco de dados...")
            result = db.session.execute(db.text("SELECT 1")).scalar()
            logger.info("Conexão com o banco de dados estabelecida com sucesso!")
            
            # Lista todas as tabelas
            logger.info("\nListando todas as tabelas:")
            inspector = db.inspect(db.engine)
            for table_name in inspector.get_table_names():
                logger.info(f"\nTabela: {table_name}")
                logger.info("Colunas:")
                for column in inspector.get_columns(table_name):
                    logger.info(f"  - {column['name']}: {column['type']}")
            
            return True
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão com o banco de dados: {str(e)}")
        if hasattr(e, '__cause__'):
            logger.error(f"Causa do erro: {e.__cause__}")
        return False

if __name__ == "__main__":
    test_database_connection()
