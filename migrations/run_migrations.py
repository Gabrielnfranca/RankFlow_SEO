from app import app, db
import os

def run_migrations():
    with app.app_context():
        try:
            # Caminho para o arquivo de migração
            migration_file = os.path.join(os.path.dirname(__file__), 'recreate_seo_tables.sql')
            
            # Ler o conteúdo do arquivo SQL
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Executar a migração
            db.session.execute(sql)
            db.session.commit()
            
            print("Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"Erro durante a migração: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == '__main__':
    run_migrations()
