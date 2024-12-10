from app import app, db
from app import Usuario, Cliente, Tarefa, EtapaSEO, ProgressoSEO

def check_tables():
    with app.app_context():
        # Verifica se as tabelas existem
        tables = db.engine.table_names()
        print("Tabelas existentes:", tables)
        
        # Tenta criar as tabelas
        try:
            db.create_all()
            print("Tabelas criadas/verificadas com sucesso!")
        except Exception as e:
            print("Erro ao criar tabelas:", str(e))
        
        # Verifica se existe usuário admin
        admin = Usuario.query.filter_by(email='admin@admin.com').first()
        if admin:
            print("Usuário admin existe!")
        else:
            print("Usuário admin não encontrado!")

if __name__ == '__main__':
    check_tables()
