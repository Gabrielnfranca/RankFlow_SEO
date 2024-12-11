-- Adiciona a coluna documentacao_url se ela não existir
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'seo_tecnico_item'
        AND column_name = 'documentacao_url'
    ) THEN
        ALTER TABLE seo_tecnico_item
        ADD COLUMN documentacao_url VARCHAR(255);
    END IF;
END $$;
