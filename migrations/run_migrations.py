from app import app, db
import os

def run_migrations():
    with app.app_context():
        # Caminho para o arquivo de migração
        migration_file = os.path.join(os.path.dirname(__file__), 'add_documentacao_url.sql')
        
        # Ler o conteúdo do arquivo SQL
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Executar a migração
        db.session.execute(sql)
        db.session.commit()
        
        print("Migração concluída com sucesso!")

if __name__ == '__main__':
    run_migrations()
