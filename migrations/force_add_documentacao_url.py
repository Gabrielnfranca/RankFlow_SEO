from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

def force_add_documentacao_url():
    # Obtém a URL do banco de dados dos env vars
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("Erro: DATABASE_URL não configurada")
        return
    
    try:
        # Cria uma conexão direta com o banco
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Verifica se a coluna existe
            check_column_query = text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'seo_tecnico_item' 
                    AND column_name = 'documentacao_url'
                )
            """)
            
            column_exists = connection.execute(check_column_query).scalar()
            
            if not column_exists:
                # Adiciona a coluna se não existir
                add_column_query = text("""
                    ALTER TABLE seo_tecnico_item 
                    ADD COLUMN documentacao_url VARCHAR(255);
                """)
                
                connection.execute(add_column_query)
                connection.commit()
                print("Coluna documentacao_url adicionada com sucesso!")
            else:
                print("Coluna documentacao_url já existe.")
    
    except SQLAlchemyError as e:
        print(f"Erro ao adicionar coluna: {str(e)}")

if __name__ == '__main__':
    force_add_documentacao_url()
