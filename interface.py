import streamlit as st

def configurar_interface():
    st.set_page_config(page_title="Gerenciador de Ordens", layout="wide")
    st.title("📋 Gerenciador de Ordens de Serviço")
    aba = st.sidebar.selectbox("Menu", ["Adicionar", "Visualizar", "Excluir", "Produção"])
    return aba 