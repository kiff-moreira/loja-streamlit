import streamlit as st
from datetime import datetime, timedelta
from app.config import VALORES_POR_TIPO, MESES
from app.utils import exportar_para_excel
import pandas as pd

def bloco_producao(ordens):
    st.header("📈 Relatório de Produção")
    if ordens.empty:
        st.info("ℹ️ Nenhuma ordem cadastrada para gerar relatórios.")
    else:
        ordens['DATA'] = pd.to_datetime(ordens['DATA'], format='%d/%m/%Y', errors='coerce').dt.date
        ordens = ordens.dropna(subset=['DATA'])
        ordens['VALOR'] = ordens['TIPO DE SERVIÇO'].apply(lambda x: VALORES_POR_TIPO.get(x, 0))
        ordens['MES_ANO'] = pd.to_datetime(ordens['DATA']).dt.strftime('%Y-%m')
        meses_disponiveis = sorted(set(ordens['MES_ANO']))
        if not meses_disponiveis:
            st.error("Nenhuma data válida encontrada nas ordens cadastradas.")
            st.stop()
        with st.form("filtros_producao"):
            col1, col2 = st.columns(2)
            with col1:
                mes_selecionado = st.selectbox("Selecione o mês", meses_disponiveis)
            with col2:
                periodo = st.selectbox("Selecione o período", ['Mês Inteiro', '1ª Quinzena', '2ª Quinzena'])
                tipo_filtro = st.selectbox("Filtrar por tipo de serviço", ["Todos"] + sorted(ordens['TIPO DE SERVIÇO'].unique()))
            st.form_submit_button("Aplicar Filtros")
        try:
            ano, mes = map(int, mes_selecionado.split('-'))
            mes_nome = MESES[mes]
            if not 1 <= mes <= 12:
                st.error("Mês inválido. Deve estar entre 1 e 12.")
                st.stop()
            if periodo == '1ª Quinzena':
                data_inicio = datetime(ano, mes, 1).date()
                data_fim = datetime(ano, mes, 15).date()
            elif periodo == '2ª Quinzena':
                data_inicio = datetime(ano, mes, 16).date()
                if mes == 12:
                    ultimo_dia = 31
                else:
                    ultimo_dia = (datetime(ano, mes + 1, 1) - timedelta(days=1)).day
                data_fim = datetime(ano, mes, ultimo_dia).date()
            else:
                data_inicio = datetime(ano, mes, 1).date()
                if mes == 12:
                    ultimo_dia = 31
                else:
                    ultimo_dia = (datetime(ano, mes + 1, 1) - timedelta(days=1)).day
                data_fim = datetime(ano, mes, ultimo_dia).date()
            ordens_periodo = ordens[(ordens['DATA'] >= data_inicio) & (ordens['DATA'] <= data_fim)]
            if tipo_filtro != "Todos":
                ordens_periodo = ordens_periodo[ordens_periodo['TIPO DE SERVIÇO'] == tipo_filtro]
            st.subheader(f"📅 Relatório: {periodo} de {mes_nome.capitalize()} de {ano}")
            if not ordens_periodo.empty:
                total_valor = ordens_periodo['VALOR'].sum()
                total_ordens = len(ordens_periodo)
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Ordens", total_ordens)
                col2.metric("Valor Total", f"R$ {total_valor:.2f}")
                col3.metric("Média por Ordem", f"R$ {total_valor/total_ordens:.2f}" if total_ordens > 0 else "R$ 0.00")
                st.subheader("🔧 Detalhamento por Tipo de Serviço")
                tipos_servico = ordens_periodo.groupby('TIPO DE SERVIÇO').agg(
                    Quantidade=('TIPO DE SERVIÇO', 'count'),
                    Valor_Total=('VALOR', 'sum')
                ).sort_values('Valor_Total', ascending=False)
                st.dataframe(
                    tipos_servico.reset_index(),
                    column_config={
                        "TIPO DE SERVIÇO": "Tipo de Serviço",
                        "Quantidade": st.column_config.NumberColumn("Qtd"),
                        "Valor_Total": st.column_config.NumberColumn("Valor Total (R$)", format="%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                if st.button("📤 Exportar para Excel"):
                    nome_arquivo = exportar_para_excel(ordens_periodo, periodo=True)
                    st.success("Relatório exportado com sucesso!")
                    st.markdown(f"💾 [Clique para baixar o arquivo Excel](sandbox:/{nome_arquivo})")
            else:
                st.warning(f"Nenhuma ordem encontrada para o período selecionado ({periodo} de {mes_nome.capitalize()} de {ano})")
        except Exception as e:
            st.error(f"⚠️ Ocorreu um erro ao processar o relatório: {str(e)}")
            st.error("Por favor, verifique os dados cadastrados e tente novamente.") 