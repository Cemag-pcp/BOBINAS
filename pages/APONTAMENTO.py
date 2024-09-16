import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
# from dotenv import load_env
from google.oauth2 import service_account

from utils import *


# load_dotenv()  # Carrega as variáveis do arquivo .env
# # load_dotenv(override=True)

# credentials_info = {
#     "type": os.environ.get('GOOGLE_TYPE'),
#     "project_id": os.environ.get('GOOGLE_PROJECT_ID'),
#     "private_key_id": os.environ.get('GOOGLE_PRIVATE_KEY_ID'),
#     "private_key": os.environ.get('GOOGLE_PRIVATE_KEY'),
#     "client_email": os.environ.get('GOOGLE_CLIENT_EMAIL'),
#     "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
#     "auth_uri": os.environ.get('GOOGLE_AUTH_URI'),
#     "token_uri": os.environ.get('GOOGLE_TOKEN_URI'),
#     "auth_provider_x509_cert_url": os.environ.get('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
#     "client_x509_cert_url": os.environ.get('GOOGLE_CLIENT_X509_CERT_URL'),
#     "universe_domain": os.environ.get('GOOGLE_UNIVERSE_DOMAIN')
# }

# # Criar as credenciais a partir das informações da conta de serviço
# credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=scope)

# # sa = gspread.service_account(credentials)
# sa = gspread.authorize(credentials)

# sh = sa.open_by_key(sheet_id)

# wks1 = sh.worksheet(worksheet1)

# Função para carregar dados da planilha de planejamento de bobinas, com cache
@st.cache_data(ttl=600)  # Armazena em cache os dados por 10 minutos
def carregar_dados_planejamento():
    
    # Connect to Google Sheets
    client = connect_google_sheet()

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet1 = planilha1.worksheet('PLANEJAMENTO BOBINA')
    dados1 = worksheet1.get_all_values()
    
    df1 = pd.DataFrame(dados1[1:], columns=dados1[0])
    return df1

# Função para carregar dados da planilha de peças pendentes, com cache
@st.cache_data(ttl=600)
def carregar_dados_planejamento_pecas():
    client = connect_google_sheet()

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet1 = planilha1.worksheet('PLANEJAMENTO PEÇA BOBINA')
    dados1 = worksheet1.get_all_values()
    
    df1 = pd.DataFrame(dados1[1:], columns=dados1[0])
    return df1

# Função para carregar dados da planilha de apontamento de chapas, com cache
@st.cache_data(ttl=600)
def carregar_dados_apontamento_chapas():
    client = connect_google_sheet()

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet1 = planilha1.worksheet('APONTAMENTO BOBINA TESTE')
    dados1 = worksheet1.get_all_values()

    df1 = pd.DataFrame(dados1[1:], columns=dados1[0])
    return df1

# Função para carregar dados da planilha de apontamento de peças, com cache
@st.cache_data(ttl=600)
def carregar_dados_apontamento_pecas():
    client = connect_google_sheet()

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet1 = planilha1.worksheet('APONTAMENTO PEÇA BOBINA')
    dados1 = worksheet1.get_all_values()

    df1 = pd.DataFrame(dados1[1:], columns=dados1[0])
    return df1

# Função para atualizar colunas com base no nome das colunas
def update_columns(worksheet, identificador, data_dict):
    headers = worksheet.row_values(1)  # Obter os nomes das colunas
    col_indices = {header: headers.index(header) + 1 for header in headers}  # Mapeia os nomes para os índices

    # Acha o número da próxima linha para adicionar os dados
    num_rows = len(worksheet.col_values(1)) + 1
    
    for col_name, value in data_dict.items():
        worksheet.update_cell(num_rows, col_indices[col_name], value)

# Função para resetar os valores do formulário
def reset_form():
    for key in st.session_state.keys():
        if key.startswith('comp_total') or key.startswith('qtd_chapas') or key.startswith('peca') or key.startswith('qtd_pecas') or key.startswith('comp_retalho') or key.startswith('qtd_retalho'):
            st.session_state[key] = 0

def main():
    st.title("Apontamento de Bobinas, Peças e Retalhos")

    # Mostrar DataFrame de bobinas pendentes da planilha de planejamento
    st.header("Bobinas Pendentes")
    df_planejamento = carregar_dados_planejamento()
    if df_planejamento is not None:
        df_pendentes = df_planejamento[df_planejamento['STATUS'].str.upper() == 'PENDENTE']  # Filtrar apenas bobinas pendentes
        st.write(f"Número de bobinas pendentes: {len(df_pendentes)}")
        st.write(df_pendentes)
    else:
        st.error("Erro ao carregar os dados de bobinas pendentes.")

    # Mostrar DataFrame de peças pendentes
    st.header("Peças Pendentes")
    df_pecas_pendentes = carregar_dados_planejamento_pecas()
    if df_pecas_pendentes is not None:
        df_pecas_pendentes = df_pecas_pendentes[df_pecas_pendentes['STATUS'].str.upper() == 'PENDENTE']  # Filtrar apenas peças pendentes
        st.write(f"Número de peças pendentes: {len(df_pecas_pendentes)}")
        st.write(df_pecas_pendentes)
    else:
        st.error("Erro ao carregar os dados de peças pendentes.")

    # Lista de IDs das bobinas pendentes
    opcoes_codigo = df_pendentes['ID BOBINA'].unique()

    # Seleção única do ID para apontamento
    identificador = st.selectbox('Selecione o ID Bobina', options=opcoes_codigo) if len(opcoes_codigo) > 0 else st.text_input('ID Bobina')

    st.markdown("---")  # Separador visual

    # Escolha do tipo de planejamento
    escolha = st.radio("Selecione o tipo de planejamento:", ('Chapas', 'Peças', 'Chapas e Peças'))

    # Inicializa listas para chapas, peças e retalhos
    comprimentos = []
    quantidades_chapas = []
    pecas = []
    quantidades_pecas = []
    comprimentos_retalhos = []
    quantidades_retalhos = []

    # Se for planejamento de chapas ou ambos
    if escolha == 'Chapas' or escolha == 'Chapas e Peças':
        st.header("Apontamento de Chapas")
        
        # Campo para determinar o número de medidas
        number_chapas = st.number_input('Quantas medidas de chapas foram cortadas?', min_value=1, step=1, key="num_chapas")

        # Gerar campos dinamicamente com base no número de chapas
        for i in range(int(number_chapas)):
            st.write(f"##### Medida {i + 1}")
            comp_total = st.number_input(f'Comprimento - {i + 1}', min_value=0.0, step=0.1, key=f'comp_total_{i}_chapas')
            qtd_chapas = st.number_input(f'Quantidade - {i + 1}', min_value=1, step=1, key=f'qtd_chapas_{i}_chapas')

            comprimentos.append(comp_total)
            quantidades_chapas.append(qtd_chapas)

    # Se for planejamento de peças ou ambos
    if escolha == 'Peças' or escolha == 'Chapas e Peças':
        st.header("Apontamento de Peças")
        number_pecas = st.number_input('Quantas peças foram cortadas?', min_value=1, step=1, key="num_pecas")

        # Gerar campos dinamicamente com base no número de peças
        for i in range(int(number_pecas)):
            st.write(f"##### Peça {i + 1}")
            peca = st.text_input(f'Peça {i + 1}', key=f'peca_{i}_pecas')
            qtd_pecas = st.number_input(f'Qtd peças {i + 1}', min_value=1, step=1, key=f'qtd_pecas_{i}_pecas')

            pecas.append(peca)
            quantidades_pecas.append(qtd_pecas)

    # Apontamento de retalhos (sucata)
    st.header("Apontamento de Retalhos")
    number_retalhos = st.number_input('Quantos retalhos foram gerados?', min_value=1, step=1, key="num_retalhos")

    # Gerar campos dinamicamente com base no número de retalhos
    for i in range(int(number_retalhos)):
        st.write(f"##### Retalho {i + 1}")
        comp_retalho = st.number_input(f'Comprimento do Retalho - {i + 1}', min_value=0.0, step=100.0, key=f'comp_retalho_{i}')
        qtd_retalho = st.number_input(f'Quantidade de Retalhos - {i + 1}', min_value=1.0, step=1.0, key=f'qtd_retalho_{i}')

        comprimentos_retalhos.append(comp_retalho)
        quantidades_retalhos.append(qtd_retalho)

    # Botão fora do formulário para envio dos dados
    submit_button = st.button("Apontar Dados")

    if submit_button:
        client = connect_google_sheet()
        document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
        planilha1 = client.open_by_key(document_id)

        success = True

        # Atualização para chapas
        if escolha == 'Chapas' or escolha == 'Chapas e Peças':
            worksheet_chapas = planilha1.worksheet('APONTAMENTO BOBINA TESTE')
            for i in range(int(number_chapas)):
                comp_total = comprimentos[i]
                qtd_chapa = quantidades_chapas[i]
                if identificador and comp_total and qtd_chapa:
                    update_columns(worksheet_chapas, identificador, {'ID BOBINA': identificador, 'COMPRIMENTO': comp_total, 'QTD CHAPAS': qtd_chapa})
                else:
                    success = False

        # Atualização para peças
        if escolha == 'Peças' or escolha == 'Chapas e Peças':
            worksheet_pecas = planilha1.worksheet('APONTAMENTO PEÇA BOBINA')
            for i in range(int(number_pecas)):
                peca = pecas[i]
                qtd_peca = quantidades_pecas[i]
                if peca and qtd_peca:
                    update_columns(worksheet_pecas, identificador, {'ID BOBINA': identificador, 'PEÇA': peca, 'QUANTIDADE': qtd_peca})
                else:
                    success = False

        # Atualização para retalhos
        worksheet_retalhos = planilha1.worksheet('APONTAMENTO BOBINA TESTE')
        for i in range(int(number_retalhos)):
            comp_retalho = comprimentos_retalhos[i]
            qtd_retalho = quantidades_retalhos[i]
            if comp_retalho and qtd_retalho:
                update_columns(worksheet_retalhos, identificador, {'ID BOBINA': identificador, 'COMP. RETALHO': comp_retalho, 'QTD. RETALHO': qtd_retalho})
            else:
                success = False

        if success:
            st.success('Apontamentos realizados com sucesso!')
            reset_form()  # Limpar os valores inseridos após o envio
        else:
            st.error('Por favor, preencha todos os campos necessários.')

    # Carregar e mostrar DataFrame de apontamentos de chapas
    df_apontamento_chapas = carregar_dados_apontamento_chapas()
    st.header("Apontamentos de Chapas")
    st.write(df_apontamento_chapas)

    # Carregar e mostrar DataFrame de apontamentos de peças
    df_apontamento_pecas = carregar_dados_apontamento_pecas()
    st.header("Apontamentos de Peças")
    st.write(df_apontamento_pecas)



if __name__ == "__main__":
    main()