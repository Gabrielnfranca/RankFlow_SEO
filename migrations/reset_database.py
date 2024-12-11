import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def reset_database():
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

        # Lista de tabelas para limpar (em ordem reversa para respeitar constraints)
        tables_to_clear = [
            'seo_tecnico_status',
            'seo_tecnico_item',
            'seo_tecnico_categoria',
            'cliente',
            'usuario'
        ]

        # Limpar todas as tabelas
        for table in tables_to_clear:
            try:
                cur.execute(f"DELETE FROM {table};")
                print(f"Tabela {table} limpa com sucesso.")
            except Exception as e:
                print(f"Erro ao limpar tabela {table}: {e}")

        # Inserir usuário de teste
        cur.execute("""
            INSERT INTO usuario (nome, email, senha) VALUES 
            ('Usuário Teste', 'teste@rankflow.com.br', 
             crypt('teste123', gen_salt('bf')));
        """)

        # Inserir cliente de teste
        cur.execute("""
            INSERT INTO cliente (nome, website, usuario_id) VALUES 
            ('Cliente Exemplo', 'https://webone.com.br', 
             (SELECT id FROM usuario WHERE email = 'teste@rankflow.com.br'));
        """)

        print("Banco de dados resetado. Usuário e cliente de teste criados.")

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao resetar banco de dados: {e}")

if __name__ == '__main__':
    reset_database()
