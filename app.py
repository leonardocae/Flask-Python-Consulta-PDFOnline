import sqlite3
import csv
import os
from datetime import datetime
import requests
from flask import Flask, render_template

app = Flask(__name__)

# Conexão com o banco de dados
def conectar_banco():
    db_path = 'companhias.db'
    conn = sqlite3.connect(db_path)
    print(f"Banco de dados {db_path} conectado com sucesso.")
    return conn

# Criar tabela no banco de dados
def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companhias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj_cia VARCHAR(20),
            denom_social VARCHAR(100),
            denom_comerc VARCHAR(100),
            dt_reg DATE,
            dt_const DATE,
            dt_cancel DATE,
            motivo_cancel VARCHAR(80),
            sit VARCHAR(40),
            dt_ini_sit DATE,
            cd_cvm NUMERIC(7, 0),
            setor_ativ VARCHAR(100),
            tp_merc VARCHAR(50),
            categ_reg VARCHAR(20),
            dt_ini_categ DATE,
            sit_emissor CHAR(80),
            dt_ini_sit_emissor DATE,
            controle_acionario VARCHAR(30),
            tp_ender CHAR(30),
            logradouro VARCHAR(100),
            compl VARCHAR(100),
            bairro VARCHAR(100),
            mun VARCHAR(100),
            uf CHAR(2),
            pais VARCHAR(100),
            cep NUMERIC(8, 0),
            ddd_tel VARCHAR(4),
            tel NUMERIC(15, 0),
            ddd_fax VARCHAR(4),
            fax NUMERIC(15, 0),
            email VARCHAR(100),
            tp_resp VARCHAR(100),
            resp VARCHAR(100),
            dt_ini_resp DATE,
            logradouro_resp VARCHAR(100),
            compl_resp VARCHAR(100),
            bairro_resp VARCHAR(100),
            mun_resp VARCHAR(100),
            uf_resp CHAR(2),
            pais_resp VARCHAR(100),
            cep_resp NUMERIC(8, 0),
            ddd_tel_resp VARCHAR(4),
            tel_resp NUMERIC(15, 0),
            ddd_fax_resp VARCHAR(4),
            fax_resp NUMERIC(15, 0),
            email_resp VARCHAR(100),
            cnpj_auditor VARCHAR(20),
            auditor VARCHAR(100),
            data_atualizacao DATE,
            UNIQUE (cnpj_cia, data_atualizacao)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabela 'companhias' criada com sucesso.")

# Remover caracteres especiais do CNPJ
def limpar_cnpj(cnpj):
    return cnpj.replace('.', '').replace('/', '').replace('-', '')

# Importar dados do CSV para o banco de dados
def importar_dados_csv():
    conn = conectar_banco()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime('%Y-%m-%d')
    
    # URL do Csv
    url_csv = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
    
    # Salvar o arquivo CSV localmente
    file_path = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Área de Trabalho', 'projetoSemFramework', 'cad_cia_aberta.csv')
    print(f"Arquivo CSV baixado em: {file_path}")
    
    # Download csv usando requests
    response = requests.get(url_csv, stream=True)
    with open(file_path, 'wb') as csvfile:
        csvfile.write(response.content)
    
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            cnpj_limpo = limpar_cnpj(row['CNPJ_CIA'])
            # Verificar se já existe um registro para o CNPJ e a data atual
            cursor.execute('''
                SELECT COUNT(*) FROM companhias WHERE cnpj_cia = ? AND data_atualizacao = ?
            ''', (cnpj_limpo, data_atual))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO companhias (
                        cnpj_cia, denom_social, denom_comerc, dt_reg, dt_const, dt_cancel, motivo_cancel, sit, 
                        dt_ini_sit, cd_cvm, setor_ativ, tp_merc, categ_reg, dt_ini_categ, sit_emissor, 
                        dt_ini_sit_emissor, controle_acionario, tp_ender, logradouro, compl, bairro, mun, uf, pais, 
                        cep, ddd_tel, tel, ddd_fax, fax, email, tp_resp, resp, dt_ini_resp, logradouro_resp, 
                        compl_resp, bairro_resp, mun_resp, uf_resp, pais_resp, cep_resp, ddd_tel_resp, tel_resp, 
                        ddd_fax_resp, fax_resp, email_resp, cnpj_auditor, auditor, data_atualizacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cnpj_limpo, row['DENOM_SOCIAL'], row['DENOM_COMERC'], row['DT_REG'], row['DT_CONST'], 
                    row['DT_CANCEL'], row['MOTIVO_CANCEL'], row['SIT'], row['DT_INI_SIT'], row['CD_CVM'], 
                    row['SETOR_ATIV'], row['TP_MERC'], row['CATEG_REG'], row['DT_INI_CATEG'], row['SIT_EMISSOR'], 
                    row['DT_INI_SIT_EMISSOR'], row['CONTROLE_ACIONARIO'], row['TP_ENDER'], row['LOGRADOURO'], 
                    row['COMPL'], row['BAIRRO'], row['MUN'], row['UF'], row['PAIS'], row['CEP'], row['DDD_TEL'], 
                    row['TEL'], row['DDD_FAX'], row['FAX'], row['EMAIL'], row['TP_RESP'], row['RESP'], 
                    row['DT_INI_RESP'], row['LOGRADOURO_RESP'], row['COMPL_RESP'], row['BAIRRO_RESP'], row['MUN_RESP'], 
                    row['UF_RESP'], row['PAIS_RESP'], row['CEP_RESP'], row['DDD_TEL_RESP'], row['TEL_RESP'], 
                    row['DDD_FAX_RESP'], row['FAX_RESP'], row['EMAIL_RESP'], row['CNPJ_AUDITOR'], row['AUDITOR'], 
                    data_atual
                ))
    conn.commit()
    conn.close()

# Página inicial
@app.route('/')
def index():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Companhias mais recentes
    cursor.execute('''
        SELECT cnpj_cia, denom_social, sit FROM companhias
        WHERE data_atualizacao = (SELECT MAX(data_atualizacao) FROM companhias)
        ORDER BY denom_social
    ''')
    companhias = cursor.fetchall()
    
    # Data da última atualização
    cursor.execute('''
        SELECT MAX(data_atualizacao) FROM companhias
    ''')
    ultima_atualizacao = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', companhias=companhias, ultima_atualizacao=ultima_atualizacao)

# Página de histórico de uma companhia específica
@app.route('/historico/<cnpj>')
def historico(cnpj):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Histórico da companhia específica
    cursor.execute('''
        SELECT cnpj_cia, denom_social, sit, data_atualizacao FROM companhias
        WHERE cnpj_cia = ? ORDER BY data_atualizacao DESC
    ''', (cnpj,))
    historico = cursor.fetchall()
    
    conn.close()
    
    return render_template('historico.html', cnpj=cnpj, historico=historico)

if __name__ == '__main__':
    criar_tabela()
    importar_dados_csv()
    app.run(debug=True)

