import pandas as pd
import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIGURAÇÕES ---
load_dotenv()
PASTA_DADOS = os.getenv('PASTA_DADOS')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

SENHA_ENCODED = urllib.parse.quote_plus(DB_PASS)
STRING_CONEXAO = f'postgresql://{DB_USER}:{SENHA_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# LISTA OFICIAL (Apenas o que existe no seu schema.sql)
COLUNAS_NO_BANCO = [
    'id', 'data_inversa', 'dia_semana', 'horario', 'uf', 'br', 'km', 'municipio',
    'causa_acidente', 'tipo_acidente', 'classificacao_acidente', 'fase_dia',
    'sentido_via', 'condicao_metereologica', 'tipo_pista', 'tracado_via',
    'uso_solo', 'pessoas', 'mortos', 'feridos_leves', 'feridos_graves',
    'ilesos', 'ignorados', 'feridos', 'veiculos', 'data_completa', 
    'ano', 'mes', 'flag_carnaval', 'turno'
]

DATAS_CARNAVAL = {
    2015: pd.date_range('2015-02-13', '2015-02-18'),
    2016: pd.date_range('2016-02-05', '2016-02-10'),
    2017: pd.date_range('2017-02-24', '2017-03-01'),
    2018: pd.date_range('2018-02-09', '2018-02-14'),
    2019: pd.date_range('2019-03-01', '2019-03-06'),
    2020: pd.date_range('2020-02-21', '2020-02-26'),
    2021: pd.date_range('2021-02-12', '2021-02-17'),
    2022: pd.date_range('2022-04-20', '2022-04-24'),
    2023: pd.date_range('2023-02-17', '2023-02-22'),
    2024: pd.date_range('2024-02-09', '2024-02-14'),
    2025: pd.date_range('2025-02-28', '2025-03-05')
}

def executar_etl():
    if not PASTA_DADOS or not os.path.exists(PASTA_DADOS):
        print("Erro: Caminho da PASTA_DADOS inválido.")
        return

    engine = create_engine(STRING_CONEXAO)
    print(f"Conectado ao banco {DB_NAME}. Iniciando processamento...")
    
    arquivos = sorted([f for f in os.listdir(PASTA_DADOS) if f.endswith('.csv')])
    
    for arquivo in arquivos:
        print(f"\n--- Processando: {arquivo} ---")
        path = os.path.join(PASTA_DADOS, arquivo)
        
        try:
            df = pd.read_csv(path, sep=';', encoding='latin1', low_memory=False)
        except:
            df = pd.read_csv(path, sep=';', encoding='utf-8', low_memory=False)
            
        df.columns = [c.lower() for c in df.columns]

        # 1. Higienização do KM
        if 'km' in df.columns:
            df['km'] = df['km'].astype(str).str.replace(',', '.')
            df['km'] = pd.to_numeric(df['km'], errors='coerce')

        # 2. Filtro Bahia
        if 'uf' in df.columns:
            df = df[df['uf'].str.upper() == 'BA'].copy()
        
        if df.empty: continue

        # 3. Transformações Temporais (Ajuste de formato para evitar warnings)
        df['data_completa'] = pd.to_datetime(df['data_inversa'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['data_completa']).copy()
        df['ano'] = df['data_completa'].dt.year.astype(int)
        df['mes'] = df['data_completa'].dt.month.astype(int)
        df['flag_carnaval'] = df.apply(lambda r: r['data_completa'] in DATAS_CARNAVAL.get(r['ano'], []), axis=1)
        df['turno'] = df['horario'].apply(lambda x: 'Dia' if '06:00' <= str(x) < '18:00' else 'Noite')

        # --- 4. O FILTRO CRUCIAL ---
        # Mantemos APENAS as colunas que o banco de dados conhece
        # Se uma coluna como 'latitude' estiver no DF, ela será descartada aqui
        df_final = df[df.columns.intersection(COLUNAS_NO_BANCO)].copy()

        # 5. Carga
        try:
            df_final.to_sql('staging_sinistros', engine, if_exists='append', index=False)
            print(f"Sucesso: {len(df_final)} registros de {arquivo} carregados no Postgres.")
        except Exception as e:
            print(f"ERRO ao carregar {arquivo}: {e}")
        
    print("\n>>> Pipeline de ETL finalizado!")

if __name__ == "__main__":
    executar_etl()