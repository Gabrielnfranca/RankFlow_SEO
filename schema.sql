-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    website TEXT,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id)
);

-- Tabela de Tarefas SEO
CREATE TABLE IF NOT EXISTS tarefa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    ordem INTEGER NOT NULL
);

-- Itens do checklist
CREATE TABLE IF NOT EXISTS seo_tecnico_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    documentacao_url TEXT,
    ordem INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES seo_tecnico_categoria (id)
);

-- Status dos itens por cliente
CREATE TABLE IF NOT EXISTS seo_tecnico_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pendente', 'em_progresso', 'concluido')),
    prioridade TEXT NOT NULL CHECK (prioridade IN ('alta', 'media', 'baixa')),
    observacoes TEXT,
    data_verificacao DATETIME,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES cliente (id),
    FOREIGN KEY (item_id) REFERENCES seo_tecnico_item (id)
);

-- Inserir categorias padrão somente se não existirem
INSERT OR IGNORE INTO seo_tecnico_categoria (nome, descricao, ordem) VALUES
('Análise Técnica Inicial', 'Verificações técnicas básicas e essenciais', 1),
('Performance do Site', 'Análise e otimização de desempenho', 2),
('Estrutura do Site', 'Organização e arquitetura da informação', 3),
('Indexação e Rastreabilidade', 'Verificação de indexação e crawling', 4),
('Otimização On-page Base', 'Elementos básicos de otimização on-page', 5),
('Experiência do Usuário', 'Métricas e análise de experiência', 6),
('Segurança e Conformidade', 'Verificações de segurança e compliance', 7);

-- Inserir itens padrão somente se não existirem
INSERT OR IGNORE INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem) VALUES
-- Análise Técnica Inicial
(1, 'Verificação de robots.txt', 'Verificar configuração e regras do robots.txt', 'https://developers.google.com/search/docs/advanced/robots/intro', 1),
(1, 'Análise do sitemap.xml', 'Verificar estrutura e URLs no sitemap', 'https://developers.google.com/search/docs/advanced/sitemaps/overview', 2),
(1, 'Verificação de SSL/HTTPS', 'Confirmar certificado SSL e redirecionamentos HTTPS', 'https://developers.google.com/search/docs/advanced/security/https', 3),
(1, 'Teste de responsividade mobile', 'Verificar adaptação para dispositivos móveis', 'https://developers.google.com/search/docs/advanced/mobile/mobile-sites', 4),
(1, 'Verificação do .htaccess', 'Analisar configurações do servidor', 'https://httpd.apache.org/docs/current/howto/htaccess.html', 5),

-- Performance do Site
(2, 'Core Web Vitals', 'Análise dos principais métricas de performance', 'https://web.dev/vitals/', 1),
(2, 'Otimização de imagens', 'Verificar compressão e formatos de imagem', 'https://web.dev/optimize-images/', 2),
(2, 'Minificação de CSS/JS', 'Verificar minificação de recursos', 'https://web.dev/minify-css/', 3),
(2, 'Cache do navegador', 'Configuração de cache e expiração', 'https://web.dev/http-cache/', 4),
(2, 'Compressão GZIP', 'Verificar compressão de recursos', 'https://web.dev/reduce-network-payloads-using-text-compression/', 5);
