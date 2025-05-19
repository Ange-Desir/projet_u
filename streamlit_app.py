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
        # Lecture avec types optimisés
        dtype = {col: 'category' for col in pd.read_excel(uploaded_file, nrows=1).columns 
                if any(kw in col.lower() for kw in ['region', 'type', 'sexe', 'methode']}
        
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

# Interface utilisateur
uploaded_file = st.file_uploader("Téléversez votre fichier de données (Excel)", type=["xlsx"])

if uploaded_file:
    # Sélection de la feuille
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    sheet_name = st.selectbox("Sélectionnez la feuille à analyser", sheet_names)
    
    # Chargement des données
    with st.spinner('Chargement et préparation des données...'):
        df = load_and_prepare_data(uploaded_file, sheet_name)
        
        if df is not None:
            st.session_state.df = df
            st.success(f"Données chargées avec succès ({len(df)} lignes)")

    if 'df' in st.session_state:
        df = st.session_state.df
        
        # Onglets d'analyse
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Aperçu", "🌱 Production", "🛒 Consommation", "📈 Comparaisons"])
        
        with tab1:
            st.header("Aperçu des données")
            st.write("5 premières lignes :")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.checkbox("Afficher les statistiques descriptives"):
                st.dataframe(df.describe(include='all'), use_container_width=True)
        
        with tab2:
            st.header("Analyse des pratiques de production")
            
            # Détection automatique des colonnes pertinentes
            prod_cols = {
                'superficie': [c for c in df.columns if 'superficie' in c.lower()],
                'rendement': [c for c in df.columns if 'rendement' in c.lower()],
                'methode': [c for c in df.columns if 'methode' in c.lower()],
                'region': [c for c in df.columns if 'region' in c.lower()]
            }
            
            if prod_cols['superficie']:
                fig, ax = plt.subplots(figsize=(10, 6))
                for legume in LEGUMES:
                    legume_cols = [c for c in prod_cols['superficie'] if legume in c.lower()]
                    if legume_cols:
                        sns.histplot(df[legume_cols[0]].dropna(), kde=True, label=legume.capitalize())
                ax.set_title("Distribution des superficies cultivées par légume")
                ax.set_xlabel("Superficie (ha)")
                ax.legend()
                st.pyplot(fig)
                plt.close()
            
            if prod_cols['region'] and prod_cols['rendement']:
                region = st.selectbox("Sélectionnez une région", df[prod_cols['region'][0]].unique())
                filtered = df[df[prod_cols['region'][0]] == region]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for legume in LEGUMES:
                    rend_cols = [c for c in prod_cols['rendement'] if legume in c.lower()]
                    if rend_cols:
                        ax.bar(legume.capitalize(), filtered[rend_cols[0]].mean(), color=primary_color)
                ax.set_title(f"Rendements moyens par légume - {region}")
                ax.set_ylabel("Rendement (tonnes/ha)")
                st.pyplot(fig)
                plt.close()
        
        with tab3:
            st.header("Analyse des pratiques de consommation")
            
            # Détection automatique des colonnes
            cons_cols = {
                'frequence': [c for c in df.columns if 'frequence' in c.lower()],
                'quantite': [c for c in df.columns if 'quantite' in c.lower()],
                'prix': [c for c in df.columns if 'prix' in c.lower()],
                'preference': [c for c in df.columns if 'preference' in c.lower()]
            }
            
            if cons_cols['frequence']:
                legume_freq = st.selectbox("Choisissez un légume pour l'analyse", LEGUMES)
                freq_cols = [c for c in cons_cols['frequence'] if legume_freq in c.lower()]
                
                if freq_cols:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    df[freq_cols[0]].value_counts().plot(kind='bar', ax=ax, color=primary_color)
                    ax.set_title(f"Fréquence de consommation - {legume_freq.capitalize()}")
                    ax.set_xlabel("Fréquence")
                    ax.set_ylabel("Nombre de consommateurs")
                    st.pyplot(fig)
                    plt.close()
            
            if cons_cols['prix'] and cons_cols['quantite']:
                st.subheader("Relation prix/quantité consommée")
                legume_pq = st.selectbox("Choisissez un légume", LEGUMES, key='pq_legume')
                prix_cols = [c for c in cons_cols['prix'] if legume_pq in c.lower()]
                qte_cols = [c for c in cons_cols['quantite'] if legume_pq in c.lower()]
                
                if prix_cols and qte_cols:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(data=df, x=prix_cols[0], y=qte_cols[0], hue=df[prod_cols['region'][0]] if prod_cols['region'] else None)
                    ax.set_title(f"Relation prix/quantité pour {legume_pq.capitalize()}")
                    ax.set_xlabel("Prix (FCFA)")
                    ax.set_ylabel("Quantité consommée (kg/mois)")
                    st.pyplot(fig)
                    plt.close()
        
        with tab4:
            st.header("Comparaisons entre légumes")
            
            # Comparaison des superficies
            if prod_cols['superficie']:
                st.subheader("Comparaison des superficies cultivées")
                sup_data = []
                for legume in LEGUMES:
                    legume_cols = [c for c in prod_cols['superficie'] if legume in c.lower()]
                    if legume_cols:
                        sup_data.append(df[legume_cols[0]].mean())
                
                if sup_data:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar([l.capitalize() for l in LEGUMES], sup_data, color=primary_color)
                    ax.set_title("Superficie moyenne cultivée par légume")
                    ax.set_ylabel("Hectares moyens")
                    st.pyplot(fig)
                    plt.close()
            
            # Comparaison des fréquences de consommation
            if cons_cols['frequence']:
                st.subheader("Comparaison des fréquences de consommation")
                freq_data = []
                for legume in LEGUMES:
                    legume_cols = [c for c in cons_cols['frequence'] if legume in c.lower()]
                    if legume_cols:
                        # Conversion des fréquences en scores numériques
                        freq_map = {'Quotidien': 7, 'Hebdomadaire': 4, 'Mensuel': 1, 'Occasionnel': 0.5}
                        df['freq_score'] = df[legume_cols[0]].map(freq_map)
                        freq_data.append(df['freq_score'].mean())
                
                if freq_data:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar([l.capitalize() for l in LEGUMES], freq_data, color=primary_color)
                    ax.set_title("Fréquence moyenne de consommation")
                    ax.set_ylabel("Jours moyens/semaine")
                    st.pyplot(fig)
                    plt.close()

        # Export des résultats
        st.sidebar.header("Options d'export")
        if st.sidebar.button("Exporter les graphiques"):
            with st.spinner("Préparation de l'export..."):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Donnees_brutes', index=False)
                    
                    # Ajout des stats par légume
                    for legume in LEGUMES:
                        legume_cols = [c for c in df.columns if legume in c.lower()]
                        if legume_cols:
                            df[legume_cols].describe().to_excel(writer, sheet_name=f'Stats_{legume}')
                
                st.sidebar.download_button(
                    label="📥 Télécharger les résultats",
                    data=output.getvalue(),
                    file_name="resultats_analyse_legumes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
