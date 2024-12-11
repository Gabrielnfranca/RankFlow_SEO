from flask import current_app
from sqlalchemy import text
from app import db, app

def add_documentacao_url_column():
    with app.app_context():
        try:
            # Verifica se a coluna já existe
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('seo_tecnico_item')
            column_names = [col['name'] for col in columns]
            
            if 'documentacao_url' not in column_names:
                # Adiciona a coluna se não existir
                db.session.execute(text('''
                    ALTER TABLE seo_tecnico_item 
                    ADD COLUMN documentacao_url VARCHAR(255);
                '''))
                db.session.commit()
                print("Coluna documentacao_url adicionada com sucesso!")
            else:
                print("Coluna documentacao_url já existe.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar coluna: {str(e)}")

if __name__ == '__main__':
    add_documentacao_url_column()
