import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# Configuration initiale
st.set_page_config(layout="wide")
st.title("Analyse des pratiques maraîchères en Côte d'Ivoire")

# Installation silencieuse des dépendances (meilleure pratique: faire dans un environnement séparé)
try:
    import seaborn as sns
    import pandas as pd
    import matplotlib.pyplot as plt
    import openpyxl
except ImportError:
    os.system('pip install seaborn pandas matplotlib openpyxl --quiet')
    import seaborn as sns
    import pandas as pd
    import matplotlib.pyplot as plt
    import openpyxl

# Fonctions de traitement des données
def clean_data(df):
    """Nettoyage de base des données"""
    # Suppression des colonnes vides
    df = df.dropna(how='all', axis=1)
    
    # Suppression des lignes complètement vides
    df = df.dropna(how='all')
    
    # Conversion des types de données
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except ValueError:
                pass
    
    # Nettoyage des chaînes de caractères
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    return df

def handle_missing_values(df, strategy='drop', fill_value=None):
    """Gestion des valeurs manquantes"""
    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill':
        if fill_value is not None:
            df = df.fillna(fill_value)
        else:
            # Remplissage par la moyenne pour les numériques, mode pour les catégorielles
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
    return df

def detect_outliers(df, columns=None, threshold=3):
    """Détection des valeurs aberrantes"""
    if columns is None:
        columns = df.select_dtypes(include='number').columns
    
    outliers = pd.DataFrame()
    
    for col in columns:
        z_scores = (df[col] - df[col].mean()) / df[col].std()
        col_outliers = df[abs(z_scores) > threshold]
        if not col_outliers.empty:
            outliers = pd.concat([outliers, col_outliers])
    
    return outliers

# Interface utilisateur
uploaded_file = st.file_uploader(
    "Téléversez un fichier Excel (Producteurs ou Consommateurs)", 
    type=["xlsx"]
)

if uploaded_file:
    # Lecture du fichier
    try:
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        sheet = st.selectbox(
            "Sélectionnez la feuille", 
            options=sheet_names, 
            key="sheet_select"
        )
        
        df = pd.read_excel(uploaded_file, sheet_name=sheet, engine="openpyxl")
        
        # Section de nettoyage des données
        st.subheader("Nettoyage des données")
        
        # Aperçu avant nettoyage
        st.write("Aperçu avant nettoyage:")
        st.dataframe(df.head())
        
        # Options de nettoyage
        cleaning_options = st.multiselect(
            "Options de nettoyage",
            options=[
                'Supprimer les colonnes vides',
                'Supprimer les lignes vides',
                'Corriger les types de données',
                'Gérer les valeurs manquantes',
                'Supprimer les doublons'
            ],
            default=[
                'Supprimer les colonnes vides',
                'Supprimer les lignes vides'
            ]
        )
        
        # Application des nettoyages sélectionnés
        df_cleaned = df.copy()
        
        if 'Supprimer les colonnes vides' in cleaning_options:
            df_cleaned = df_cleaned.dropna(how='all', axis=1)
        
        if 'Supprimer les lignes vides' in cleaning_options:
            df_cleaned = df_cleaned.dropna(how='all')
        
        if 'Corriger les types de données' in cleaning_options:
            df_cleaned = clean_data(df_cleaned)
        
        if 'Gérer les valeurs manquantes' in cleaning_options:
            strategy = st.radio(
                "Stratégie pour les valeurs manquantes",
                options=['drop', 'fill'],
                index=1,
                horizontal=True
            )
            
            if strategy == 'fill':
                fill_value = st.text_input(
                    "Valeur de remplissage (laisser vide pour auto)",
                    value=""
                )
                if fill_value == "":
                    df_cleaned = handle_missing_values(df_cleaned, strategy='fill')
                else:
                    try:
                        fill_value = float(fill_value) if '.' in fill_value else int(fill_value)
                    except ValueError:
                        pass
                    df_cleaned = handle_missing_values(
                        df_cleaned, 
                        strategy='fill', 
                        fill_value=fill_value
                    )
            else:
                df_cleaned = handle_missing_values(df_cleaned, strategy='drop')
        
        if 'Supprimer les doublons' in cleaning_options:
            df_cleaned = df_cleaned.drop_duplicates()
        
        # Aperçu après nettoyage
        st.write("Aperçu après nettoyage:")
        st.dataframe(df_cleaned.head())
        
        # Téléchargement des données nettoyées
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name='Données nettoyées')
        st.download_button(
            label="Télécharger les données nettoyées",
            data=output.getvalue(),
            file_name="donnees_nettoyees.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Analyse des données
        st.subheader("Analyse des données")
        
        if st.checkbox("Afficher les statistiques descriptives", key="desc_checkbox"):
            st.write("Statistiques descriptives:")
            st.dataframe(df_cleaned.describe(include="all"))
        
        # Analyse univariée
        numeric_cols = df_cleaned.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            st.subheader("Analyse univariée")
            num_col = st.selectbox(
                "Variable numérique pour analyse univariée", 
                numeric_cols, 
                key="univar_select"
            )
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(df_cleaned[num_col], kde=True, ax=ax)
            ax.set_title(f"Distribution de {num_col}")
            st.pyplot(fig)
            
            # Détection des outliers
            outliers = detect_outliers(df_cleaned, [num_col])
            if not outliers.empty:
                st.warning(f"Valeurs aberrantes détectées dans {num_col}")
                st.dataframe(outliers)
        
        # Analyse bivariée
        cat_cols = df_cleaned.select_dtypes(include='object').columns.tolist()
        if numeric_cols and cat_cols:
            st.subheader("Analyse bivariée")
            col1, col2 = st.columns(2)
            
            with col1:
                cat_col = st.selectbox(
                    "Variable catégorielle pour analyse bivariée", 
                    cat_cols, 
                    key="cat_select"
                )
            
            with col2:
                num_col_bi = st.selectbox(
                    "Variable numérique pour analyse bivariée", 
                    numeric_cols, 
                    key="bivar_select"
                )
            
            plot_type = st.radio(
                "Type de visualisation",
                options=['Boxplot', 'Violinplot', 'Barplot'],
                index=0,
                horizontal=True
            )
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if plot_type == 'Boxplot':
                sns.boxplot(x=df_cleaned[cat_col], y=df_cleaned[num_col_bi], ax=ax)
            elif plot_type == 'Violinplot':
                sns.violinplot(x=df_cleaned[cat_col], y=df_cleaned[num_col_bi], ax=ax)
            else:
                sns.barplot(x=df_cleaned[cat_col], y=df_cleaned[num_col_bi], ax=ax)
            
            plt.xticks(rotation=45, ha='right')
            ax.set_title(f"{plot_type} de {num_col_bi} par {cat_col}")
            st.pyplot(fig)
            
            # Analyse de corrélation pour les variables numériques
            if len(numeric_cols) > 1:
                st.subheader("Matrice de corrélation")
                corr_matrix = df_cleaned[numeric_cols].corr()
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
                st.pyplot(fig)
    
    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement du fichier: {str(e)}")
