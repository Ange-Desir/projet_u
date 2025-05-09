import streamlit as st  
import pandas as pd  

# Config de la page  
st.set_page_config(page_title="Gestion Maquis", layout="wide")  

# Charger les données (simulées ou depuis Google Sheets)  
def load_data():  
    return pd.DataFrame({  
        "Produit": ["Poulet", "Poisson", "Attiéké"],  
        "Stock": [15, 8, 20],  
        "Prix": [2500, 3000, 1000]  
    })  

# Afficher le formulaire de saisie  
st.title("📊 Gestion du Maquis")  
with st.form("saisie_vente"):  
    produit = st.selectbox("Produit", load_data()["Produit"])  
    quantite = st.number_input("Quantité", min_value=1)  
    submitted = st.form_submit_button("Enregistrer")  
    if submitted:  
        st.success(f"✅ Vente enregistrée : {quantite} {produit}")  
        # Ici : Ajouter la logique pour mettre à jour les stocks/chiffre d'affaires  

# Afficher les données  
st.header("📦 Stocks")  
st.dataframe(load_data(), hide_index=True)  

# Alertes stocks bas  
st.header("🚨 Alertes")  
for index, row in load_data().iterrows():  
    if row["Stock"] < 10:  
        st.warning(f"Stock bas : {row['Produit']} ({row['Stock']} restants)")
