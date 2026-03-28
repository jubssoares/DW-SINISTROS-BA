import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

def limpar_tabela():
    load_dotenv()
    
    # Monta a conexão exatamente como no seu ETL
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    try:
        with engine.connect() as conn:
            conn.execute(text('TRUNCATE TABLE staging_sinistros;'))
            conn.commit()
            print(">>> Sucesso: Tabela 'staging_sinistros' limpa e pronta para o novo ETL!")
    except Exception as e:
        print(f">>> Erro ao limpar a tabela: {e}")

if __name__ == "__main__":
    limpar_tabela()