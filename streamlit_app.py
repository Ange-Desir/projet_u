import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import numpy as np

# Configuration de l'application
st.set_page_config(layout="wide", page_title="Analyse Production-Consommation")
st.title("🍅🌶️ Analyse des pratiques maraîchères en Côte d'Ivoire")
st.markdown("""
**Thème du mémoire :**  
Analyse des pratiques de production et de consommation de 4 légumes-fruits (gombo, aubergine, piment, tomate)
""")

# Paramètres visuels
plt.style.use('seaborn')
sns.set_palette("husl")
COLORS = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2"]
LEGUMES = ['gombo', 'aubergine', 'piment', 'tomate']

# Fonctions de chargement optimisé
@st.cache_data(ttl=3600)
def load_data(uploaded_file, sheet_name=None):
    """Charge un fichier Excel avec optimisation mémoire"""
    try:
        # Détection automatique des colonnes catégorielles
        sample = pd.read_excel(uploaded_file, nrows=100)
        dtype = {col: 'category' for col in sample.columns 
                if sample[col].nunique() < 20 and sample[col].dtype == 'object'}
        
        return pd.read_excel(uploaded_file, sheet_name=sheet_name, dtype=dtype, engine='openpyxl')
    except Exception as e:
        st.error(f"Erreur de chargement : {str(e)}")
        return None

def detect_columns(df):
    """Détecte automatiquement les colonnes pertinentes"""
    cols = {
        'production': {'superficie': [], 'rendement': [], 'region': [], 'methode': []},
        'consommation': {'frequence': [], 'quantite': [], 'prix': [], 'preference': []}
    }
    
    if df is not None:
        for col in df.columns:
            col_lower = col.lower()
            # Détection pour la production
            if any(legume in col_lower for legume in LEGUMES):
                if 'superficie' in col_lower:
                    cols['production']['superficie'].append(col)
                elif 'rendement' in col_lower:
                    cols['production']['rendement'].append(col)
            
            # Détection générale
            if 'region' in col_lower:
                cols['production']['region'].append(col)
                cols['consommation']['region'].append(col)
            elif 'methode' in col_lower:
                cols['production']['methode'].append(col)
            elif 'frequence' in col_lower:
                cols['consommation']['frequence'].append(col)
            elif 'quantite' in col_lower:
                cols['consommation']['quantite'].append(col)
            elif 'prix' in col_lower:
                cols['consommation']['prix'].append(col)
            elif 'preference' in col_lower:
                cols['consommation']['preference'].append(col)
    
    return cols

# Interface utilisateur
st.sidebar.header("Chargement des fichiers")
uploaded_file1 = st.sidebar.file_uploader("Fichier 1 (Production)", type=["xlsx"])
uploaded_file2 = st.sidebar.file_uploader("Fichier 2 (Consommation)", type=["xlsx"])

if uploaded_file1 or uploaded_file2:
    # Chargement des données
    dfs = {}
    cols_info = {}
    
    if uploaded_file1:
        sheet_names1 = pd.ExcelFile(uploaded_file1).sheet_names
        sheet1 = st.sidebar.selectbox("Feuille (Fichier 1)", sheet_names1, key="sheet1")
        dfs['f1'] = load_data(uploaded_file1, sheet1)
        cols_info['f1'] = detect_columns(dfs['f1'])
    
    if uploaded_file2:
        sheet_names2 = pd.ExcelFile(uploaded_file2).sheet_names
        sheet2 = st.sidebar.selectbox("Feuille (Fichier 2)", sheet_names2, key="sheet2")
        dfs['f2'] = load_data(uploaded_file2, sheet2)
        cols_info['f2'] = detect_columns(dfs['f2'])
    
    # Onglets d'analyse
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Aperçu", "🌱 Production", "🛒 Consommation", "🔄 Comparaisons"])
    
    with tab1:
        st.header("Aperçu des données")
        
        if uploaded_file1 and 'f1' in dfs:
            st.subheader("Fichier Production")
            st.dataframe(dfs['f1'].head(3))
            st.write(f"Colonnes détectées : {cols_info['f1']}")
        
        if uploaded_file2 and 'f2' in dfs:
            st.subheader("Fichier Consommation")
            st.dataframe(dfs['f2'].head(3))
            st.write(f"Colonnes détectées : {cols_info['f2']}")
    
    with tab2:
        st.header("Analyse Production")
        if uploaded_file1 and 'f1' in dfs:
            df = dfs['f1']
            cols = cols_info['f1']['production']
            
            if cols['superficie']:
                st.subheader("Superficies cultivées")
                fig, ax = plt.subplots(figsize=(12, 6))
                for legume, color in zip(LEGUMES, COLORS):
                    legume_cols = [c for c in cols['superficie'] if legume in c.lower()]
                    if legume_cols:
                        sns.histplot(df[legume_cols[0]].dropna(), kde=True, 
                                    color=color, label=legume.capitalize())
                ax.set_title("Distribution des superficies par légume")
                ax.legend()
                st.pyplot(fig)
            
            if cols['region'] and cols['rendement']:
                st.subheader("Rendement par région")
                region_col = cols['region'][0]
                selected_region = st.selectbox("Choisir une région", df[region_col].unique(), key="prod_region")
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for legume, color in zip(LEGUMES, COLORS):
                    rend_cols = [c for c in cols['rendement'] if legume in c.lower()]
                    if rend_cols:
                        region_data = df[df[region_col] == selected_region]
                        ax.bar(legume.capitalize(), region_data[rend_cols[0]].mean(), 
                               color=color)
                ax.set_title(f"Rendement moyen - {selected_region}")
                st.pyplot(fig)
    
    with tab3:
        st.header("Analyse Consommation")
        if uploaded_file2 and 'f2' in dfs:
            df = dfs['f2']
            cols = cols_info['f2']['consumption']
            
            if cols['frequence']:
                st.subheader("Fréquence de consommation")
                selected_legume = st.selectbox("Choisir un légume", LEGUMES, key="cons_legume")
                freq_cols = [c for c in cols['frequence'] if selected_legume in c.lower()]
                
                if freq_cols:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    df[freq_cols[0]].value_counts().plot(kind='bar', ax=ax)
                    ax.set_title(f"Fréquence de consommation - {selected_legume.capitalize()}")
                    st.pyplot(fig)
            
            if cols['prix'] and cols['quantite']:
                st.subheader("Relation Prix-Quantité")
                legume_pq = st.selectbox("Choisir un légume", LEGUMES, key="pq_legume")
                prix_cols = [c for c in cols['prix'] if legume_pq in c.lower()]
                qte_cols = [c for c in cols['quantite'] if legume_pq in c.lower()]
                
                if prix_cols and qte_cols:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(data=df, x=prix_cols[0], y=qte_cols[0])
                    ax.set_title(f"Relation prix/quantité - {legume_pq.capitalize()}")
                    st.pyplot(fig)
    
    with tab4:
        st.header("Analyses comparatives")
        
        if uploaded_file1 and uploaded_file2 and 'f1' in dfs and 'f2' in dfs:
            df_prod = dfs['f1']
            df_cons = dfs['f2']
            
            # Comparaison régionale
            if cols_info['f1']['production']['region'] and cols_info['f2']['consumption']['region']:
                st.subheader("Répartition géographique comparée")
                col1, col2 = st.columns(2)
                
                with col1:
                    prod_region = cols_info['f1']['production']['region'][0]
                    st.write("**Production**")
                    fig1, ax1 = plt.subplots()
                    df_prod[prod_region].value_counts().plot(kind='bar', ax=ax1)
                    st.pyplot(fig1)
                
                with col2:
                    cons_region = cols_info['f2']['consumption']['region'][0]
                    st.write("**Consommation**")
                    fig2, ax2 = plt.subplots()
                    df_cons[cons_region].value_counts().plot(kind='bar', ax=ax2)
                    st.pyplot(fig2)
            
            # Analyse adéquation production-consommation
            st.subheader("Adéquation production-consommation")
            selected_legume = st.selectbox("Choisir un légume", LEGUMES, key="comp_legume")
            
            # Calcul des indicateurs (exemple simplifié)
            if (cols_info['f1']['production']['rendement'] and 
                cols_info['f2']['consumption']['frequence']):
                rend_col = [c for c in cols_info['f1']['production']['rendement'] 
                          if selected_legume in c.lower()][0]
                freq_col = [c for c in cols_info['f2']['consumption']['frequence'] 
                          if selected_legume in c.lower()][0]
                
                prod_mean = df_prod[rend_col].mean()
                cons_freq = df_cons[freq_col].value_counts(normalize=True).get('Quotidien', 0)
                
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(['Production (rendement)', 'Consommation (quotidien)'], 
                       [prod_mean, cons_freq*100])
                ax.set_title(f"Indicateurs clés - {selected_legume.capitalize()}")
                ax.set_ylabel("Valeur")
                st.pyplot(fig)

    # Export des résultats
    st.sidebar.header("Export des résultats")
    if st.sidebar.button("Générer le rapport complet"):
        with st.spinner("Préparation du rapport..."):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if uploaded_file1 and 'f1' in dfs:
                    dfs['f1'].to_excel(writer, sheet_name='Production', index=False)
                if uploaded_file2 and 'f2' in dfs:
                    dfs['f2'].to_excel(writer, sheet_name='Consommation', index=False)
            
            st.sidebar.download_button(
                label="📥 Télécharger le rapport",
                data=output.getvalue(),
                file_name="rapport_analyse.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
