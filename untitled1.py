import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Gestion Maquis", page_icon="🍽️", layout="wide")

# Initialisation des données
if "stocks" not in st.session_state:
    st.session_state.stocks = pd.DataFrame({
        "Produit": ["Poulet", "Poisson", "Attiéké", "Plantain"],
        "Stock": [15, 8, 20, 12],
        "Prix": [2500, 3000, 1000, 800],
        "Seuil Alerte": [5, 5, 5, 5]  # Seuil personnalisable par produit
    })

if "historique" not in st.session_state:
    st.session_state.historique = []

# Fonctions principales
def enregistrer_vente(produit, quantite):
    """Met à jour le stock et l'historique"""
    index = st.session_state.stocks[st.session_state.stocks["Produit"] == produit].index[0]
    st.session_state.stocks.at[index, "Stock"] -= quantite
    
    st.session_state.historique.append({
        "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Produit": produit,
        "Quantité": quantite,
        "Prix Unitaire": st.session_state.stocks.at[index, "Prix"],
        "Total": quantite * st.session_state.stocks.at[index, "Prix"]
    })

# Interface utilisateur
st.title("🍽️ Gestion du Maquis - Tableau de Bord")

# Section 1: Saisie des ventes
with st.expander("📝 Enregistrer une vente", expanded=True):
    with st.form("vente_form"):
        col1, col2 = st.columns(2)
        produit = col1.selectbox("Produit", st.session_state.stocks["Produit"])
        quantite = col2.number_input("Quantité", min_value=1, max_value=100, value=1)
        
        if st.form_submit_button("💾 Enregistrer"):
            enregistrer_vente(produit, quantite)
            st.success(f"Vente enregistrée : {quantite} {produit}")
            st.rerun()

# Section 2: Tableaux de bord
tab1, tab2, tab3 = st.tabs(["📦 Stocks", "📈 Historique", "🚨 Alertes"])

with tab1:
    st.subheader("Niveaux de stock actuels")
    st.dataframe(
        st.session_state.stocks.style.applymap(
            lambda x: "background-color: #FFCCCB" if x < st.session_state.stocks["Seuil Alerte"].iloc[0] else "",
            subset=["Stock"]
        ),
        use_container_width=True
    )

with tab2:
    if st.session_state.historique:
        df_historique = pd.DataFrame(st.session_state.historique)
        st.subheader("Dernières ventes")
        st.dataframe(df_historique.sort_values("Date", ascending=False), use_container_width=True)
        
        total_journalier = df_historique[df_historique["Date"].str.startswith(datetime.now().strftime("%d/%m/%Y"))]["Total"].sum()
        st.metric("Chiffre d'affaires aujourd'hui", f"{total_journalier:,} XOF")
    else:
        st.info("Aucune vente enregistrée aujourd'hui")

with tab3:
    st.subheader("Alertes stock")
    produits_alertes = st.session_state.stocks[st.session_state.stocks["Stock"] < st.session_state.stocks["Seuil Alerte"]]
    
    if not produits_alertes.empty:
        for _, row in produits_alertes.iterrows():
            st.warning(f"{row['Produit']} : Seulement {row['Stock']} restants (seuil à {row['Seuil Alerte']})")
    else:
        st.success("Aucun stock critique")

# Section 3: Réapprovisionnement
with st.expander("🛒 Gestion des stocks"):
    st.subheader("Réapprovisionnement")
    produit_reappro = st.selectbox("Produit à réapprovisionner", st.session_state.stocks["Produit"])
    quantite_reappro = st.number_input("Quantité à ajouter", min_value=1, value=1)
    
    if st.button("Valider l'ajout"):
        index = st.session_state.stocks[st.session_state.stocks["Produit"] == produit_reappro].index[0]
        st.session_state.stocks.at[index, "Stock"] += quantite_reappro
        st.success(f"{quantite_reappro} {produit_reappro} ajoutés au stock")
        st.rerun()

# Fonctionnalité export
st.sidebar.download_button(
    label="📤 Exporter les données",
    data=st.session_state.stocks.to_csv(index=False).encode('utf-8'),
    file_name=f"stocks_maquis_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
