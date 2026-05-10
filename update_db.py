import sqlite3
conn = sqlite3.connect('gestion_magasin.db')
try:
    conn.execute("ALTER TABLE ventes ADD COLUMN ticket_id TEXT")
    conn.commit()
    print("Base de données mise à jour !")
except:
    print("La colonne existe déjà.")
conn.close()