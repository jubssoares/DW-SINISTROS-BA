import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

def carregar_star_schema():
    load_dotenv()
    
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    sql_statements = [
        # 1. Dimensão Tempo
        """
        INSERT INTO dm_tempo (data_completa, ano, mes, dia_semana, horario, turno, flag_carnaval)
        SELECT DISTINCT data_completa, ano, mes, dia_semana, CAST(horario AS TIME), turno, flag_carnaval
        FROM staging_sinistros
        ON CONFLICT DO NOTHING;
        """,
        # 2. Dimensão Local (Convertendo KM para TEXT para garantir o DISTINCT correto)
        """
        INSERT INTO dm_local (uf, br, km, municipio)
        SELECT DISTINCT uf, CAST(br AS INT), CAST(km AS TEXT), municipio
        FROM staging_sinistros
        ON CONFLICT DO NOTHING;
        """,
        # 3. Dimensão Condições
        """
        INSERT INTO dm_condicoes (fase_dia, condicao_tempo, tipo_pista, tracado_via, uso_solo, sentido_via)
        SELECT DISTINCT fase_dia, condicao_metereologica, tipo_pista, tracado_via, uso_solo, sentido_via
        FROM staging_sinistros
        ON CONFLICT DO NOTHING;
        """,
        # 4. Dimensão Causa
        """
        INSERT INTO dm_causa (causa_base, tipo_acidente, classificacao)
        SELECT DISTINCT causa_acidente, tipo_acidente, classificacao_acidente
        FROM staging_sinistros
        ON CONFLICT DO NOTHING;
        """,
        # 5. Tabela Fato (Ajustada com CAST para evitar erro de tipos)
        """
        INSERT INTO ft_sinistros (sk_tempo, sk_local, sk_condicoes, sk_causa, id_original, qtd_pessoas, qtd_mortos, qtd_feridos, qtd_veiculos, qtd_ilesos)
        SELECT 
            t.sk_tempo, l.sk_local, cond.sk_condicoes, c.sk_causa,
            s.id, s.pessoas, s.mortos, s.feridos, s.veiculos, s.ilesos
        FROM staging_sinistros s
        JOIN dm_tempo t ON s.data_completa = t.data_completa 
             AND CAST(s.horario AS TIME) = t.horario
        JOIN dm_local l ON CAST(s.br AS INT) = l.br 
             AND CAST(s.km AS TEXT) = l.km 
             AND s.municipio = l.municipio
        JOIN dm_condicoes cond ON s.fase_dia = cond.fase_dia 
             AND s.condicao_metereologica = cond.condicao_tempo 
             AND s.tipo_pista = cond.tipo_pista 
             AND s.tracado_via = cond.tracado_via
        JOIN dm_causa c ON s.causa_acidente = c.causa_base 
             AND s.tipo_acidente = c.tipo_acidente 
             AND s.classificacao_acidente = c.classificacao;
        """
    ]

    try:
        with engine.connect() as conn:
            print("Iniciando carga do Star Schema...")
            for i, query in enumerate(sql_statements, 1):
                conn.execute(text(query))
                print(f"Etapa {i} finalizada.")
            conn.commit()
            print("\n>>> SUCESSO ABSOLUTO: O seu Data Warehouse está pronto!")
    except Exception as e:
        print(f"\n>>> ERRO NA CARGA: {e}")

if __name__ == "__main__":
    carregar_star_schema()