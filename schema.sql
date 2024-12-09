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

-- Inserir tarefas padrão de SEO Técnico
INSERT INTO tarefa (cliente_id, titulo, descricao, prioridade, checklist) VALUES
(1, 'Análise de Velocidade do Site', 'Realizar análise completa da velocidade do site usando PageSpeed Insights', 'high', 
'[
    {"text": "Executar teste no PageSpeed Insights", "completed": false},
    {"text": "Otimizar imagens", "completed": false},
    {"text": "Minificar CSS/JS", "completed": false},
    {"text": "Configurar cache", "completed": false}
]'),
(1, 'Verificação Mobile-Friendly', 'Verificar se o site está totalmente adaptado para dispositivos móveis', 'high',
'[
    {"text": "Teste de responsividade", "completed": false},
    {"text": "Verificar viewport", "completed": false},
    {"text": "Testar formulários", "completed": false},
    {"text": "Checar fontes", "completed": false}
]'),
(1, 'Estrutura de URLs', 'Analisar e otimizar a estrutura de URLs do site', 'medium',
'[
    {"text": "Verificar URLs amigáveis", "completed": false},
    {"text": "Implementar breadcrumbs", "completed": false},
    {"text": "Verificar canonical tags", "completed": false},
    {"text": "Mapear redirecionamentos", "completed": false}
]'),
(1, 'Meta Tags', 'Otimizar meta tags de todas as páginas', 'high',
'[
    {"text": "Verificar title tags", "completed": false},
    {"text": "Otimizar meta descriptions", "completed": false},
    {"text": "Implementar Open Graph", "completed": false},
    {"text": "Verificar heading tags", "completed": false}
]'),
(1, 'Sitemap XML', 'Criar e otimizar o sitemap do site', 'medium',
'[
    {"text": "Gerar sitemap XML", "completed": false},
    {"text": "Validar estrutura", "completed": false},
    {"text": "Submeter ao Google", "completed": false},
    {"text": "Monitorar indexação", "completed": false}
]'),
(1, 'Robots.txt', 'Configurar e otimizar o arquivo robots.txt', 'medium',
'[
    {"text": "Criar/revisar robots.txt", "completed": false},
    {"text": "Definir diretrizes", "completed": false},
    {"text": "Testar configurações", "completed": false},
    {"text": "Verificar bloqueios", "completed": false}
]'),
(1, 'SSL/HTTPS', 'Verificar e otimizar a segurança do site', 'high',
'[
    {"text": "Verificar certificado SSL", "completed": false},
    {"text": "Configurar redirecionamentos", "completed": false},
    {"text": "Corrigir conteúdo misto", "completed": false},
    {"text": "Testar segurança", "completed": false}
]'),
(1, 'Links Quebrados', 'Identificar e corrigir links quebrados', 'medium',
'[
    {"text": "Fazer varredura completa", "completed": false},
    {"text": "Identificar 404s", "completed": false},
    {"text": "Corrigir redirecionamentos", "completed": false},
    {"text": "Verificar links externos", "completed": false}
]'),
(1, 'Schema Markup', 'Implementar marcações de dados estruturados', 'medium',
'[
    {"text": "Identificar tipos necessários", "completed": false},
    {"text": "Implementar markup", "completed": false},
    {"text": "Testar no validador", "completed": false},
    {"text": "Monitorar resultados", "completed": false}
]'),
(1, 'Canonical Tags', 'Implementar e otimizar canonical tags', 'medium',
'[
    {"text": "Identificar duplicações", "completed": false},
    {"text": "Implementar canonicals", "completed": false},
    {"text": "Verificar implementação", "completed": false},
    {"text": "Monitorar indexação", "completed": false}
]');
