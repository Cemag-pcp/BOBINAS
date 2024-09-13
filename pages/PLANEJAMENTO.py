import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Função para carregar dados da planilha do Google Sheets, com cache
@st.cache_data(ttl=600)  # Armazena em cache por 10 minutos
def carregar_dados_bd():
    cred_path = 'credentials.json'
    if not os.path.exists(cred_path):
        st.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        return None

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet1 = planilha1.worksheet('CADASTRO')
    dados1 = worksheet1.get_all_values()
    
    df1 = pd.DataFrame(dados1[1:], columns=dados1[0])  # Converte para DataFrame do Pandas
    return df1

# Função para carregar dados da planilha de planejamento de chapas, com cache
@st.cache_data(ttl=600)  # Armazena em cache por 10 minutos
def carregar_dados_planejamento_chapas():
    cred_path = 'credentials.json'
    if not os.path.exists(cred_path):
        st.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        return None

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet = planilha1.worksheet('PLANEJAMENTO BOBINA')
    dados = worksheet.get_all_values()
    
    df = pd.DataFrame(dados[1:], columns=dados[0])  # Converte para DataFrame do Pandas
    return df

# Função para carregar dados da planilha de planejamento de peças, com cache
@st.cache_data(ttl=600)  # Armazena em cache por 10 minutos
def carregar_dados_planejamento_pecas():
    cred_path = 'credentials.json'
    if not os.path.exists(cred_path):
        st.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        return None

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    planilha1 = client.open_by_key(document_id)

    worksheet = planilha1.worksheet('PLANEJAMENTO PEÇA BOBINA')
    dados = worksheet.get_all_values()
    
    df = pd.DataFrame(dados[1:], columns=dados[0])  # Converte para DataFrame do Pandas
    return df

# Função para encontrar o índice da coluna pelo nome
def get_column_index(worksheet, column_name):
    header = worksheet.row_values(1)  # Cabeçalho está na primeira linha
    if column_name in header:
        return header.index(column_name) + 1  # Retorna o índice da coluna (1-based)
    else:
        raise ValueError(f"Coluna {column_name} não encontrada.")

# Função para atualizar as colunas no Google Sheets para chapas
def update_columns_chapas(worksheet, identificador, comp_total, qtd_chapas):
    id_col = get_column_index(worksheet, 'ID BOBINA')
    comprimento_col = get_column_index(worksheet, 'COMPRIMENTO')
    qtd_chapas_col = get_column_index(worksheet, 'QTD CHAPAS')
    
    next_row = len(worksheet.get_all_values()) + 1  # Próxima linha disponível
    
    worksheet.update_cell(next_row, id_col, identificador)
    worksheet.update_cell(next_row, comprimento_col, comp_total)
    worksheet.update_cell(next_row, qtd_chapas_col, qtd_chapas)

# Função para atualizar as colunas no Google Sheets para peças
def update_columns_pecas(worksheet, identificador, peca, qtd_pecas):
    id_col = get_column_index(worksheet, 'ID BOBINA')
    peca_col = get_column_index(worksheet, 'PEÇA')
    qtd_pecas_col = get_column_index(worksheet, 'QUANTIDADE')
    
    next_row = len(worksheet.get_all_values()) + 1  # Próxima linha disponível
    
    worksheet.update_cell(next_row, id_col, identificador)
    worksheet.update_cell(next_row, peca_col, peca)
    worksheet.update_cell(next_row, qtd_pecas_col, qtd_pecas)

# Carregar os dados da planilha
df = carregar_dados_bd()

if df is not None:
    # Filtrar apenas bobinas com status "DISPONÍVEL"
    df_disponiveis = df[df['STATUS'].str.strip().str.upper() == 'DISPONÍVEL']

    # Exibir as bobinas disponíveis para planejamento
    st.header("Bobinas disponíveis para planejamento:")
    bobinas_area = st.empty()  # Área reservada para atualizar o DataFrame automaticamente
    bobinas_area.write(df_disponiveis)

    if not df_disponiveis.empty:
        # Escolher entre chapas, peças ou ambos
        tipo_planejamento = st.radio(
            "Selecione o tipo de planejamento:",
            ('Chapas', 'Peças', 'Chapas e Peças')
        )

        # Seleção de ID das bobinas disponíveis
        opcoes_codigo = df_disponiveis['ID BOBINA'].unique()
        identificador = st.selectbox('Selecione o ID Bobina', options=opcoes_codigo)

        # Inicializa listas para chapas e peças
        comprimentos = []
        quantidades_chapas = []
        pecas = []
        quantidades_pecas = []

        # Se for planejamento de chapas ou ambos
        if tipo_planejamento == 'Chapas' or tipo_planejamento == 'Chapas e Peças':
            st.header("Planejamento de chapas")
            number_chapas = st.number_input('Número de medidas a serem cortadas', min_value=1, step=1)

            # Gerar campos dinamicamente com base no número de chapas
            for i in range(int(number_chapas)):
                st.write(f"##### Medida {i + 1}")
                comp_total = st.number_input(f'Comprimento - {i + 1}', min_value=0.0, step=0.1, key=f'comp_total_{i}')
                qtd_chapas = st.number_input(f'Qtd chapas - {i + 1}', min_value=1, step=1, key=f'qtd_chapas_{i}')

                comprimentos.append(comp_total)
                quantidades_chapas.append(qtd_chapas)

        # Se for planejamento de peças ou ambos
        if tipo_planejamento == 'Peças' or tipo_planejamento == 'Chapas e Peças':
            st.header("Planejamento de peças")
            number_pecas = st.number_input('Quantidade de peças a serem cortadas', min_value=1, step=1)

            # Gerar campos dinamicamente com base no número de peças
            for i in range(int(number_pecas)):
                st.write(f"##### Peça {i + 1}")
                peca = st.text_input(f'Peça {i + 1}', key=f'peca_{i}')
                qtd_pecas = st.number_input(f'Qtd peças - {i + 1}', min_value=1, step=1, key=f'qtd_pecas_{i}')

                pecas.append(peca)
                quantidades_pecas.append(qtd_pecas)

        # Botão único para envio fora do formulário
        submit_button = st.button("Atualizar Planilhas")

        if submit_button:
            # Atualizar os dados no Google Sheets
            cred_path = 'credentials.json'
            if not os.path.exists(cred_path):
                st.error(f"Arquivo de credenciais não encontrado: {cred_path}")

            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
            client = gspread.authorize(creds)

            document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'

            # Atualização para chapas
            if tipo_planejamento == 'Chapas' or tipo_planejamento == 'Chapas e Peças':
                worksheet_chapas = client.open_by_key(document_id).worksheet('PLANEJAMENTO BOBINA')
                for i in range(int(number_chapas)):
                    comp_total = comprimentos[i]
                    update_columns_chapas(worksheet_chapas, identificador, comp_total, quantidades_chapas[i])

            # Atualização para peças
            if tipo_planejamento == 'Peças' or tipo_planejamento == 'Chapas e Peças':
                worksheet_pecas = client.open_by_key(document_id).worksheet('PLANEJAMENTO PEÇA BOBINA')
                for i in range(int(number_pecas)):
                    peca = pecas[i]
                    update_columns_pecas(worksheet_pecas, identificador, peca, quantidades_pecas[i])

            # Limpar cache e recarregar DataFrame após a atualização
            st.success('Atualização realizada com sucesso!')
            st.cache_data.clear()  # Limpa o cache após a atualização

    # Recarregar o DataFrame atualizado
    df_atualizado = carregar_dados_bd()
    df_disponiveis_atualizado = df_atualizado[df_atualizado['STATUS'].str.strip().str.upper() == 'DISPONÍVEL']
    
    # Atualizar o DataFrame exibido automaticamente
    bobinas_area.write(df_disponiveis_atualizado)

    # Exibir o DataFrame de planejamento de chapas
    st.header("Planejamento de Chapas:")
    df_chapas = carregar_dados_planejamento_chapas()
    st.write(df_chapas)

    # Exibir o DataFrame de planejamento de peças
    st.header("Planejamento de Peças:")
    df_pecas = carregar_dados_planejamento_pecas()
    st.write(df_pecas)

else:
    st.error("Erro ao carregar os dados.")