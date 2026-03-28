-- ===============================================================
-- CRIAÇÃO DO ESQUEMA ESTRELA (STAR SCHEMA) - DW SINISTROS BAHIA
-- ===============================================================

-- 1. Dimensão Tempo: Granularidade por data e horário
CREATE TABLE dm_tempo (
    sk_tempo SERIAL PRIMARY KEY,
    data_completa DATE NOT NULL,
    ano INT NOT NULL,
    mes INT NOT NULL,
    dia_semana VARCHAR(20),
    horario TIME,
    turno VARCHAR(20),
    flag_carnaval BOOLEAN DEFAULT FALSE
);

-- 2. Dimensão Local: Atributos geográficos da rodovia
CREATE TABLE dm_local (
    sk_local SERIAL PRIMARY KEY,
    uf VARCHAR(2),
    br INT,
    km VARCHAR(10),
    municipio VARCHAR(100),
    regional VARCHAR(100),
    delegacia VARCHAR(100),
    uop VARCHAR(100),
    latitude VARCHAR(20),
    longitude VARCHAR(20)
);

-- 3. Dimensão Condições: Fatores ambientais e da via
CREATE TABLE dm_condicoes (
    sk_condicoes SERIAL PRIMARY KEY,
    fase_dia VARCHAR(255),
    condicao_tempo VARCHAR(255),
    tipo_pista VARCHAR(255),
    tracado_via VARCHAR(255),
    uso_solo VARCHAR(255),
    sentido_via VARCHAR(255)
);

-- 4. Dimensão Causa: Classificação e motivação do sinistro
CREATE TABLE dm_causa (
    sk_causa SERIAL PRIMARY KEY,
    causa_base VARCHAR(255),
    tipo_acidente VARCHAR(255),
    classificacao VARCHAR(255)
);

-- 5. Tabela Fato: Centralização das métricas
CREATE TABLE ft_sinistros (
    sk_sinistro SERIAL PRIMARY KEY,
    sk_tempo INT REFERENCES dm_tempo(sk_tempo),
    sk_local INT REFERENCES dm_local(sk_local),
    sk_condicoes INT REFERENCES dm_condicoes(sk_condicoes),
    sk_causa INT REFERENCES dm_causa(sk_causa),
    id_original BIGINT,
    qtd_pessoas INT DEFAULT 0,
    qtd_mortos INT DEFAULT 0,
    qtd_feridos INT DEFAULT 0,
    qtd_veiculos INT DEFAULT 0,
    qtd_ilesos INT DEFAULT 0
);