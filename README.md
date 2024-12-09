# Sistema SaaS

Um sistema SaaS leve desenvolvido com Flask, oferecendo funcionalidades de autenticação e dashboard.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone [seu-repositorio]
cd [seu-diretorio]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Sistema

1. Execute o aplicativo Flask:
```bash
python app.py
```

2. Acesse o sistema através do navegador:
```
http://localhost:5000
```

## Funcionalidades

- Sistema de Login/Cadastro
- Dashboard personalizado
- Interface responsiva
- Autenticação segura

## Tecnologias Utilizadas

- Flask (Backend)
- SQLAlchemy (ORM)
- Bootstrap 5 (Frontend)
- SQLite (Banco de dados)

## Estrutura do Projeto

```
.
├── app.py              # Arquivo principal da aplicação
├── requirements.txt    # Dependências do projeto
├── static/            # Arquivos estáticos (CSS, JS)
│   └── css/
│       └── style.css
└── templates/         # Templates HTML
    ├── login.html
    ├── cadastro.html
    └── dashboard.html
```
