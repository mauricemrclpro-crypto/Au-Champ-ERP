import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Au - Champ ERP", layout="wide", page_icon="🛒")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #E30613; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border-left: 6px solid #E30613; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #E30613; }
    .ticket-box { background-color: #fff; padding: 25px; border: 2px dashed #333; font-family: 'Courier New', monospace; color: #000; }
    .warning-text { color: #E30613; font-weight: bold; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION DE BASE DE DONNÉES (CORRECTIF MYSQL) ---
def run_query(query, params=(), fetch=False):
    # Connexion au serveur MySQL de XAMPP
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="au_champ_db"
    )
    
    # SOLUTION À L'ERREUR : MySQL utilise %s au lieu de ?
    query = query.replace('?', '%s')
    
    # dictionary=True pour garder la compatibilité avec vos accès par nom de colonne
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
    except mysql.connector.Error as err:
        st.error(f"Erreur MySQL : {err}")
    finally:
        cursor.close()
        conn.close()

# --- INITIALISATION SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 'user_role': None, 'username': None, 
        'panier': [], 'dernier_ticket': None
    })

# --- FONCTION GÉNÉRATION TICKET ---
def get_ticket_text(ticket):
    txt = f"      AU - CHAMP\n   RECU DE VENTE\n"
    txt += "="*30 + "\n"
    txt += f"Ticket ID: {ticket['id']}\nDate: {ticket['date']}\n"
    txt += "-"*30 + "\n"
    for i in ticket['items']:
        txt += f"{i['Nom'][:15]:<15} x{i['Qte']} : {i['Total']} FCFA\n"
    txt += "-"*30 + "\n"
    txt += f"TOTAL PAYE: {ticket['total']:,.0f} FCFA\n"
    txt += "="*30 + "\nMerci de votre visite !"
    return txt

# --- PAGE DE CONNEXION ---
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<br>", unsafe_allow_html=True)
        buff, col_logo, buff2 = st.columns([1, 2, 1])
        with col_logo:
            try: st.image("logo(2).jpg", use_container_width=True)
            except: st.markdown("<h2 style='text-align: center; color: #E30613;'>Au - Champ</h2>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>Authentification</h3>", unsafe_allow_html=True)
            u = st.text_input("👤 Identifiant")
            p = st.text_input("🔑 Mot de passe", type="password")
            if st.button("SE CONNECTER"):
                # Ici, le ? sera remplacé par %s automatiquement par run_query
                res = run_query("SELECT role FROM users WHERE username = ? AND password = ?", (u, p), fetch=True)
                if res:
                    # Accès via le nom de colonne 'role' grâce au dictionnaire
                    st.session_state.update({'logged_in': True, 'user_role': res[0]['role'], 'username': u})
                    st.toast(f"Connexion réussie", icon="✅")
                    st.rerun()
                else: st.error("Identifiants incorrects.")
    st.stop()

# --- NAVIGATION ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.update({'logged_in': False, 'panier': [], 'dernier_ticket': None})
    st.rerun()

menu = ["🏠 Accueil"]
if st.session_state.user_role == "Admin":
    menu += ["📊 Dashboard", "📦 Inventaire & Stocks", "👥 Utilisateurs"]
else:
    menu += ["💳 Caisse"]
choice = st.sidebar.radio("Navigation", menu)

# --- 💳 CAISSE ---
if choice == "💳 Caisse":
    st.title("📟 Terminal de Vente")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("🔍 Sélection")
        prods = run_query("SELECT id, nom, prix, stock FROM products WHERE stock > 0", fetch=True)
        if prods:
            df_p = pd.DataFrame(prods)
            search = st.selectbox("Choisir produit", df_p['nom'])
            sel = df_p[df_p['nom'] == search].iloc[0]
            
            if sel['stock'] < 15:
                st.markdown(f"<p class='warning-text'>⚠️ RUPTURE PROCHE : Il ne reste que {sel['stock']} unités !</p>", unsafe_allow_html=True)
            
            st.metric("Prix", f"{sel['prix']} FCFA", f"Stock: {sel['stock']}")
            q = st.number_input("Quantité", 1, int(sel['stock']), 1)
            if st.button("🛒 Ajouter au Panier"):
                st.session_state.panier.append({"ID": int(sel['id']), "Nom": search, "Prix": float(sel['prix']), "Qte": int(q), "Total": float(sel['prix']*q)})
                st.toast(f"{search} ajouté !", icon="🛒")
                st.rerun()
    with c2:
        st.subheader("🧾 Encaissement")
        if st.session_state.panier:
            df_panier = pd.DataFrame(st.session_state.panier)
            st.table(df_panier[['Nom', 'Qte', 'Total']])
            total_v = df_panier['Total'].sum()
            st.markdown(f"## Total : {total_v:,.0f} FCFA")
            if st.button("✅ Valider la Vente", type="primary"):
                tid = datetime.now().strftime("%Y%m%d%H%M")
                for item in st.session_state.panier:
                    run_query("UPDATE products SET stock = stock - ? WHERE id = ?", (item['Qte'], item['ID']))
                    run_query("INSERT INTO ventes (produit_id, quantite, date, total, ticket_id) VALUES (?,?,?,?,?)", 
                             (item['ID'], item['Qte'], datetime.now().strftime("%Y-%m-%d %H:%M"), item['Total'], tid))
                st.session_state.dernier_ticket = {"id": tid, "items": st.session_state.panier.copy(), "total": total_v, "date": datetime.now().strftime("%d/%m/%Y %H:%M")}
                st.session_state.panier = []
                st.success("Vente enregistrée !")
                st.rerun()
        if st.session_state.dernier_ticket:
            dt = st.session_state.dernier_ticket
            st.download_button("📥 Télécharger Ticket", get_ticket_text(dt), f"ticket_{dt['id']}.txt")
            if st.button("🔄 Nouvelle Vente"):
                st.session_state.dernier_ticket = None
                st.rerun()

# --- 📊 DASHBOARD ---
elif choice == "📊 Dashboard":
    st.title("📊 Analyses de Performance")
    data = run_query("SELECT v.date, p.nom, v.quantite, v.total FROM ventes v JOIN products p ON v.produit_id = p.id", fetch=True)
    if data:
        df = pd.DataFrame(data)
        df.columns = ['Date', 'Produit', 'Qté', 'Total']
        col1, col2 = st.columns(2)
        col1.metric("Chiffre d'Affaires", f"{df['Total'].sum():,.0f} FCFA")
        col2.metric("Volume Ventes", f"{df['Qté'].sum()} articles")
        st.subheader("Répartition par Produit")
        st.bar_chart(df.groupby('Produit')['Total'].sum())
    else: st.info("Aucune donnée.")

# --- 📦 INVENTAIRE ---
elif choice == "📦 Inventaire & Stocks":
    st.title("📦 Logistique & Catalogue")
    stock_raw = run_query("SELECT * FROM products", fetch=True)
    df_s = pd.DataFrame(stock_raw)
    df_s.columns = ['ID', 'Nom', 'Catégorie', 'Prix', 'Stock']
    
    ruptures = df_s[df_s['Stock'] < 15]
    if not ruptures.empty:
        st.error(f"🚨 ALERTE RUPTURE : {len(ruptures)} produit(s) sous le seuil de sécurité !")
        with st.expander("👁️ Voir les produits"):
            st.table(ruptures[['Nom', 'Stock']])

    st.subheader("Inventaire Complet")
    def highlight_low_stock(s):
        return ['background-color: #ffcccc' if s.Stock < 15 else '' for _ in s]
    st.dataframe(df_s.style.apply(highlight_low_stock, axis=1), use_container_width=True, hide_index=True)
    
    t1, t2, t3 = st.tabs(["🔄 Réapprovisionnement", "✨ Nouveau Référencement", "🗑️ Gestion"])
    with t1:
        with st.form("reassort"):
            p_sel = st.selectbox("Article", df_s['Nom'])
            q_add = st.number_input("Quantité reçue", min_value=1)
            if st.form_submit_button("✅ Valider"):
                run_query("UPDATE products SET stock = stock + ? WHERE nom = ?", (q_add, p_sel))
                st.success("Stock mis à jour !")
                st.rerun()
    with t2:
        with st.form("nouveau"):
            n_nom = st.text_input("Nom")
            n_cat = st.selectbox("Catégorie", ["Alimentaire", "Hygiène", "Electronique", "Divers"])
            n_prix = st.number_input("Prix", min_value=0)
            n_stock = st.number_input("Stock initial", min_value=0)
            if st.form_submit_button("💾 Enregistrer"):
                if n_nom:
                    run_query("INSERT INTO products (nom, categorie, prix, stock) VALUES (?,?,?,?)", (n_nom, n_cat, n_prix, n_stock))
                    st.success("Produit ajouté !")
                    st.rerun()
    with t3:
        with st.form("suppr"):
            p_del = st.selectbox("Article à supprimer", df_s['Nom'])
            confirm = st.checkbox("Confirmer la suppression")
            if st.form_submit_button("🗑️ Supprimer"):
                if confirm:
                    run_query("DELETE FROM products WHERE nom = ?", (p_del,))
                    st.success("Supprimé !")
                    st.rerun()

# --- 👥 UTILISATEURS ---
elif choice == "👥 Utilisateurs":
    st.title("👥 Gestion Personnel")
    users = run_query("SELECT username, role FROM users", fetch=True)
    st.table(pd.DataFrame(users))
    with st.form("user"):
        un = st.text_input("Identifiant")
        up = st.text_input("Mot de passe", type="password")
        ur = st.selectbox("Rôle", ["Admin", "Caissier"])
        if st.form_submit_button("Créer compte"):
            if un and up:
                run_query("INSERT INTO users (username, password, role) VALUES (?,?,?)", (un, up, ur))
                st.success("Compte créé !")
                st.rerun()

# --- 🏠 ACCUEIL ---
else:
    st.title("🏠 Au - Champ ERP")
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        try: st.image("logo(2).jpg", use_container_width=True)
        except: pass
    st.info(f"Session active : {st.session_state.username}")