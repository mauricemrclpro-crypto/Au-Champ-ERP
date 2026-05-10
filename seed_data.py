import sqlite3

def seed_database():
    conn = sqlite3.connect('gestion_magasin.db')
    cursor = conn.cursor()
    
    # On vide les anciennes données pour le test
    cursor.execute("DELETE FROM products")
    
    # Jeu de données : (Nom, Catégorie, Prix, Stock)
    produits_test = [
        ('Lait Entier 1L', 'Alimentaire', 850, 150),
        ('Riz Parfumé 5kg', 'Alimentaire', 4500, 40),
        ('Huile de Tournesol', 'Alimentaire', 1200, 60),
        ('Savon Liquide 500ml', 'Hygiène', 1500, 100),
        ('Dentifrice Fresh', 'Hygiène', 900, 85),
        ('Shampooing Doux', 'Hygiène', 2200, 30),
        ('Téléviseur LED 43"', 'Électronique', 185000, 5),
        ('Smartphone Android', 'Électronique', 95000, 12),
        ('Machine à café', 'Électronique', 45000, 8),
        ('Pain de campagne', 'Alimentaire', 200, 200),
        ('Pâtes Spaghetti 500g', 'Alimentaire', 450, 300),
        ('Yaourt Nature (Pack de 4)', 'Alimentaire', 1100, 50),
        ('Papier Toilette (Pack de 6)', 'Hygiène', 1800, 120),
        ('Câble HDMI 2m', 'Électronique', 3500, 25),
        ('Batterie de cuisine', 'Maison', 35000, 10)
    ]
    
    cursor.executemany("INSERT INTO products (nom, categorie, prix, stock) VALUES (?, ?, ?, ?)", produits_test)
    
    conn.commit()
    print(f"✅ {len(produits_test)} produits ont été injectés avec succès !")
    conn.close()

if __name__ == "__main__":
    seed_database()