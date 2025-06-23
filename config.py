import streamlit as st
import pandas as pd
import os
import csv
import unicodedata
from datetime import datetime, timedelta
from typing import Dict

ARQUIVO_CSV = 'ordens_servico.csv'
ARQUIVO_EXCEL_BASE = 'ordens_servico'

VALORES_POR_TIPO = {
    "troca de conector": 50,
    "instalacao": 100,
    "troca de equipamento": 20,
    "troca de drop": 75,
    "troca de ponto": 50,
    "los": 50,
    "instalacao tabela 2": 150,
    "mesh": 50,
    "instalacao + mesh": 150,
    "instalacao + 2 mesh": 200,
    "instalacao tabela 3": 250,
    "instalacao tabela 2 + mesh": 200
}

MESES: Dict[int, str] = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
} 