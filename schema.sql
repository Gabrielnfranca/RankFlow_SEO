-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS cliente (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    website TEXT,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id)
);

-- Tabela de Tarefas SEO
CREATE TABLE IF NOT EXISTS tarefa (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    status TEXT NOT NULL DEFAULT 'todo',
    prioridade TEXT NOT NULL DEFAULT 'medium',
    checklist TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES cliente (id)
);

-- Categorias de checklist SEO Técnico
CREATE TABLE IF NOT EXISTS seo_tecnico_categoria (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    ordem INTEGER NOT NULL
);

-- Itens do checklist
CREATE TABLE IF NOT EXISTS seo_tecnico_item (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    documentacao_url TEXT,
    ordem INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES seo_tecnico_categoria (id)
);

-- Status dos itens por cliente
CREATE TABLE IF NOT EXISTS seo_tecnico_status (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pendente', 'em_progresso', 'concluido')),
    prioridade TEXT NOT NULL CHECK (prioridade IN ('alta', 'media', 'baixa')),
    observacoes TEXT,
    data_verificacao TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES cliente (id),
    FOREIGN KEY (item_id) REFERENCES seo_tecnico_item (id)
);

-- Inserir categorias padrão somente se não existirem
INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Análise Técnica Inicial', 'Verificações técnicas básicas e essenciais', 1
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Performance do Site', 'Análise e otimização de desempenho', 2
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Performance do Site');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Estrutura do Site', 'Organização e arquitetura da informação', 3
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Estrutura do Site');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Indexação e Rastreabilidade', 'Verificação de indexação e crawling', 4
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Indexação e Rastreabilidade');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Otimização On-page Base', 'Elementos básicos de otimização on-page', 5
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Otimização On-page Base');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Experiência do Usuário', 'Métricas e análise de experiência', 6
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Experiência do Usuário');

INSERT INTO seo_tecnico_categoria (nome, descricao, ordem)
SELECT 'Segurança e Conformidade', 'Verificações de segurança e compliance', 7
WHERE NOT EXISTS (SELECT 1 FROM seo_tecnico_categoria WHERE nome = 'Segurança e Conformidade');

-- Inserir itens padrão somente se não existirem (para a categoria "Análise Técnica Inicial")
WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Verificação de robots.txt', 'Verificar configuração e regras do robots.txt', 'https://developers.google.com/search/docs/advanced/robots/intro', 1
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Análise Técnica Inicial' AND i.nome = 'Verificação de robots.txt'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Análise do sitemap.xml', 'Verificar estrutura e URLs no sitemap', 'https://developers.google.com/search/docs/advanced/sitemaps/overview', 2
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Análise Técnica Inicial' AND i.nome = 'Análise do sitemap.xml'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Verificação de SSL/HTTPS', 'Confirmar certificado SSL e redirecionamentos HTTPS', 'https://developers.google.com/search/docs/advanced/security/https', 3
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Análise Técnica Inicial' AND i.nome = 'Verificação de SSL/HTTPS'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Teste de responsividade mobile', 'Verificar adaptação para dispositivos móveis', 'https://developers.google.com/search/docs/advanced/mobile/mobile-sites', 4
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Análise Técnica Inicial' AND i.nome = 'Teste de responsividade mobile'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Verificação do .htaccess', 'Analisar configurações do servidor', 'https://httpd.apache.org/docs/current/howto/htaccess.html', 5
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Análise Técnica Inicial' AND i.nome = 'Verificação do .htaccess'
);

-- Inserir itens padrão somente se não existirem (para a categoria "Performance do Site")
WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Performance do Site')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Core Web Vitals', 'Análise das principais métricas de performance', 'https://web.dev/vitals/', 1
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Performance do Site' AND i.nome = 'Core Web Vitals'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Performance do Site')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Otimização de imagens', 'Verificar compressão e formatos de imagem', 'https://web.dev/optimize-images/', 2
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Performance do Site' AND i.nome = 'Otimização de imagens'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Performance do Site')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Minificação de CSS/JS', 'Verificar minificação de recursos', 'https://web.dev/minify-css/', 3
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Performance do Site' AND i.nome = 'Minificação de CSS/JS'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Performance do Site')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Cache do navegador', 'Configuração de cache e expiração', 'https://web.dev/http-cache/', 4
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Performance do Site' AND i.nome = 'Cache do navegador'
);

WITH cat AS (SELECT id FROM seo_tecnico_categoria WHERE nome = 'Performance do Site')
INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem)
SELECT cat.id, 'Compressão GZIP', 'Verificar compressão de recursos', 'https://web.dev/reduce-network-payloads-using-text-compression/', 5
FROM cat
WHERE NOT EXISTS (
    SELECT 1 FROM seo_tecnico_item i 
    JOIN seo_tecnico_categoria c ON i.categoria_id = c.id 
    WHERE c.nome = 'Performance do Site' AND i.nome = 'Compressão GZIP'
);
