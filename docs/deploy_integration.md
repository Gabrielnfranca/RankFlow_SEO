# Integração GitHub e Render - RankFlow SEO

## Visão Geral
O RankFlow SEO utiliza integração contínua através do GitHub e Render. Quando fazemos alterações no código e enviamos para o GitHub, o Render automaticamente detecta essas mudanças e faz um novo deploy.

## Fluxo de Deploy
1. **Fazer alterações locais**
   ```bash
   # Editar arquivos necessários
   # Exemplo: schema.sql, models.py, etc.
   ```

2. **Adicionar alterações ao Git**
   ```bash
   git add .  # Para adicionar todas as alterações
   # OU
   git add arquivo1.py arquivo2.py  # Para arquivos específicos
   ```

3. **Fazer commit das alterações**
   ```bash
   git commit -m "Descrição clara das alterações"
   ```

4. **Enviar para o GitHub**
   ```bash
   git push
   ```

5. **Deploy Automático no Render**
   - O Render detecta automaticamente o push no GitHub
   - Inicia um novo deploy com as alterações
   - Executa as migrações do banco de dados
   - Executa scripts de inicialização (ex: init_seo_data.py)

## Arquivos Importantes
- `schema.sql`: Define a estrutura do banco de dados
- `init_seo_data.py`: Inicializa dados necessários no banco
- `requirements.txt`: Lista de dependências Python
- `Procfile`: Comandos para iniciar a aplicação no Render

## Exemplos de Uso

### Exemplo 1: Alterando Schema do Banco
```sql
-- Adicionar nova coluna
ALTER TABLE tabela ADD COLUMN nova_coluna TIPO;

-- No schema.sql
CREATE TABLE IF NOT EXISTS tabela (
    ...
    nova_coluna TIPO,
    ...
);
```

### Exemplo 2: Atualizando Dados
```python
# Em init_seo_data.py
def init_db():
    # Adicionar novos dados
    novo_item = Item(nome="Novo Item")
    db.session.add(novo_item)
    db.session.commit()
```

## Verificação do Deploy
1. Após o push, o Render inicia automaticamente um novo deploy
2. O progresso pode ser acompanhado no dashboard do Render
3. Logs de deploy estão disponíveis para debugging

## Troubleshooting
Se o deploy falhar:
1. Verificar logs no Render
2. Confirmar que todas as dependências estão no requirements.txt
3. Verificar se as variáveis de ambiente estão configuradas
4. Confirmar que o schema do banco está correto

## Boas Práticas
1. Sempre testar alterações localmente antes do push
2. Manter o requirements.txt atualizado
3. Usar mensagens de commit descritivas
4. Documentar alterações importantes
5. Verificar logs após o deploy
