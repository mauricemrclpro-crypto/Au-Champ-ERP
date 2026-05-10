import sqlite3

def init_db():
    conn = sqlite3.connect('gestion_magasin.db')
    cursor = conn.cursor()
    
    # Table des Utilisateurs (Admin et Caissier)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
    # Table des Produits (Stock)
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                   (id INTEGER PRIMARY KEY, nom TEXT, categorie TEXT, prix REAL, stock INTEGER)''')
    
    # Table des Ventes
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventes 
                   (id INTEGER PRIMARY KEY, produit_id INTEGER, quantite INTEGER, date TEXT, total REAL)''')
    
    # Ajout d'utilisateurs par défaut pour tester
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'Admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'caissier1', 'caisse123', 'Caissier')")
    
    conn.commit()
    conn.close()

init_db()

