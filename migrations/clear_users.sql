-- Limpar todas as tabelas relacionadas a usuários
DO $$
BEGIN
    -- Desabilitar verificações de chave estrangeira
    SET session_replication_role = 'replica';

    -- Limpar tabelas relacionadas a usuários
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

    -- Reabilitar verificações de chave estrangeira
    SET session_replication_role = 'origin';

    -- Inserir usuário de teste
    INSERT INTO usuario (nome, email, senha) VALUES 
    ('Usuário Teste', 'teste@rankflow.com.br', 
     crypt('teste123', gen_salt('bf')));

    -- Inserir cliente de teste
    INSERT INTO cliente (nome, website, usuario_id) VALUES 
    ('Cliente Exemplo', 'https://webone.com.br', 
     (SELECT id FROM usuario WHERE email = 'teste@rankflow.com.br'));
END $$;
