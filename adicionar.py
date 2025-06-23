import streamlit as st
from app.utils import formatar_data, normalizar_texto, salvar_ordens
from app.config import VALORES_POR_TIPO
import pandas as pd

def bloco_adicionar(ordens):
    st.header("➕ Adicionar Nova Ordem")
    with st.form("form_adicionar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id = st.text_input("ID do Cliente*", help="Identificação única do cliente")
            data = st.text_input("Data (Dia e Mes)*")
        with col2:
            nome = st.text_input("Nome do Cliente*", help="Nome completo do cliente")
            tipo = st.selectbox("Tipo de Serviço*", options=[" "] + list(VALORES_POR_TIPO.keys()))
        submitted = st.form_submit_button("Salvar Ordem")
        if submitted:
            data_formatada = formatar_data(data)
            tipo_normalizado = normalizar_texto(tipo) if tipo != "None" else None
            if not all([id, nome, data_formatada]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)!")
            elif tipo == "None":
                st.error("Por favor, selecione um tipo de serviço válido!")
            elif tipo_normalizado not in VALORES_POR_TIPO:
                st.error("Tipo de serviço inválido!")
            elif not ordens[(ordens['ID'] == id) & (ordens['NOME'] == nome) & (ordens['DATA'] == data_formatada) & (ordens['TIPO DE SERVIÇO'] == tipo_normalizado)].empty:
                st.warning("⚠️ Esta ordem já foi cadastrada anteriormente!")
            else:
                nova_ordem = pd.DataFrame([[id, nome, data_formatada, tipo_normalizado]], columns=ordens.columns)
                ordens = pd.concat([ordens, nova_ordem], ignore_index=True)
                salvar_ordens(ordens)
                st.success("✅ Ordem cadastrada com sucesso!") 