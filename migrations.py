from app import db
from sqlalchemy import text
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        with db.engine.connect() as conn:
            # PostgreSQL
            if 'postgresql' in db.engine.url.drivername:
                query = text("""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name 
                        AND column_name = :column_name
                    );
                """)
            # SQLite
            else:
                query = text("""
                    SELECT COUNT(*) 
                    FROM pragma_table_info(:table_name) 
                    WHERE name = :column_name;
                """)
            
            result = conn.execute(query, {"table_name": table_name, "column_name": column_name})
            return bool(result.scalar())
    except Exception as e:
        logger.error(f"Erro ao verificar coluna {column_name} na tabela {table_name}: {str(e)}")
        return False

def add_column_if_not_exists(table_name, column_name, column_type):
    """Adiciona uma coluna se ela não existir"""
    try:
        if not check_column_exists(table_name, column_name):
            logger.info(f"Adicionando coluna {column_name} na tabela {table_name}")
            with db.engine.connect() as conn:
                # PostgreSQL
                if 'postgresql' in db.engine.url.drivername:
                    query = text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type};")
                # SQLite
                else:
                    query = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
                conn.execute(query)
                conn.commit()
                logger.info(f"Coluna {column_name} adicionada com sucesso!")
        else:
            logger.info(f"Coluna {column_name} já existe na tabela {table_name}")
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna {column_name}: {str(e)}")
        raise

def run_migrations():
    """Executa todas as migrações necessárias"""
    try:
        logger.info("Iniciando migrações...")
        
        # Migrações para a tabela usuario
        add_column_if_not_exists('usuario', 'nome', 'TEXT')
        add_column_if_not_exists('usuario', 'email', 'TEXT')
        add_column_if_not_exists('usuario', 'senha', 'TEXT')
        add_column_if_not_exists('usuario', 'data_criacao', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Migrações para a tabela cliente
        add_column_if_not_exists('cliente', 'nome', 'TEXT')
        add_column_if_not_exists('cliente', 'website', 'TEXT')
        add_column_if_not_exists('cliente', 'descricao', 'TEXT')
        add_column_if_not_exists('cliente', 'usuario_id', 'INTEGER')
        add_column_if_not_exists('cliente', 'data_criacao', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Migrações para a tabela tarefa
        add_column_if_not_exists('tarefa', 'titulo', 'TEXT')
        add_column_if_not_exists('tarefa', 'descricao', 'TEXT')
        add_column_if_not_exists('tarefa', 'prazo', 'DATE')
        add_column_if_not_exists('tarefa', 'status', 'TEXT DEFAULT "pendente"')
        add_column_if_not_exists('tarefa', 'cliente_id', 'INTEGER')
        
        # Migrações para a tabela etapa_seo
        add_column_if_not_exists('etapa_seo', 'nome', 'TEXT')
        add_column_if_not_exists('etapa_seo', 'descricao', 'TEXT')
        add_column_if_not_exists('etapa_seo', 'ordem', 'INTEGER')
        
        # Migrações para a tabela progresso_seo
        add_column_if_not_exists('progresso_seo', 'cliente_id', 'INTEGER')
        add_column_if_not_exists('progresso_seo', 'etapa_id', 'INTEGER')
        add_column_if_not_exists('progresso_seo', 'status', 'TEXT DEFAULT "todo"')
        add_column_if_not_exists('progresso_seo', 'observacoes', 'TEXT')
        
        logger.info("Migrações concluídas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante as migrações: {str(e)}")
        raise

if __name__ == "__main__":
    run_migrations()
