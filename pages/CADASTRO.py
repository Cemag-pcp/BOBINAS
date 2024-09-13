import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Função para carregar dados da planilha
def carregar_dados_bd():
    cred_path = 'credentials.json'
    if not os.path.exists(cred_path):
        st.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        return None

    # Configurações de autenticação e escopo
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao autenticar com Google Sheets: {e}")
        return None

    # Substitua pelo ID correto da sua planilha
    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    try:
        planilha1 = client.open_by_key(document_id)
    except gspread.SpreadsheetNotFound:
        st.error("Planilha não encontrada. Verifique o ID.")
        return None

    try:
        worksheet1 = planilha1.worksheet('CADASTRO')
        dados1 = worksheet1.get_all_values()
        df1 = pd.DataFrame(dados1[1:], columns=dados1[0])
        return df1
    except Exception as e:
        st.error(f"Erro ao carregar os dados da planilha: {e}")
        return None

# Função para salvar dados no Google Sheets
def save_data_google_sheets(data, colunas_para_atualizar):
    cred_path = 'credentials.json'
    if not os.path.exists(cred_path):
        st.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        return
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao autenticar com Google Sheets: {e}")
        return

    document_id = '16atY486fScsRTrLsh9OGUjYsYwiIkX4IRovD19wKdVk'
    try:
        planilha1 = client.open_by_key(document_id)
        worksheet1 = planilha1.worksheet('CADASTRO')

        # Obtendo cabeçalhos da planilha (primeira linha)
        cabecalho = worksheet1.row_values(1)

        # Verificando se as colunas existem
        indices_colunas = [cabecalho.index(coluna) + 1 for coluna in colunas_para_atualizar if coluna in cabecalho]

        # Garantindo que todas as colunas foram encontradas
        if len(indices_colunas) != len(colunas_para_atualizar):
            st.error("Nem todas as colunas foram encontradas na planilha.")
            return

        # Encontrando a próxima linha em branco
        proxima_linha = len(worksheet1.get_all_values()) + 1

        # Atualizando apenas as colunas informadas
        for indice, valor in zip(indices_colunas, data):
            worksheet1.update_cell(proxima_linha, indice, valor)
        
        st.success('Dados salvos com sucesso!')
    except gspread.SpreadsheetNotFound:
        st.error("Planilha não encontrada. Verifique o ID.")
    except Exception as e:
        st.error(f"Erro ao salvar os dados na planilha: {e}")

# Função principal do aplicativo
def main():
    st.title("Sistema de Cadastro de Bobinas")

    st.header("Cadastrar Nova Bobina")
    form = st.form(key='Bobinas', clear_on_submit=True)
    with form:
        identificador = st.text_input('ID BOBINA')

        largura = st.number_input('Largura', min_value=0.0, step=0.1)
        espessura = st.number_input('Espessura', min_value=0.0, step=0.1)
        peso_real = st.number_input('Peso Real', min_value=0.0, step=0.1)
        peso_nota_fiscal = st.number_input('Peso Nota Fiscal', min_value=0.0, step=0.1)
        submit_button = st.form_submit_button(label='Cadastrar')

    if submit_button:
        if largura and espessura and peso_real:
            data = [identificador, largura, espessura, peso_real, peso_nota_fiscal]
            colunas_para_atualizar = ['ID BOBINA', 'LARGURA', 'ESPESSURA', 'PESO REAL', 'PESO NOTA FISCAL']  # Colunas que você deseja atualizar
            save_data_google_sheets(data, colunas_para_atualizar)
        else:
            st.error('Por favor, preencha todos os campos.')

    st.header("Dados Existentes")
    df = carregar_dados_bd()
    if df is not None:
        st.dataframe(df)
    else:
        st.error("Erro ao carregar os dados.")

if __name__ == "__main__":
    main()