from app import app, db, SeoTecnicoCategoria, SeoTecnicoItem

def init_seo_tecnico_data():
    with app.app_context():
        # Verificar se já existem categorias
        categorias = SeoTecnicoCategoria.query.all()
        if not categorias:
            print("Inserindo categorias...")
            # Inserir categorias
            categorias_data = [
                {
                    'nome': 'Análise Técnica Inicial',
                    'descricao': 'Verificações técnicas básicas e essenciais',
                    'ordem': 1
                },
                {
                    'nome': 'Performance do Site',
                    'descricao': 'Análise e otimização de desempenho',
                    'ordem': 2
                },
                {
                    'nome': 'Estrutura do Site',
                    'descricao': 'Organização e arquitetura da informação',
                    'ordem': 3
                },
                {
                    'nome': 'Indexação e Rastreabilidade',
                    'descricao': 'Verificação de indexação e crawling',
                    'ordem': 4
                },
                {
                    'nome': 'Otimização On-page Base',
                    'descricao': 'Elementos básicos de otimização on-page',
                    'ordem': 5
                },
                {
                    'nome': 'Experiência do Usuário',
                    'descricao': 'Métricas e análise de experiência',
                    'ordem': 6
                },
                {
                    'nome': 'Segurança e Conformidade',
                    'descricao': 'Verificações de segurança e compliance',
                    'ordem': 7
                }
            ]

            for cat_data in categorias_data:
                categoria = SeoTecnicoCategoria(**cat_data)
                db.session.add(categoria)
            db.session.commit()

            # Recarregar categorias após inserção
            categorias = SeoTecnicoCategoria.query.all()

        # Verificar se já existem itens
        itens = SeoTecnicoItem.query.all()
        if not itens:
            print("Inserindo itens...")
            # Mapear categorias por nome para facilitar a inserção dos itens
            categorias_dict = {cat.nome: cat for cat in categorias}

            # Itens para cada categoria
            itens_data = {
                'Análise Técnica Inicial': [
                    {
                        'nome': 'Verificação de robots.txt',
                        'descricao': 'Verificar configuração e regras do robots.txt',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/robots/intro',
                        'ordem': 1
                    },
                    {
                        'nome': 'Análise do sitemap.xml',
                        'descricao': 'Verificar estrutura e URLs no sitemap',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/sitemaps/overview',
                        'ordem': 2
                    },
                    {
                        'nome': 'Verificação de SSL/HTTPS',
                        'descricao': 'Confirmar certificado SSL e redirecionamentos HTTPS',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/security/https',
                        'ordem': 3
                    }
                ],
                'Performance do Site': [
                    {
                        'nome': 'Core Web Vitals',
                        'descricao': 'Análise das principais métricas de performance',
                        'documentacao_url': 'https://web.dev/vitals/',
                        'ordem': 1
                    },
                    {
                        'nome': 'Otimização de imagens',
                        'descricao': 'Verificar compressão e formatos de imagem',
                        'documentacao_url': 'https://web.dev/optimize-images/',
                        'ordem': 2
                    },
                    {
                        'nome': 'Minificação de CSS/JS',
                        'descricao': 'Verificar minificação de recursos',
                        'documentacao_url': 'https://web.dev/minify-css/',
                        'ordem': 3
                    }
                ],
                'Estrutura do Site': [
                    {
                        'nome': 'Arquitetura da Informação',
                        'descricao': 'Análise da estrutura de navegação e hierarquia',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/site-structure',
                        'ordem': 1
                    },
                    {
                        'nome': 'URLs Amigáveis',
                        'descricao': 'Verificar estrutura e formatação das URLs',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/url-structure',
                        'ordem': 2
                    }
                ]
            }

            for categoria_nome, items in itens_data.items():
                categoria = categorias_dict.get(categoria_nome)
                if categoria:
                    for item_data in items:
                        item = SeoTecnicoItem(
                            categoria_id=categoria.id,
                            **item_data
                        )
                        db.session.add(item)
            
            db.session.commit()
            print("Dados iniciais do SEO Técnico inseridos com sucesso!")
        else:
            print("Dados já existem no banco de dados.")

if __name__ == '__main__':
    init_seo_tecnico_data()
