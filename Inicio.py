import streamlit as st
from utils.layout import firma_sidebar

# Firma en la barra lateral
firma_sidebar()

st.title("Simulador de Deuda")

st.write("Bienvenido/a 👋")

st.write(
    """
    Esta aplicación te permitirá:

    - Entender los conceptos clave de una deuda
    - Generar tablas de amortización (Francesa y Alemana)
    - Comparar escenarios
    - Calcular la tasa de interés a partir de la cuota
    - Conectar tus resultados a un dashboard en Tableau
    """
)

st.info("Usa el menú lateral para navegar por las secciones")
