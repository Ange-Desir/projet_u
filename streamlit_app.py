import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Configuration minimale
st.set_page_config(layout="wide")
st.title("Analyse des pratiques maraîchères (Optimisé grands fichiers)")

# Optimisation mémoire
@st.cache_data(show_spinner=False, ttl=3600)
def load_large_file(uploaded_file, sheet_name, sample_size=10000):
    """
    Charge un échantillon du fichier ou utilise des types optimisés
    """
    # D'abord lire juste les en-têtes pour obtenir la structure
    header = pd.read_excel(uploaded_file, sheet_name=sheet_name, nrows=1).columns
    
    # Déterminer les types de données pour optimisation
    dtype_dict = {col: 'category' for col in header if col.startswith(('id', 'code', 'type'))}
    
    # Lire un échantillon ou le fichier entier selon la taille
    try:
        chunks = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name,
            dtype=dtype_dict,
            engine='openpyxl',
            chunksize=10000
        )
        df = pd.concat([chunk.sample(min(1000, len(chunk))) for chunk in chunks])
    except:
        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name,
            dtype=dtype_dict,
            engine='openpyxl',
            nrows=sample_size
        )
    
    return df

def clean_data_optimized(df):
    """Nettoyage optimisé pour grands datasets"""
    # Suppression des colonnes entièrement vides
    df = df.dropna(how='all', axis=1)
    
    # Conversion de types pour économiser la mémoire
    for col in df.select_dtypes(include=['object']):
        if df[col].nunique() / len(df) < 0.5:  # Si peu de valeurs uniques
            df[col] = df[col].astype('category')
    
    return df

# Interface utilisateur
uploaded_file = st.file_uploader("Téléversez un fichier Excel (max 200MB)", type=["xlsx"])

if uploaded_file:
    # Vérification taille fichier
    if uploaded_file.size > 200 * 1024 * 1024:  # 200MB
        st.warning("Fichier très volumineux détecté. Un échantillon sera utilisé.")
    
    with st.spinner('Analyse du fichier en cours...'):
        # Liste des feuilles avec gestion d'erreur
        try:
            sheet_names = pd.ExcelFile(uploaded_file).sheet_names
            sheet = st.selectbox("Feuille à analyser", sheet_names)
            
            # Chargement optimisé
            df = load_large_file(uploaded_file, sheet)
            df = clean_data_optimized(df)
            
            # Sauvegarde en mémoire cache
            st.session_state['current_df'] = df
            
        except Exception as e:
            st.error(f"Erreur de lecture : {str(e)}")
            st.stop()

    # Affichage optimisé
    st.write(f"Échantillon analysé ({len(df)} lignes) :")
    st.dataframe(df.head(), height=200)  # Taille fixe
    
    # Statistiques basiques
    if st.checkbox("Afficher les stats de base"):
        stats = df.describe(include='all').fillna('-')
        st.dataframe(stats, height=300)
    
    # Visualisations optimisées
    st.subheader("Analyse visuelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            num_col = st.selectbox("Variable numérique", num_cols)
            
            fig, ax = plt.subplots(figsize=(8,4))
            ax.hist(df[num_col].dropna(), bins=min(50, len(df[num_col].unique())))
            ax.set_title(f"Distribution de {num_col}")
            st.pyplot(fig, clear_figure=True)
            plt.close()
    
    with col2:
        cat_cols = df.select_dtypes(include=['category', 'object']).columns.tolist()
        if cat_cols and num_cols:
            cat_col = st.selectbox("Variable catégorielle", cat_cols)
            
            # Agrégation avant visualisation
            agg_data = df.groupby(cat_col).size().reset_index(name='count')
            agg_data = agg_data.sort_values('count', ascending=False).head(20)
            
            fig, ax = plt.subplots(figsize=(8,4))
            ax.bar(agg_data[cat_col].astype(str), agg_data['count'])
            ax.set_xticklabels(agg_data[cat_col].astype(str), rotation=45, ha='right')
            ax.set_title(f"Répartition par {cat_col}")
            st.pyplot(fig, clear_figure=True)
            plt.close()

    # Option d'export des résultats
    if st.button("Exporter les statistiques"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.describe(include='all').to_excel(writer, sheet_name='Stats')
        st.download_button(
            label="Télécharger",
            data=output.getvalue(),
            file_name="statistiques_analyse.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
