import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# O conteúdo deste arquivo será substituído para importar e executar os blocos do app modularizado.
from app.interface import configurar_interface
from app.data import carregar_dados
from app.adicionar import bloco_adicionar
from app.visualizar import bloco_visualizar
from app.excluir import bloco_excluir
from app.producao import bloco_producao  # type: ignore

# Configuração da interface e menu
aba = configurar_interface()

# Carregamento dos dados
ordens = carregar_dados()

# Execução dos blocos conforme a aba selecionada
if aba == "Adicionar":
    bloco_adicionar(ordens)
elif aba == "Visualizar":
    bloco_visualizar(ordens)
elif aba == "Excluir":
    bloco_excluir(ordens)
elif aba == "Produção":
    bloco_producao(ordens)