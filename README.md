# Data Warehouse e ETL em Python para Análise de Sinistros Rodoviários na Bahia

Este repositório contém o código-fonte e a documentação técnica do projeto de conclusão de curso (TCC) em Engenharia de Software (USP/Esalq).

## 🚀 Sobre o Projeto
O sistema consiste numa arquitetura de dados *end-to-end* para extração, tratamento e visualização de acidentes nas rodovias federais da Bahia (2015-2025), utilizando dados abertos da PRF.

### 🛠 Tech Stack
* **Linguagem:** Python 3.12
* **Banco de Dados:** PostgreSQL (Modelo Star Schema)
* **Bibliotecas:** Pandas, SQLAlchemy, Plotly Dash
* **Ambiente:** VS Code / Jupyter Notebooks

## 📁 Estrutura do Repositório
* `database/`: Scripts de criação das tabelas dimensionais e fato.
* `src/etl_process.py`: Pipeline de extração e higienização de dados.
* `src/app_dashboard.py`: Aplicação web interativa para visualização dos dados.

## 📊 Base de Dados
Para executar este projeto, é necessário baixar os microdados de acidentes (2015-2025) diretamente do portal de Dados Abertos da PRF:
* [Link para Dados Abertos PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)

Após o download, extraia os arquivos na pasta configurada na variável `PASTA_DADOS` do seu ficheiro `.env`.

## ⚙️ Como Executar
1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv venv`.
3. Instale as dependências: `pip install -r requirements.txt`.
4. Configure as suas credenciais no ficheiro `.env` (veja `.env.example`).
5. Execute o script de banco de dados no PostgreSQL.
6. Rode o ETL: `python src/etl_process.py`.
7. Inicie o Dashboard: `python src/app_dashboard.py`.

## 📊 Visualização
O dashboard permite filtrar e analisar o impacto de feriados como o Carnaval e identificar as rodovias de maior letalidade no estado.

---
**Autora:** Juliana Silva Soares  
**Orientação:** Flávio Manoel Leal  
*Pós-graduação em Engenharia de Software - USP/Esalq*
