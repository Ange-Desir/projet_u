import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Streamlit app configuration
st.set_page_config(page_title="Vegetable Farming Analysis", layout="wide")
st.title("Analyse des pratiques de production et consommation de légumes-fruits en Côte d'Ivoire")

# Load cleaned data (replace with your cleaned datasets)
@st.cache_data
def load_data():
    # Placeholder: Load your cleaned producer and consumer datasets
    prod_data = pd.DataFrame({
        'crop': ['Aubergine', 'Tomate', 'Gombo', 'Piment'],
        'percentage': [58.59, 41.80, 39.45, 20.31]
    })
    cons_data = pd.DataFrame({
        'location': ['Marché Local', 'Bord Champ', 'Supermarché'],
        'percentage': [96.51, 9.03, 0.82]
    })
    return prod_data, cons_data

prod_data, cons_data = load_data()

# Sidebar for navigation
st.sidebar.header("Navigation")
analysis_type = st.sidebar.selectbox("Choisir l'analyse", ["Production", "Consommation"])

# Main content
if analysis_type == "Production":
    st.header("Analyse de la Production")
    st.write("Pourcentage des producteurs cultivant chaque légume-fruit")
    fig = px.bar(prod_data, x='crop', y='percentage', color='crop',
                 title="Crops Cultivated by Producers",
                 labels={'percentage': 'Percentage (%)', 'crop': 'Crop'})
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Consommation":
    st.header("Analyse de la Consommation")
    st.write("Lieux d'achat des légumes-fruits par les consommateurs")
    fig = px.bar(cons_data, x='location', y='percentage', color='location',
                 title="Consumer Purchase Locations",
                 labels={'percentage': 'Percentage (%)', 'location': 'Purchase Location'})
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.write("Développé pour le mémoire sur les pratiques de production et consommation de gombo, aubergine, piment, et tomate en Côte d'Ivoire.")
