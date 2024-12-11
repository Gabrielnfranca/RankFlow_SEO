import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def run_migrations():
    # Obter a URL do banco de dados do ambiente
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception('DATABASE_URL não encontrada nas variáveis de ambiente')

    # Parsear a URL do banco de dados
    url = urlparse(database_url)
    dbname = url.path[1:]  # Remove a barra inicial
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Conectado ao banco de dados. Iniciando migrações...")

        # Executar o script de recriação das tabelas
        migration_path = os.path.join(os.path.dirname(__file__), 'recreate_seo_tables.sql')
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        print("Executando script de migração...")
        cur.execute(sql_script)
        print("Script de migração executado com sucesso!")

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    run_migrations()
