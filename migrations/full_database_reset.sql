-- Desabilitar verificações de chave estrangeira
DO $$
BEGIN
    -- Excluir dados de tabelas relacionadas
    DELETE FROM seo_tecnico_status;
    DELETE FROM seo_tecnico_item;
    DELETE FROM seo_tecnico_categoria;
    DELETE FROM cliente;
    DELETE FROM usuario;

    -- Resetar sequências
    ALTER SEQUENCE usuario_id_seq RESTART WITH 1;
    ALTER SEQUENCE cliente_id_seq RESTART WITH 1;
    ALTER SEQUENCE seo_tecnico_status_id_seq RESTART WITH 1;
    ALTER SEQUENCE seo_tecnico_item_id_seq RESTART WITH 1;
    ALTER SEQUENCE seo_tecnico_categoria_id_seq RESTART WITH 1;

    -- Inserir usuário de teste
    INSERT INTO usuario (nome, email, senha) VALUES 
    ('Usuário Teste', 'teste@rankflow.com.br', 
     crypt('teste123', gen_salt('bf')));

    -- Inserir cliente de teste
    INSERT INTO cliente (nome, website, usuario_id) VALUES 
    ('Cliente Exemplo', 'https://webone.com.br', 
     (SELECT id FROM usuario WHERE email = 'teste@rankflow.com.br'));

    -- Inserir categorias e itens de SEO
    INSERT INTO seo_tecnico_categoria (nome, descricao, ordem) VALUES 
    ('Análise Técnica Inicial', 'Verificações técnicas básicas e essenciais', 1),
    ('Performance do Site', 'Análise e otimização de desempenho', 2);

    INSERT INTO seo_tecnico_item (categoria_id, nome, descricao, documentacao_url, ordem) VALUES 
    ((SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial'), 
     'Verificação de robots.txt', 
     'Verificar configuração e regras do robots.txt', 
     'https://developers.google.com/search/docs/advanced/robots/intro', 
     1),
    ((SELECT id FROM seo_tecnico_categoria WHERE nome = 'Análise Técnica Inicial'), 
     'Análise do sitemap.xml', 
     'Verificar estrutura e URLs no sitemap', 
     'https://developers.google.com/search/docs/advanced/sitemaps/overview', 
     2);

END $$;
