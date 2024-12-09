import sqlite3

def check_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tarefa'")
    if cursor.fetchone() is None:
        print("A tabela 'tarefa' não existe!")
        return
    
    # Obter informações sobre as colunas
    cursor.execute("PRAGMA table_info(tarefa)")
    columns = cursor.fetchall()
    
    print("\nColunas na tabela 'tarefa':")
    for col in columns:
        print(f"Nome: {col[1]}, Tipo: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
    
    conn.close()

if __name__ == '__main__':
    check_table()
