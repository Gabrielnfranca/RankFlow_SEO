import sqlite3
import os

def init_db():
    # Remove o banco de dados existente
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Conecta ao banco de dados (isso criará um novo)
    conn = sqlite3.connect('database.db')
    
    # Lê o arquivo schema.sql
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Executa os comandos SQL
    conn.executescript(schema)
    
    # Commit e fecha a conexão
    conn.commit()
    conn.close()
    
    print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_db()
