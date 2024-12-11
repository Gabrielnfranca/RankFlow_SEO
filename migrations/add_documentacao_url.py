from flask import current_app
from app import db, app

def add_documentacao_url_column():
    with app.app_context():
        try:
            # Adiciona a coluna documentacao_url se não existir
            db.session.execute('''
                ALTER TABLE seo_tecnico_item 
                ADD COLUMN IF NOT EXISTS documentacao_url VARCHAR(255);
            ''')
            db.session.commit()
            print("Coluna documentacao_url adicionada com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar coluna: {str(e)}")

if __name__ == '__main__':
    add_documentacao_url_column()
