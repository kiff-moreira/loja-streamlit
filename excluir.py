import streamlit as st
from datetime import datetime, timedelta
from app.utils import salvar_ordens
import pandas as pd

def bloco_excluir(ordens):
    st.header("❌ Excluir Ordem")
    st.warning("Esta ação é irreversível. Tenha certeza antes de excluir.")
    metodo = st.radio("Como deseja localizar a ordem?", ["Por ID exato", "Por filtros"], horizontal=True)
    if metodo == "Por ID exato":
        id_excluir = st.text_input("Digite o ID exato da ordem a ser excluída")
        if id_excluir:
            ordens_filtradas = ordens[ordens['ID'] == id_excluir]
    else:
        with st.expander("Filtros de busca"):
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data inicial", datetime.now() - timedelta(days=30))
                nome_cliente = st.text_input("Nome do cliente")
            with col2:
                data_fim = st.date_input("Data final", datetime.now())
                tipo_servico = st.selectbox("Tipo de serviço", ["Todos"] + sorted(ordens['TIPO DE SERVIÇO'].unique()))
        ordens_filtradas = ordens.copy()
        ordens_filtradas['DATA'] = pd.to_datetime(ordens_filtradas['DATA'], format='%d/%m/%Y', errors='coerce').dt.date
        ordens_filtradas = ordens_filtradas[(ordens_filtradas['DATA'] >= data_inicio) & (ordens_filtradas['DATA'] <= data_fim)]
        if nome_cliente:
            ordens_filtradas = ordens_filtradas[ordens_filtradas['NOME'].str.contains(nome_cliente, case=False)]
        if tipo_servico != "Todos":
            ordens_filtradas = ordens_filtradas[ordens_filtradas['TIPO DE SERVIÇO'] == tipo_servico]
    if 'ordens_filtradas' in locals() and not ordens_filtradas.empty:
        st.dataframe(ordens_filtradas, use_container_width=True)
        if len(ordens_filtradas) == 1:
            ordem_excluir = ordens_filtradas.iloc[0]
            st.warning(f"Ordem selecionada para exclusão: ID {ordem_excluir['ID']} - {ordem_excluir['NOME']}")
        else:
            ids = ordens_filtradas['ID'].tolist()
            id_excluir = st.selectbox("Selecione o ID para excluir", ids)
            ordem_excluir = ordens_filtradas[ordens_filtradas['ID'] == id_excluir].iloc[0]
            st.warning(f"Ordem selecionada para exclusão: ID {ordem_excluir['ID']} - {ordem_excluir['NOME']}")
        if st.button("Confirmar Exclusão", type="primary"):
            ordens = ordens[ordens['ID'] != ordem_excluir['ID']]
            salvar_ordens(ordens)
            st.success(f"Ordem ID {ordem_excluir['ID']} excluída com sucesso!")
    elif 'ordens_filtradas' in locals():
        st.info("Nenhuma ordem encontrada com os filtros aplicados.") 