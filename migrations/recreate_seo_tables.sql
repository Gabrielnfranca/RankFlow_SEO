-- Backup dos dados existentes
CREATE TEMP TABLE IF NOT EXISTS temp_seo_tecnico_status AS
SELECT * FROM seo_tecnico_status;

CREATE TABLE IF NOT EXISTS seo_tecnico_categoria_backup AS 
SELECT * FROM seo_tecnico_categoria;

CREATE TABLE IF NOT EXISTS seo_tecnico_item_backup AS 
SELECT * FROM seo_tecnico_item;

-- Drop das tabelas na ordem correta
DROP TABLE IF EXISTS seo_tecnico_status;
DROP TABLE IF EXISTS seo_tecnico_item;
DROP TABLE IF EXISTS seo_tecnico_categoria;

-- Recriar as tabelas com a estrutura correta
CREATE TABLE seo_tecnico_categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    ordem INTEGER NOT NULL
);

CREATE TABLE seo_tecnico_item (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES seo_tecnico_categoria(id),
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    documentacao_url VARCHAR(255),
    ordem INTEGER NOT NULL
);

CREATE TABLE seo_tecnico_status (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES cliente(id),
    item_id INTEGER REFERENCES seo_tecnico_item(id),
    status VARCHAR(20) DEFAULT 'pendente',
    prioridade VARCHAR(20) DEFAULT 'media',
    observacoes TEXT,
    data_verificacao TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restaurar os dados das categorias
INSERT INTO seo_tecnico_categoria (id, nome, descricao, ordem)
SELECT id, nome, descricao, COALESCE(ordem, 0)
FROM seo_tecnico_categoria_backup;

INSERT INTO seo_tecnico_item (id, categoria_id, nome, descricao, documentacao_url, ordem)
SELECT id, categoria_id, nome, descricao, documentacao_url, COALESCE(ordem, 0)
FROM seo_tecnico_item_backup;

-- Restaurar os dados dos status
INSERT INTO seo_tecnico_status (id, cliente_id, item_id, status, prioridade, observacoes, data_verificacao, data_atualizacao)
SELECT id, cliente_id, item_id, status, prioridade, observacoes, data_verificacao, data_atualizacao
FROM temp_seo_tecnico_status;

-- Drop das tabelas de backup
DROP TABLE IF EXISTS seo_tecnico_categoria_backup;
DROP TABLE IF EXISTS seo_tecnico_item_backup;

-- Resetar as sequências
SELECT setval('seo_tecnico_categoria_id_seq', (SELECT MAX(id) FROM seo_tecnico_categoria));
SELECT setval('seo_tecnico_item_id_seq', (SELECT MAX(id) FROM seo_tecnico_item));
SELECT setval('seo_tecnico_status_id_seq', (SELECT MAX(id) FROM seo_tecnico_status));
