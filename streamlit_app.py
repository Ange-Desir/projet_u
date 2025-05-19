import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Analyse des pratiques maraîchères en Côte d’Ivoire")

uploaded_file = st.file_uploader("Téléversez un fichier Excel (Producteurs ou Consommateurs)", type=["xlsx"])

if uploaded_file:
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    sheet = st.selectbox("Sélectionnez la feuille", options=sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    st.write("Aperçu des données")
    st.dataframe(df.head())

    if st.checkbox("Afficher les statistiques descriptives"):
        st.write(df.describe(include="all"))

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        st.subheader("Analyse univariée")
        num_col = st.selectbox("Choisir une variable numérique", numeric_cols)
        sns.histplot(df[num_col], kde=True)
        st.pyplot(plt)

    cat_cols = df.select_dtypes(include='object').columns.tolist()
    if numeric_cols and cat_cols:
        st.subheader("Analyse bivariée")
        cat_col = st.selectbox("Choisir une variable catégorielle", cat_cols)
        num_col_bi = st.selectbox("Choisir une variable numérique", numeric_cols)
        sns.boxplot(x=df[cat_col], y=df[num_col_bi])
        plt.xticks(rotation=90)
        st.pyplot(plt)
