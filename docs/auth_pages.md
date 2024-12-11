# Documentação das Páginas de Autenticação

## Visão Geral
Este documento descreve a implementação e estrutura das páginas de login e cadastro do RankFlow SEO.

## Estrutura de Arquivos

```
templates/
├── login.html      # Template da página de login
└── cadastro.html   # Template da página de cadastro

static/
└── css/
    └── style.css   # Estilos incluindo autenticação
```

## Páginas de Autenticação

### Login (`login.html`)

#### Estrutura HTML
```html
<body class="auth-page">
    <div class="login-page">
        <div class="container">
            <div class="login-container">
                <div class="login-content">
                    <!-- Logo e Título -->
                    <div class="text-center">
                        <img src="logo.svg" class="login-logo">
                        <h1 class="login-title">RankFlow</h1>
                        <p class="login-subtitle">Monitore seus rankings com precisão</p>
                    </div>

                    <!-- Formulário de Login -->
                    <form method="POST" class="login-form">
                        <div class="mb-4">
                            <label>Email</label>
                            <input type="email" class="form-control">
                        </div>
                        <div class="mb-4">
                            <label>Senha</label>
                            <input type="password" class="form-control">
                        </div>
                        <button type="submit" class="btn btn-primary">Entrar</button>
                    </form>

                    <!-- Links -->
                    <div class="login-links">
                        <p>Não tem uma conta? <a href="/cadastro">Cadastre-se</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
```

### Cadastro (`cadastro.html`)

#### Estrutura HTML
```html
<body class="auth-page">
    <div class="login-page">
        <div class="container">
            <div class="login-container">
                <div class="login-content">
                    <!-- Logo e Título -->
                    <div class="text-center">
                        <img src="logo.svg" class="login-logo">
                        <h1 class="login-title">Cadastro</h1>
                        <p class="login-subtitle">Crie sua conta no RankFlow</p>
                    </div>

                    <!-- Formulário de Cadastro -->
                    <form method="POST" class="login-form">
                        <div class="mb-4">
                            <label>Nome</label>
                            <input type="text" class="form-control">
                        </div>
                        <div class="mb-4">
                            <label>Email</label>
                            <input type="email" class="form-control">
                        </div>
                        <div class="mb-4">
                            <label>Senha</label>
                            <input type="password" class="form-control">
                        </div>
                        <button type="submit" class="btn btn-primary">Criar Conta</button>
                    </form>

                    <!-- Links -->
                    <div class="login-links">
                        <p>Já tem uma conta? <a href="/login">Faça login</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
```

## Estilos CSS

### Classes Principais

```css
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2c5282 0%, #4a5568 100%);
    padding: 20px;
}

.login-container {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    padding: 2rem;
    margin: 0 auto;
}
```

### Responsividade

#### Mobile (< 576px)
```css
@media (max-width: 576px) {
    .login-container {
        padding: 1.5rem;
        margin: 1rem;
        max-width: 100%;
    }
    .login-form .form-control {
        font-size: 16px;
    }
}
```

#### Tablet (577px - 992px)
```css
@media (min-width: 577px) and (max-width: 992px) {
    .login-container {
        max-width: 80-90%;
        padding: 2-2.5rem;
    }
}
```

#### Desktop (> 993px)
```css
@media (min-width: 993px) {
    .login-container {
        max-width: 400px;
        padding: 2.5rem;
    }
}
```

## Características Responsivas

1. **Mobile-First Design**
   - Layout otimizado para dispositivos móveis
   - Fontes maiores para melhor legibilidade
   - Botões e inputs adaptados para touch

2. **Tablets**
   - Container com largura proporcional
   - Espaçamento equilibrado
   - Transições suaves

3. **Desktop**
   - Container com largura fixa
   - Animações sutis
   - Hover states

4. **Telas Grandes**
   - Container ligeiramente maior
   - Fontes proporcionalmente maiores
   - Mais espaço em branco

## Boas Práticas Implementadas

1. **Acessibilidade**
   - Labels semânticos
   - Contraste adequado
   - Feedback visual claro

2. **Performance**
   - CSS minificado
   - Imagens otimizadas
   - Carregamento eficiente

3. **Segurança**
   - CSRF Protection
   - Validação de formulários
   - Sanitização de inputs

4. **UX/UI**
   - Feedback de erros claro
   - Mensagens de sucesso
   - Navegação intuitiva

## Manutenção

Para manter a consistência ao fazer alterações:

1. Sempre teste em múltiplos dispositivos
2. Mantenha a hierarquia de classes CSS
3. Siga o padrão de nomenclatura existente
4. Atualize esta documentação quando necessário

## Dependências

- Bootstrap 5.3.0
- Inter Font (Google Fonts)
- Custom CSS (style.css)
