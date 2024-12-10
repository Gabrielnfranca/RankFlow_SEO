# Layouts e Padrões de Design - RankFlow SEO

Este documento serve como referência oficial para os layouts e padrões de design utilizados no RankFlow SEO.

## Página de Detalhes do Cliente

### Estrutura Principal
```html
<div class="client-header">
  <!-- Cabeçalho do Cliente -->
</div>
<div class="progress-cards">
  <!-- Cartões de Progresso -->
</div>
<div class="main-content">
  <!-- Conteúdo Principal -->
</div>
```

### 1. Cabeçalho do Cliente
- **Avatar**: Círculo com inicial do nome do cliente
- **Informações Básicas**:
  - Nome do cliente
  - Website
  - Data de cadastro
- **Ações**:
  - Botão de edição

### 2. Cartões de Progresso
Linha com 4 cartões mostrando métricas principais:
1. **Palavras-chave**
   - Contador
   - Barra de progresso
2. **Rankings Melhorados**
   - Contador
   - Barra de progresso verde
3. **Tarefas Concluídas**
   - Contador fracionado (x/y)
   - Barra de progresso amarela
4. **Relatórios Gerados**
   - Contador
   - Barra de progresso azul

### 3. Layout de Duas Colunas

#### Coluna Principal (8 colunas)
1. **Seção de Palavras-chave**
   - Cabeçalho com botão de adicionar
   - Lista de palavras-chave com:
     - Indicador de status (up/down)
     - Termo
     - Posição atual
     - Variação
2. **Gráfico de Rankings**
   - Título com ícone
   - Gráfico de linha temporal

#### Coluna Lateral (4 colunas)
1. **Atividades Recentes**
   - Cabeçalho com filtro
   - Timeline de atividades
2. **Ações Rápidas**
   - Botões de ação principais
   - Estilo consistente

### Elementos Visuais

#### Cores
- **Principal**: Azul (#007bff)
- **Sucesso**: Verde (#28a745)
- **Alerta**: Amarelo (#ffc107)
- **Info**: Azul claro (#17a2b8)

#### Ícones
- Utilizar Bootstrap Icons (bi-*)
- Manter consistência no tamanho
- Alinhar com texto quando usado em botões

#### Espaçamento
- Margem entre seções: 1.5rem (mb-4)
- Padding interno dos cards: 1rem
- Espaço entre elementos: 0.5rem

### Responsividade
- Layout flexível que se adapta a diferentes tamanhos de tela
- Cards empilham em telas menores
- Colunas principais tornam-se 100% em mobile

## Diretrizes Gerais

1. **Consistência**
   - Manter este layout como padrão para todas as páginas de detalhes
   - Não alterar a estrutura básica
   - Novas funcionalidades devem seguir o padrão estabelecido

2. **Modificações**
   - Apenas adicionar novos elementos
   - Manter a hierarquia visual
   - Preservar o esquema de cores
   - Seguir os padrões de espaçamento

3. **Performance**
   - Otimizar imagens
   - Minimizar requisições
   - Manter o código limpo e organizado

4. **Acessibilidade**
   - Manter contraste adequado
   - Incluir textos alternativos
   - Seguir hierarquia de headings

## Observações Importantes

- Este layout foi cuidadosamente projetado para oferecer a melhor experiência do usuário
- Qualquer alteração deve ser discutida e documentada
- Manter a documentação atualizada com mudanças aprovadas
