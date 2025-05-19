import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Configuration de la page
st.set_page_config(layout="wide", page_title="Analyse Gombo-Aubergine-Piment-Tomate Côte d'Ivoire")
st.title("🍅🌶️ Analyse des pratiques de production et consommation")
st.subheader("Gombo - Aubergine - Piment - Tomate en Côte d'Ivoire")

# Style des visualisations
plt.style.use('ggplot')
sns.set_palette("husl")
primary_color = "#2e8b57"  # Couleur verte thématique

# Liste des légumes étudiés
LEGUMES = ['gombo', 'aubergine', 'piment', 'tomate']

# Fonctions optimisées
@st.cache_data(ttl=3600)
def load_and_prepare_data(uploaded_file, sheet_name):
    """Charge et prépare les données avec optimisation mémoire"""
    try:
        # Lecture avec types optimisés - CORRECTION APPLIQUÉE ICI
        dtype = {col: 'category' for col in pd.read_excel(uploaded_file, nrows=1).columns 
                if any(kw in col.lower() for kw in ['region', 'type', 'sexe', 'methode'])}
        
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, dtype=dtype, engine='openpyxl')
        
        # Nettoyage de base
        df = df.dropna(how='all', axis=1).dropna(how='all')
        
        # Conversion des colonnes légumes en catégorielles si besoin
        for col in df.columns:
            if any(legume in col.lower() for legume in LEGUMES):
                if df[col].dtype == 'object' and df[col].nunique() < 20:
                    df[col] = df[col].astype('category')
        
        return df
    except Exception as e:
        st.error(f"Erreur de chargement : {str(e)}")
        return None

[... le reste du code reste inchangé ...]
