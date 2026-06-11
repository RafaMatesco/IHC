import sqlite3

def create_ecommerce_database():
    conn = sqlite3.connect("ecommerce.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY, nome TEXT, email TEXT, data_cadastro TEXT)""")
        
    c.execute("""CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY, nome TEXT, categoria TEXT, preco REAL, estoque INTEGER)""")
        
    c.execute("""CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY, cliente_id INTEGER, produto_id INTEGER, quantidade INTEGER, status TEXT)""")

    c.executemany("INSERT OR IGNORE INTO clientes VALUES (?, ?, ?, ?)", [
        (1, "João Silva", "joao@email.com", "2023-01-15"),
        (2, "Maria Souza", "maria@email.com", "2023-05-20"),
        (3, "Carlos Oliveira", "carlos@email.com", "2023-08-10")
    ])

    c.executemany("INSERT OR IGNORE INTO produtos VALUES (?, ?, ?, ?, ?)", [
        (1, "Notebook Dell", "Eletrônicos", 3500.00, 10),
        (2, "Smartphone Samsung", "Eletrônicos", 1500.00, 25),
        (3, "Cadeira Gamer", "Móveis", 800.00, 5)
    ])

    c.executemany("INSERT OR IGNORE INTO pedidos VALUES (?, ?, ?, ?, ?)", [
        (1, 1, 1, 1, "Entregue"),
        (2, 2, 2, 2, "Enviado"),
        (3, 1, 3, 1, "Pendente")
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_ecommerce_database()
    print("Banco de dados inicializado com sucesso!")