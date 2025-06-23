from app.config import ARQUIVO_CSV, ARQUIVO_EXCEL_BASE, VALORES_POR_TIPO, MESES
import pandas as pd
import os
import csv
import unicodedata
from datetime import datetime
import streamlit as st
from typing import Optional, Any
import gspread
from google.oauth2.service_account import Credentials

def normalizar_texto(texto: str) -> str:
    """Remove acentos e converte para minúsculas"""
    return ''.join(
        letra for letra in unicodedata.normalize('NFD', texto)
        if unicodedata.category(letra) != 'Mn'
    ).lower()

def carregar_ordens() -> pd.DataFrame:
    """Carrega as ordens do arquivo CSV ou cria um novo se não existir"""
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "NOME", "DATA", "TIPO DE SERVIÇO"])
        return pd.DataFrame(columns=["ID", "NOME", "DATA", "TIPO DE SERVIÇO"])
    try:
        return pd.read_csv(ARQUIVO_CSV, encoding='utf-8')
    except UnicodeDecodeError:  # noqa: E722
        # Caso o arquivo não esteja em utf-8, tenta latin1
        return pd.read_csv(ARQUIVO_CSV, encoding='latin1')

def salvar_ordens(df: pd.DataFrame) -> None:
    """Salva as ordens no CSV"""
    df.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8')

def formatar_data(data: str) -> Optional[str]:
    """Converte a data para o formato DD/MM/AAAA"""
    try:
        return datetime.strptime(data, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError:
        try:
            return datetime.strptime(data, '%d/%m').strftime('%d/%m') + f'/{datetime.now().year}'
        except ValueError:
            return None

def exportar_para_excel(df: pd.DataFrame, periodo: bool = False) -> Optional[str]:
    """Exporta os dados para um arquivo Excel organizado"""
    if df.empty:
        st.warning("Nenhum dado para exportar.")
        return None
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce').dt.date
    df = df.dropna(subset=['DATA'])
    if df.empty:
        st.warning("Nenhuma data válida para exportar.")
        return None
    if periodo:
        data_min = pd.to_datetime(df['DATA'].min())
        data_inicio = data_min.strftime('%d')
        data_fim = pd.to_datetime(df['DATA'].max()).strftime('%d')
        mes = MESES[data_min.month]
        nome_arquivo = f"{ARQUIVO_EXCEL_BASE}_{data_inicio}-{data_fim}_{mes}.xlsx"
    else:
        nome_arquivo = f"{ARQUIVO_EXCEL_BASE}.xlsx"
    with pd.ExcelWriter(nome_arquivo) as writer:
        df.to_excel(writer, sheet_name="Todas as Ordens", index=False)
        for tipo, grupo in df.groupby('TIPO DE SERVIÇO'):
            nome_aba = tipo[:31]
            grupo.to_excel(writer, sheet_name=nome_aba, index=False)
        df['VALOR'] = df['TIPO DE SERVIÇO'].apply(lambda x: VALORES_POR_TIPO.get(x, 0))
        resumo = pd.DataFrame({
            "Total de Ordens": [len(df)],
            "Valor Total": [df['VALOR'].sum()],
            "Primeira Data": [df['DATA'].min().strftime('%d/%m/%Y')],
            "Última Data": [df['DATA'].max().strftime('%d/%m/%Y')]
        })
        resumo.to_excel(writer, sheet_name="Resumo", index=False)
    return nome_arquivo

# Instruções:
# 1. Crie um projeto no Google Cloud e ative a API Google Sheets e Google Drive.
# 2. Gere um arquivo de credenciais (service_account.json) e coloque na raiz do projeto.
# 3. Compartilhe a planilha Google com o email do service account.
# 4. Instale as dependências: pip install gspread google-auth

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CREDS_FILE = 'service_account.json'

def get_gspread_client():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def exportar_para_google_sheets(df: pd.DataFrame, nome_planilha: str, nome_aba: str = 'Sheet1') -> None:
    """Exporta um DataFrame para uma planilha Google Sheets."""
    gc = get_gspread_client()
    try:
        sh = gc.open(nome_planilha)
    except gspread.SpreadsheetNotFound:
        sh = gc.create(nome_planilha)
    try:
        worksheet = sh.worksheet(nome_aba)
        sh.del_worksheet(worksheet)
    except gspread.WorksheetNotFound:
        pass
    worksheet = sh.add_worksheet(title=nome_aba, rows=str(len(df)+10), cols=str(len(df.columns)+5))
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

def ler_de_google_sheets(nome_planilha: str, nome_aba: str = 'Sheet1') -> pd.DataFrame:
    """Lê uma aba de uma planilha Google Sheets e retorna como DataFrame."""
    gc = get_gspread_client()
    sh = gc.open(nome_planilha)
    worksheet = sh.worksheet(nome_aba)
    data = worksheet.get_all_records()
    return pd.DataFrame(data) 