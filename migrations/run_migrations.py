import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def check_table_exists(cur, table_name):
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    return cur.fetchone()[0]

def run_migrations():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception('DATABASE_URL não encontrada nas variáveis de ambiente')

    url = urlparse(database_url)
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Conectado ao banco de dados. Verificando necessidade de migrações...")

        # Verifica se as tabelas já existem
        tables_exist = all(check_table_exists(cur, table) for table in ['usuario', 'projeto', 'pagina'])

        if not tables_exist:
            print("Tabelas não encontradas. Iniciando criação...")
            migration_path = os.path.join(os.path.dirname(__file__), 'recreate_seo_tables.sql')
            with open(migration_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            cur.execute(sql_script)
            print("Tabelas criadas com sucesso!")
        else:
            print("Tabelas já existem. Pulando migração.")

    except Exception as e:
        print(f"Erro durante a verificação/migração: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    run_migrations()
