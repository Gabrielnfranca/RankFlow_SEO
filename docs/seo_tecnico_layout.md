# Layout da Página SEO Técnico

## Visão Geral
A página SEO Técnico é uma interface completa para gerenciar e monitorar tarefas técnicas de SEO para cada cliente. O layout é organizado em seções distintas para facilitar a navegação e compreensão.

## Estrutura do Layout

### 1. Cabeçalho
- **Breadcrumb Navigation**
  - Painel > Clientes > [Nome do Cliente] > SEO Técnico
- **Informações do Cliente**
  - Avatar com a primeira letra do nome do cliente
  - Nome do cliente
  - Porcentagem de conclusão
  - Data da última atualização

### 2. Cards de Métricas (Dashboard)
Quatro cards no topo da página mostrando estatísticas importantes:

1. **Card Concluídos**
   - Ícone: check-circle (verde)
   - Número de tarefas concluídas
   - Cor: Verde (#28a745)

2. **Card Em Progresso**
   - Ícone: clock-history (amarelo)
   - Número de tarefas em andamento
   - Cor: Amarelo (#ffc107)

3. **Card Alta Prioridade**
   - Ícone: exclamation-triangle (vermelho)
   - Número de tarefas prioritárias
   - Cor: Vermelho (#dc3545)

4. **Card Total de Itens**
   - Ícone: list-check (azul)
   - Número total de itens
   - Cor: Azul (#0d6efd)

### 3. Conteúdo Principal (Layout de 2 Colunas)

#### Coluna Principal (8 colunas)
- Lista de categorias em cards expansíveis
- Cada categoria contém:
  - Título da categoria com ícone
  - Descrição da categoria
  - Lista de itens de verificação
  - Cada item possui:
    - Checkbox de status
    - Título do item
    - Descrição
    - Link para documentação
    - Seletor de prioridade (Alta/Média/Baixa)
    - Status visual (Concluído/Em Progresso/Pendente)

#### Coluna Lateral (4 colunas)
- Card fixo (sticky) com:
  - Barra de progresso geral
  - Resumo de status
  - Filtros rápidos
  - Ações em lote

### 4. Elementos Visuais

#### Cores
- **Status**
  - Concluído: Verde (#28a745)
  - Em Progresso: Amarelo (#ffc107)
  - Pendente: Cinza (#6c757d)

- **Prioridade**
  - Alta: Vermelho (#dc3545)
  - Média: Amarelo (#ffc107)
  - Baixa: Azul (#0d6efd)

#### Ícones
- Utiliza a biblioteca Bootstrap Icons (bi-*)
- Ícones consistentes para cada tipo de ação/status

### 5. Interatividade
- Checkboxes para atualizar status
- Dropdowns para selecionar prioridade
- Cards expansíveis/recolhíveis
- Atualização em tempo real dos contadores
- Filtros dinâmicos na coluna lateral

## Responsividade
- Layout responsivo que se adapta a diferentes tamanhos de tela
- Em telas menores:
  - Cards de métricas empilham em 2x2
  - Layout muda para uma coluna
  - Coluna lateral move-se para baixo
  - Menus colapsam em dropdown

## Tecnologias Utilizadas
- Bootstrap 5 para layout e componentes
- Bootstrap Icons para ícones
- JavaScript para interatividade
- Flask/Jinja2 para renderização do template

## Endpoints da API
- GET `/seo-tecnico/<cliente_id>`: Carrega a página
- POST `/api/seo-tecnico/atualizar-status`: Atualiza status dos itens
