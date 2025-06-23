import streamlit as st
import pandas as pd
from app.config import VALORES_POR_TIPO

def bloco_visualizar(ordens):
    st.header("👀 Visualizar Ordens")
    if ordens.empty:
        st.info("ℹ️ Nenhuma ordem cadastrada no sistema.")
    else:
        ordens['DATA'] = pd.to_datetime(ordens['DATA'], format='%d/%m/%Y', errors='coerce').dt.date
        ordens = ordens.dropna(subset=['DATA'])
        ordens['VALOR'] = ordens['TIPO DE SERVIÇO'].apply(lambda x: VALORES_POR_TIPO.get(x, 0))
        with st.expander("🔍 Filtros Avançados", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                ordens['MES_ANO'] = pd.to_datetime(ordens['DATA']).dt.strftime('%Y-%m')
                meses = ["Todos"] + sorted(ordens['MES_ANO'].unique())
                periodo = st.selectbox("Período", meses)
            with col2:
                tipos = ["Todos"] + sorted(ordens['TIPO DE SERVIÇO'].unique())
                tipo_filtro = st.selectbox("Tipo de Serviço", tipos)
        ordens_filtradas = ordens.copy()
        if periodo != "Todos":
            ordens_filtradas = ordens_filtradas[ordens_filtradas['MES_ANO'] == periodo]
        if tipo_filtro != "Todos":
            ordens_filtradas = ordens_filtradas[ordens_filtradas['TIPO DE SERVIÇO'] == tipo_filtro]
        st.dataframe(
            ordens_filtradas.sort_values('DATA', ascending=False),
            column_config={
                "DATA": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "VALOR": st.column_config.NumberColumn("Valor (R$)", format="%.2f")
            },
            use_container_width=True
        )
        st.subheader("📊 Resumo")
        if not ordens_filtradas.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Ordens", len(ordens_filtradas))
            col2.metric("Valor Total", f"R$ {ordens_filtradas['VALOR'].sum():.2f}")
            col3.metric("Período", f"{ordens_filtradas['DATA'].min().strftime('%d/%m/%Y')} a {ordens_filtradas['DATA'].max().strftime('%d/%m/%Y')}") 