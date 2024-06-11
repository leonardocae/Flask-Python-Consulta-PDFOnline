# Teste-Sparta
Desafio Teste para Desenvolvedor Python - Sparta Fundos de Investimento


## Projeto

O objetivo deste projeto é desenvolver uma aplicação web simples utilizando Flask e SQLite para listar companhias abertas e visualizar o histórico de uma companhia específica. A aplicação baixa os dados de um arquivo CSV hospedado na internet e os armazena em um banco de dados SQLite local.

Inicialmente, planejei construir este projeto com Django, mas acabei escolhendo Flask por suas características únicas em comparação com Django. Flask é um microframework, o que significa que ele é leve e fácil de usar, especialmente para projetos menores ou para desenvolvedores que preferem ter mais controle sobre as bibliotecas e ferramentas utilizadas. Com Flask, pude adicionar apenas os componentes necessários ao projeto, tornando-o mais modular e fácil de gerenciar. Se precisasse de mais funcionalidades integradas e uma estrutura mais rígida, consideraria usar Django.

# Decisões do Projeto

### Flask
O Flask foi escolhido por ser um microframework leve e fácil de usar, permitindo uma rápida configuração e desenvolvimento de aplicações web.

### SQLite
O SQLite foi escolhido como o banco de dados por ser um banco de dados leve e autossuficiente, sem necessidade de um servidor de banco de dados separado. 

### Requests
A biblioteca `requests` foi utilizada para realizar o download do arquivo CSV da internet.

## Instruções para Rodar a Solução Localmente

### Pré-requisitos
- Python 3.7 ou superior
- Virtualenv (opcional, mas recomendado)

### Passo a Passo

**1 - Clonar o repositório**
```
git clone https://github.com/seuusuario/projetosemframework.git
cd projetosemframework
```
**2 - Criar o ambiente virtual**
```
python -m venv venv
```
**3 - Ativar o ambiente virtual**
```
venv\Scripts\activate
(após, retornar a pasta raiz)
```
**4 - Instalar as dependências**
```
pip install -r requirements.txt
```
**5 - Iniciar a aplicação**
```
python app.py
```

## Estrutura do Projeto
````
projetosemframework/
├── app.py
├── templates/
│ ├── historico.html
│ └── index.html
├── cad_cia_aberta.csv
├── companhias.db
├── venv/
└── requirements.txt
````

## Comentários sobre os Arquivos

- `app.py`: Contém a lógica principal da aplicação, incluindo a criação do banco de dados, importação dos dados e definição das rotas.
- `templates/`: Contém os arquivos HTML usados para renderizar as páginas da web.
- `cad_cia_aberta.csv`: O arquivo CSV com os dados das companhias (baixado automaticamente pelo script).
- `companhias.db`: O banco de dados SQLite onde os dados são armazenados.
- `venv/`: O ambiente virtual.
- `requirements.txt`: Lista das dependências do projeto.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Explicação da lógica app.py

## Importações e Configurações Iniciais
Aqui, importamos as bibliotecas necessárias para o projeto: sqlite3 para interagir com o banco de dados, csv para ler arquivos CSV, os para manipulação de arquivos e diretórios, datetime para manipulação de datas, requests para realizar download de arquivos da internet e flask para criar a aplicação web.

```python
Copiar código
import sqlite3
import csv
import os
from datetime import datetime
import requests
from flask import Flask, render_template

app = Flask(__name__)
```

## Função para Conectar ao Banco de Dados
Esta função cria e retorna uma conexão com o banco de dados SQLite. Ela também imprime uma mensagem de sucesso ao conectar.
```
def conectar_banco():
    db_path = 'companhias.db'
    conn = sqlite3.connect(db_path)
    print(f"Banco de dados {db_path} conectado com sucesso.")
    return conn
```
## Função para Criar a Tabela
Esta função cria a tabela companhias no banco de dados caso ela não exista. A tabela possui várias colunas que armazenam informações detalhadas sobre cada companhia.

```sql
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
```
## Função para Limpar o CNPJ
Esta função remove caracteres especiais do CNPJ para garantir um formato uniforme.
```python
def limpar_cnpj(cnpj):
    return cnpj.replace('.', '').replace('/', '').replace('-', '')
```
## Função para Importar Dados do CSV
Esta função realiza o download do arquivo CSV com os dados das companhias, lê seu conteúdo e insere os dados no banco de dados SQLite. Antes de inserir um novo registro, a função verifica se já existe um registro com o mesmo CNPJ e data de atualização.
```python
def importar_dados_csv():
    conn = conectar_banco()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime('%Y-%m-%d')
    
    url_csv = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
    file_path = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Área de Trabalho', 'projetoSemFramework', 'cad_cia_aberta.csv')
    print(f"Arquivo CSV baixado em: {file_path}")
    
    response = requests.get(url_csv, stream=True)
    with open(file_path, 'wb') as csvfile:
        csvfile.write(response.content)
    
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            cnpj_limpo = limpar_cnpj(row['CNPJ_CIA'])
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
```
# Rotas

## Rota para a Página Inicial
Esta rota renderiza a página inicial, mostrando uma lista de companhias com as informações mais recentes.
```python
@app.route('/')
def index():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cnpj_cia, denom_social, sit FROM companhias
        WHERE data_atualizacao = (SELECT MAX(data_atualizacao) FROM companhias)
        ORDER BY denom_social
    ''')
    companhias = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', companhias=companhias)
```
## Rota para o Histórico de uma Companhia
Esta rota renderiza uma página que mostra o histórico de uma companhia específica baseada no CNPJ fornecido na URL.
```python
@app.route('/historico/<cnpj>')
def historico(cnpj):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM companhias WHERE cnpj_cia = ? ORDER BY data_atualizacao DESC
    ''', (cnpj,))
    historico_companhia = cursor.fetchall()
    
    conn.close()
    
    return render_template('historico.html', historico=historico_companhia)
```
## Inicialização da Aplicação
Estas linhas finais garantem que a tabela seja criada e os dados sejam importados do CSV ao iniciar a aplicação.
```python
if __name__ == '__main__':
    criar_tabela()
    importar_dados_csv()
    app.run(debug=True)
```
# Templates (utilizado bootstrap para estilização)

## Index.html
Exibe a lista de companhias abertas e permite pesquisar por nome, CNPJ, situação ou data.

## Historico.html
Responsável por exibir o histórico de uma companhia específica com base no CNPJ fornecido na URL. 

# Codificação

## encoding = ISO-8859-1
A codificação da tabela consumida no link fornecido foi especificada no código para permitir sua leitura pelo SQLite.
```
...
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
...
```

# Considerações

- Este sistema foi concebido de maneira simplificada, utilizando Flask como backend e SQLite para armazenar os dados. A aplicação permite listar empresas abertas e visualizar o histórico de uma empresa específica. Os dados são obtidos a partir de um arquivo CSV disponibilizado pela CVM.
- A tabela utilizada possui uma estrutura abrangente. Se for necessário adicionar mais colunas de dados, isso pode ser feito facilmente, pois todos os dados estão armazenados no banco de dados companhias.db.
- O sistema utiliza HTML e Bootstrap para a estilização, combinados com Flask para renderização dinâmica das páginas HTML. É possível expandir as funcionalidades adicionando novas rotas e templates conforme necessário.
- A atualização dos dados será feita sempre que eu executar o sistema manualmente, usando a data da atualização para o banco de dados, visto que o arquivo disponibilizado pela CVM é de atualização diária. Caso tivesse algum tipo de pipeline ou servidor em nuvem para realizar essa execução automaticamente o histórico será sempre diário (uma atualização por dia no histórico). Poderiamos utilizar o Apache Airflow e Docker, os quais podem automatizar essa atualização diária de forma autônoma. 
- Nesse projeto desenvolvi um sistema simples e funcional, trazendo uma solução para o desafio proposto.

**Estou à disposição para mais informações!**

